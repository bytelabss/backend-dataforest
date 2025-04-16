from typing import List, Optional
from uuid import UUID
from bson import ObjectId
from ..database import mongo_db
from .models import ReforestedArea

class ReforestedAreaRepository:
    def __init__(self):
        self.collection = mongo_db["reforested_areas"]

    def insert(self, area: ReforestedArea) -> ReforestedArea:
        data = area.to_dict()
        self.collection.insert_one(data)
        return area

    def get_by_id(self, area_id: UUID) -> Optional[ReforestedArea]:
        data = self.collection.find_one({"id": str(area_id)})
        return ReforestedArea.from_dict(data) if data else None

    def list_areas(self, offset=0, limit=10) -> List[ReforestedArea]:
        cursor = self.collection.find().skip(offset).limit(limit)
        return [ReforestedArea.from_dict(doc) for doc in cursor]

    def update(self, area: ReforestedArea) -> Optional[ReforestedArea]:
        result = self.collection.update_one({"id": str(area.id)}, {"$set": area.to_dict()})
        if result.modified_count:
            return area
        return None

    def delete(self, area_id: UUID) -> bool:
        result = self.collection.delete_one({"id": str(area_id)})
        return result.deleted_count == 1
