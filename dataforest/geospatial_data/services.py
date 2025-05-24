import numpy as np
from sqlalchemy.orm import Session
from shapely.geometry import Polygon

from .models import GeoSpatialData
from .repositories import GeospatialDataRepository
from .exceptions import GeospatialDataNotFoundError

class GeospatialDataService:
    def __init__(self, session: Session):
        self.repository = GeospatialDataRepository(session)

    def get_meaningful_raster_data(self, rasters: list) -> dict:
        """
        Processa uma lista de dados raster e calcula a média dos valores numéricos para cada chave.
        Se não houver valores numéricos, mantém o primeiro valor encontrado.
        """
        values = {}

        for geo in rasters:
            for date in geo.raster:
                for key, value in geo.raster[date].items():
                    if key not in values:
                        values[key] = {
                            'valor': [],
                            'medida': value.get('medida')
                        }
                    values[key]['valor'].append(value.get('valor'))

        for key, value in values.items():
            # Filtra apenas os valores numéricos
            numeric_values = [v for v in value['valor'] if isinstance(v, (int, float))]

            if numeric_values:
                # Calcula a média dos valores numéricos
                values[key]['valor'] = sum(numeric_values) / len(numeric_values)
            else:
                # Usa o primeiro valor original se não houver valor numérico
                values[key]['valor'] = value['valor'][0] if value['valor'] else None

        return values


    def get_data_from_coordinates(self, coordinates: list(list[float])) -> GeoSpatialData: 
        """
        Retorna os dados de todos os pontos que estão até 10km de distância do polígono. 
        """
        geospatial_data = []
        longitude = float(np.mean([coord[0] for coord in coordinates]))
        print("LONGITUDE: ", longitude)
        latitude = float(np.mean([coord[1] for coord in coordinates]))
        print("LATITUDE: ", latitude)
        distance_km = 10.0
        geospatial_data = self.repository.get_data_from_coordinates(
            longitude=longitude, 
            latitude=latitude, 
            distance_km=distance_km
        )
        if not geospatial_data:
            raise GeospatialDataNotFoundError
        
        # Calcula a média dos dados raster
        meaningful_raster_data = self.get_meaningful_raster_data(geospatial_data)

        return GeoSpatialData(
            id=str(coordinates),
            geom=Polygon(coordinates),
            raster=meaningful_raster_data
        )
    
    def get_batch_data_from_coordinates(self, coordinates: list(list[list[float]])) -> list[GeoSpatialData]:
        """
        Retorna os dados de todos os pontos que estão até 10km de distância dos polígonos.
        [{'coordinates': [[-63.920176435701194, -3.8830344419355285], [-63.86349738177961, -3.8920061007820004], [-63.859954940909496, -3.8446999190730504], [-63.90355421315689, -3.8376309530695285]]}, {'coordinates': [[-63.75441737887113, -3.8414389322234674], [-63.71699519827447, -3.8409251049756157], [-63.71939845757883, -3.8099236234598783], [-63.76557536849858, -3.8114651600574283]]}, {'coordinates': [[-64.11987972915185, -3.866479886721251], [-64.0525884686294, -3.8729881466179825], [-64.04469204520073, -3.8229760283130467], [-64.11781979260523, -3.817495070171685]]}, {'coordinates': [[-45.710204132340465, -23.084449989708247], [-45.622966391605054, -23.116537760113786], [-45.73363590977393, -23.18926533529807], [-45.752861984099525, -23.135368278070278], [-45.710204132340465, -23.084449989708247]]}, {'coordinates': [[-55.262949849664395, -14.005635003190413], [-49.59400452691279, -14.26132515947099], [-49.9895123317241, -18.22635440437193], [-55.96607471553939, -17.85028677405258], [-55.262949849664395, -14.005635003190413]]}, {'coordinates': [[-52.93384815047648, -22.793530585997082], [-48.58326229755212, -24.12382236124137], [-52.67017628060227, -31.575847268028713], [-57.02076213352664, -29.79977986435854], [-52.93384815047648, -22.793530585997082]]}, {'coordinates': [[-42.211191968820415, -3.9049512320161806], [-35.4875592870282, -6.268481910590175], [-39.398692023495556, -12.551483801159327], [-44.89185597920815, -8.925370201359216], [-42.211191968820415, -3.9049512320161806]]}, {'coordinates': [[-59.97037874673651, -0.781335643151248], [-46.81559700271271, -1.763496752117202], [-48.54081428061746, -8.63180596355428], [-62.82177952549576, -7.872988047748817], [-59.97037874673651, -0.781335643151248]]}]
        """

        geospatial_data = []
        
        for polygon in coordinates:
            if isinstance(polygon, dict) and 'coordinates' in polygon:
                poly = polygon['coordinates']
            else:
                raise ValueError("Invalid input format: each item in coordinates must be a dictionary with a 'coordinates' key.")
            
            if not all(
                isinstance(coord, (list, tuple)) and len(coord) == 2 and
                all(isinstance(x, (float, int)) for x in coord)
                for coord in poly
            ):
                raise ValueError(f"Coordenadas inválidas detectadas em: {poly}")
            longitudes = [float(coord[0]) for coord in poly]
            latitudes = [float(coord[1]) for coord in poly]
            longitude = float(np.mean(longitudes))
            latitude = float(np.mean(latitudes))
            distance_km = 10.0
            data = self.repository.get_data_from_coordinates(
                longitude=longitude, 
                latitude=latitude, 
                distance_km=distance_km
            )
            if not data:
                raise GeospatialDataNotFoundError
            
            # Calcula a média dos dados raster
            meaningful_raster_data = self.get_meaningful_raster_data(data)

            geospatial_data.append(GeoSpatialData(
                id=str(poly),
                geom=Polygon(poly),
                raster=meaningful_raster_data
            ))
            print("GEO: ", geospatial_data[-1])

        return geospatial_data
        