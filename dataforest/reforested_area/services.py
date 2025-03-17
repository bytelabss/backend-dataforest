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

    def create_area(self, user_id: UUID, name: str, description: str, area: float, geom_geojson) -> ReforestedArea:
        geom = shape(geom_geojson)
        if geom.geom_type != "Polygon":
            raise ValueError("Geometry must be a valid Polygon.")

        new_area = ReforestedArea(user_id=user_id, name=name, description=description, area=area)
        new_area.set_geometry_from_geojson(geom_geojson)

        return self.repository.insert(new_area)

    def get_area_by_id(self, id: UUID) -> ReforestedArea:
        area = self.repository.get_by_id(id)
        if not area:
            raise ReforestedAreaNotFoundError("Reforested Area not found.")
        return area

    def list_areas(self, offset: int = 0, limit: int = 10) -> List[ReforestedArea]:
        return self.repository.list_areas(offset, limit)

    def update_area(self, id: UUID, name: str = None, description: str = None, area: float = None, geom_geojson=None) -> ReforestedArea:
        area_obj = self.get_area_by_id(id)

        if name:
            area_obj.name = name
        if description:
            area_obj.description = description
        if area:
            area_obj.area = area
        if geom_geojson:
            area_obj.set_geometry_from_geojson(geom_geojson)

        return self.repository.update(area_obj)

    def delete_area(self, id: UUID) -> None:
        area = self.get_area_by_id(id)
        self.repository.delete(area)
