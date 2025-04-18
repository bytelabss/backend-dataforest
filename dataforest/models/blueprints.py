from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from ..database import Session
import pandas as pd
import numpy as np
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
import joblib

bp = Blueprint("models", __name__)

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
        
        df_especies.to_csv("models/df_especies_clusters.csv", index=False)

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

        cluster = int(cluster) 
        response = {
            "cluster": cluster,
            "species": species,
            "mensagem": "Área classificada com sucesso!"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500