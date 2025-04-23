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
        Pega uma lista de rasters de coordenadas e calcula a média dos valores.
        {  
            '2025-04-08': {
                'exposicao': {'valor': 321.8937072753906, 'medida': 'graus'}, 
                'declividade': {'valor': 11.35536003112793, 'medida': 'graus'}, 
                'temperatura': {'valor': 18.2, 'medida': '°C'}, 
                'precipitacao': {'valor': 1337.0, 'medida': 'mm'}, 
                'cobertura_arborea': {'valor': 22.0, 'medida': 'percentual'}, 
                'densidade_drenagem': {'valor': 11.166500091552734, 'medida': 'km/km²'}, 
                'distancia_vertical_drenagem': {'valor': 126.30000305175781, 'medida': 'metros'}
            }, 
            '2025-04-10': {
                'altitude': {'valor': 714.8800048828125, 'medida': 'metros'}
            }
        }
        """
        values = {}
        for geo in rasters:
            for date in geo.raster:
                for key, value in geo.raster[date].items():
                    if key not in values.keys():
                        values[key] = {
                            'valor': [],
                            'medida': value['medida']
                        }
                    values[key]['valor'].append(value['valor'])

        for key, value in values.items():
            string = False
            for v in value['valor']:
                if isinstance(v, str):
                    string = True
                    break
            if not string:
                values[key]['valor'] = sum(value['valor']) / len(value['valor'])
            else:
                values[key]['valor'] = value['valor'][0]


        return values

    def get_data_from_coordinates(self, coordinates: list(list[float])) -> GeoSpatialData: 
        """
        Retorna os dados de todos os pontos que estão até 10km de distância do polígono. 
        """
        geospatial_data = []
        for coord in coordinates:
            print(coord)
            if len(coord) != 2:
                raise ValueError("Cada coordenada deve ter exatamente 2 valores (longitude e latitude).")
            
            data = self.repository.get_data_from_coordinates(
                longitude=coord[0],
                latitude=coord[1],
                distance_km=10.0
            )
            geospatial_data.extend(data)
        if not geospatial_data:
            raise GeospatialDataNotFoundError
        mean = self.get_meaningful_raster_data(geospatial_data)

        return GeoSpatialData(
            id=str(coordinates),
            geom=Polygon(coordinates),
            raster=mean
        )
        