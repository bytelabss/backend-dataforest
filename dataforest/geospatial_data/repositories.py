from geoalchemy2.functions import ST_DWithin, ST_SetSRID, ST_MakePoint
from sqlalchemy.orm import Session
from .models import GeoSpatialData

class GeospatialDataRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_data_from_coordinates(self, longitude: float, latitude: float, distance_km: float = 1.0) -> list[GeoSpatialData]:
        """
        SELECT *
        FROM public.dados_geoespaciais
        WHERE ST_DWithin(
        geom,
        ST_SetSRID(ST_MakePoint(-45.70857606, -23.10341063), 4326),
        0.01  -- distância em graus (~1km)
        )
        LIMIT 100;
        """
        distance_degrees = distance_km / 111.0  # Aproximando 1 grau ≈ 111 km
        point = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)

        data = (
            self.session.query(GeoSpatialData)
            .filter(ST_DWithin(GeoSpatialData.geom, point, distance_degrees))
            .limit(100)
            .all()
        )

        # print("RETORNO: ", data)

        return data
