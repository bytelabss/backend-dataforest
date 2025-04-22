from flask import Blueprint, logging, request, jsonify
from marshmallow import ValidationError
from ..database import Session
import pandas as pd
import numpy as np
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import joblib
from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix



bp = Blueprint("models", __name__)

MODEL_PATH = 'models/modelo_estrategia.pkl'
SCALER_PATH = 'models/scaler_estrategia.pkl'
DATA_PATH = 'dataforest/data/areasxespecies.csv'

@bp.route('/treinar', methods=['POST'])
def treinar_kmeans():
    try:
        os.makedirs('models', exist_ok=True)

        df = pd.read_csv("dataforest/data/dados_amostragem.csv")

        X = df[["temperatura", "precipitacao", "altitude", "declividade", "exposicao",
                "distancia_vertical_drenagem", "densidade_drenagem", "cobertura_arborea"]]

        imputer = SimpleImputer(strategy="mean")
        X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imputed)

        inertia = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, random_state=42)
            kmeans.fit(X_scaled)
            inertia.append(kmeans.inertia_)

        kmeans = KMeans(n_clusters=4, random_state=42)
        kmeans.fit(X_scaled)

        df['cluster'] = kmeans.labels_

        centroids = kmeans.cluster_centers_

        joblib.dump(kmeans, 'models/modelo_kmeans.pkl')
        joblib.dump(scaler, 'models/scaler.pkl')
        joblib.dump(imputer, 'models/imputer.pkl')
        joblib.dump(centroids, 'models/centroids.pkl')

        print("✅ Modelos salvos com sucesso!")

        df_especies = pd.read_csv("dataforest/data/areasxespecies.csv")

        X = df_especies.drop("target", axis=1)

        X_imputado = imputer.transform(X) 

        X_normalizado = scaler.transform(X_imputado)  

        clusters = kmeans.predict(X_normalizado)

        df_especies["cluster"] = clusters

        encoder = LabelEncoder()
        df_especies["target_encoded"] = encoder.fit_transform(df_especies["target"])
        joblib.dump(encoder, 'models/encoder.pkl')

        cluster_species = {}
        for cluster in df_especies['cluster'].unique():
            species_in_cluster = df_especies[df_especies['cluster'] == cluster]
            most_common_species = species_in_cluster['target_encoded'].mode()[0]
            species_name = encoder.inverse_transform([most_common_species])[0]
            cluster_species[int(cluster)] = species_name

        print(cluster_species)
        
        df_especies.to_csv("models/df_especies_clusters.csv", index=False)

        print(df_especies.groupby('cluster')['target'].value_counts())


        return jsonify({
            "mensagem": "Modelo treinado com sucesso!",
            "clusters": cluster_species
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

@bp.route('/classificar', methods=['POST'])
def classificar_area():
    try:

        kmeans = joblib.load('models/modelo_kmeans.pkl')
        scaler = joblib.load('models/scaler.pkl')
        imputer = joblib.load('models/imputer.pkl')
        encoder = joblib.load('models/encoder.pkl')


        df_especies = pd.read_csv("models/df_especies_clusters.csv")
        
        # Aqui é importante adicionar a regra que classifica todas as áreas já cadastradas após implementação da Lari
        # A ideia é - a lari coloca no banco a area já com essas caracteristicas do modelo
        # E depois a gente roda o classificador para todas essas áreas
        # Retorna essa recomendação na página 

        nova_area = request.get_json()  

        nova_area_df = pd.DataFrame([nova_area])

        X_imputed = imputer.transform(nova_area_df)

        X_normalizado = scaler.transform(X_imputed)

        cluster = kmeans.predict(X_normalizado)[0]

        species = df_especies[df_especies['cluster'] == cluster]['target'].mode()[0]
        print(species)

        cluster = int(cluster) 
        response = {
            "cluster": cluster,
            "species": species,
            "mensagem": "Área classificada com sucesso!"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    


@bp.route('/prever-estrategia', methods=['POST'])
def prever_estrategia():
    try:

        nova_area = request.get_json()
        df_nova_area = pd.DataFrame([nova_area])

        scaler = joblib.load('models/scaler.pkl')
        modelo = joblib.load('models/modelo_estrategia.pkl')

        dados_normalizados = scaler.transform(df_nova_area)

        estrategia_prevista = modelo.predict(dados_normalizados)[0]
        # Aqui é importante adicionar a regra que classifica todas as áreas já cadastradas após implementação da Lari
        # A ideia é - a lari coloca no banco a area já com essas caracteristicas do modelo
        # E depois a gente roda o classificador para todas essas áreas
        # Retorna essa recomendação na página 

        estrategias_justificativas = {
            'mecanizacao': {'estrategia': 'mecanizacao', 
                            'justificativa': 'Este cluster apresenta alta precipitação e baixa declividade, ideal para o uso de maquinário na plantação. ',
                            'eucalipto': 'Ideal para áreas planas. Utilizar subsolagem, gradagem e plantio mecanizado em linha. Aplicar fosfato natural no sulco (50–100 kg/ha de P2O5) e NPK 6-30-6 no plantio. Em cobertura, usar 20-0-20 ou ureia + KCl.',
                            'pinha': 'Recomendado para grandes áreas. Fazer plantio em linha com densidade de 1.000 a 1.500 mudas/ha. Usar fosfato de rocha no sulco e NPK 4-14-8 no plantio. Posteriormente, aplicar 20-0-20 para estimular o crescimento.',
                            'adubacao': 'Aplicar adubação de base com NPK 4-14-8 no sulco e cobertura com 20-0-20 ou ureia + KCl.'
                            },
            'reflorestamento_natural': {'estrategia': 'reflorestamento_natural',
                                        'justificativa': 'Alta precipitação e boa cobertura arbórea indicam que o reflorestamento natural seria o mais adequado.',
                                        'eucalipto': 'O eucalipto precisa ser plantado manual ou mecanicamente. Aplicar matéria orgânica e NPK 6-30-6 caso opte por introduzir mudas.',
                                        'pinha': 'Pode ocorrer regeneração natural se houver árvores-matrizes. Ideal para áreas já reflorestadas. Adubar com matéria orgânica e aplicar reforço com NPK leve em áreas de regeneração assistida.',
                                        'adubacao': 'Utilizar adubação leve com NPK 4-14-8 ou 6-30-6, dependendo da análise de solo. Aplicar matéria orgânica para melhorar a fertilidade do solo.'
                                        },
            'intensiva_irrigacao': {'estrategia': 'intensiva_irrigacao', 'justificativa': 'Temperatura mais baixa e precipitação moderada indicam a necessidade de irrigação intensiva para garantir o crescimento.',
                                    'eucalipto': 'Usar irrigação por gotejamento nas fases iniciais. Plantar em linhas com espaçamento controlado. Aplicar NPK 6-30-6 e usar fertirrigação com ureia e potássio conforme análise de solo.',
                                    'pinha': 'Ideal em viveiros ou no primeiro ano em regiões secas. Pode usar irrigação por aspersão leve. Aplicar fertilizante de liberação lenta e usar composto orgânico com nitrogênio e potássio.',
                                    'adubacao': 'Fertilizantes de liberação lenta são recomendados. Aplicar NPK 4-14-8 ou 6-30-6 conforme análise de solo. Usar composto orgânico para melhorar a fertilidade do solo.'
                                        },
            'fertilizacao_alta': {'estrategia': 'fertilizacao_alta', 
                                  'justificativa': 'Clima quente e precipitação moderada exigem fertilização alta para fornecer os nutrientes necessários ao solo.',
                                  'eucalipto': 'Realizar plantio com análise de solo detalhada. Reforçar fertilização durante crescimento. Usar NPK 6-30-6 no plantio e depois aplicar ureia, KCl e torta de mamona como adubo de cobertura.',
                                  'pinha': 'Plantio com adubação de base rica em fósforo e potássio. Aplicar fertilização ao redor das mudas. Utilizar húmus de minhoca, esterco curtido e fertilizantes com nitrogênio e potássio após 6 meses.',
                                  'adubacao': 'Fazer análise de solo e aplicar NPK 4-14-8 ou 6-30-6 conforme necessidade. Usar adubação de cobertura com ureia, KCl e torta de mamona. Aplicar húmus de minhoca e esterco curtido para melhorar a fertilidade.'
                                  }
        }

        estrategia_com_justificativa = estrategias_justificativas[estrategia_prevista]

        return jsonify({
            'estrategia_prevista': estrategia_com_justificativa['estrategia'],
            'justificativa': estrategia_com_justificativa['justificativa'],
            'eucalipto': estrategia_com_justificativa['eucalipto'],
            'pinha': estrategia_com_justificativa['pinha'],
            'adubacao': estrategia_com_justificativa['adubacao']
        })

    except Exception as e:
        return jsonify({'erro': str(e)}), 500



@bp.route('/treinar-estrategias', methods=['POST'])
def treinar_modelo():
    try:
        df = pd.read_csv(DATA_PATH)
        df = df.dropna()
        df_features = df.drop(columns=['target'], errors='ignore')
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df_features)

        inertia = []
        K = range(1, 10)
        for k in K:
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(scaled_data)
            inertia.append(kmeans.inertia_)
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        df_features['estrategia_cluster'] = kmeans.fit_predict(scaled_data)

        cluster_profiles = df_features.groupby('estrategia_cluster').mean()
        cluster_profiles.to_csv('cluster_profiles.csv')

        cluster_to_label = {
            0: 'mecanizacao',
            1: 'reflorestamento_natural',
            2: 'intensiva_irrigacao',
            3: 'fertilizacao_alta'
}
        df_features['estrategia'] = df_features['estrategia_cluster'].map(cluster_to_label)


        df_features.to_csv('estrategias.csv', index=False)
        data = pd.read_csv('estrategias.csv')

        data = data.drop(columns=['estrategia_cluster'], errors='ignore')

        X = data.drop(columns=['estrategia'])
        y = data['estrategia']


        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        joblib.dump(clf, 'models/modelo_estrategia.pkl')
        joblib.dump(scaler, 'models/scaler.pkl')


        return jsonify({'mensagem': 'Modelo treinado e salvo com sucesso!'})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
