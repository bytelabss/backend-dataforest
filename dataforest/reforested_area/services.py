from uuid import UUID
from typing import List

from sqlalchemy.orm import Session
from shapely.geometry import shape

from .models import ReforestedArea
from .repositories import ReforestedAreaRepository
from .exceptions import ReforestedAreaNotFoundError


class ReforestedAreaService:
    def __init__(self, session: Session):
        self.repository = ReforestedAreaRepository(session)

    def create_area(self, user_id: UUID, name: str, description: str, area_in_m2: float, geom : dict) -> ReforestedArea:
        geom2 = shape(geom)
        if geom2.geom_type != "Polygon":
            raise ValueError("Geometry must be a valid Polygon.")
        
    # Converte o Polygon para WKT e adiciona o SRID (4326)
        geom_wkt = geom2.wkt  # Converte o Polygon para WKT
        geom_ewkt = f"SRID=4326;{geom_wkt}"  # Adiciona o SRID para EWKT

        new_area = ReforestedArea(user_id=user_id, name=name, description=description, area_in_m2=area_in_m2, geom=geom_ewkt)

        return self.repository.insert(new_area)

    def get_area_by_id(self, id: UUID) -> ReforestedArea:
        area = self.repository.get_by_id(id)
        if not area:
            raise ReforestedAreaNotFoundError("Reforested Area not found.")
        return area

    def list_areas(self, offset: int = 0, limit: int = 10) -> List[ReforestedArea]:
        return self.repository.list_areas(offset, limit)

    def update_area(self, area: ReforestedArea, **validated_data) -> ReforestedArea:

        if 'name' in validated_data:
            area.name = validated_data['name']
        if 'description' in validated_data:
            area.description = validated_data['description']
        if 'area_in_m2' in validated_data:
            area.area_in_m2 = validated_data['area_in_m2']
        if 'geom' in validated_data:
            geom2 = shape(validated_data['geom'])
            geom_wkt = geom2.wkt  # Converte o Polygon para WKT
            geom_ewkt = f"SRID=4326;{geom_wkt}"  # Adiciona o SRID para EWKT
            area.set_geometry_from_geojson(geom_ewkt)

        return self.repository.update(area)

    def delete_area(self, id: UUID) -> None:
        area = self.get_area_by_id(id)
        self.repository.delete(area)
