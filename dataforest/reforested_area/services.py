import datetime
from .models import ReforestedArea
from .repositories import ReforestedAreaRepository
from .exceptions import ReforestedAreaNotFoundError

class ReforestedAreaService:
    def __init__(self):
        self.repository = ReforestedAreaRepository()

    def create_area(self, user_id, name, description, area_in_m2, geom):
        area = ReforestedArea(user_id, name, description, area_in_m2, geom)
        return self.repository.insert(area)

    def get_area_by_id(self, area_id):
        area = self.repository.get_by_id(area_id)
        if not area:
            raise ReforestedAreaNotFoundError()
        return area

    def list_areas(self, offset=0, limit=10):
        return self.repository.list_areas(offset, limit)

    def update_area(self, area: ReforestedArea, **validated_data):
        for attr, value in validated_data.items():
            setattr(area, attr, value)
        area.updated_at = datetime.datetime.utcnow()
        return self.repository.update(area)

    def delete_area(self, area_id):
        area = self.get_area_by_id(area_id)
        return self.repository.delete(area.id)
