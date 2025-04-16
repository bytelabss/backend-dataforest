from shapely.geometry import shape, mapping
import uuid
import datetime

class ReforestedArea:
    def __init__(self, user_id, name, description, area_in_m2, geom, id=None, created_at=None, updated_at=None):
        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.name = name
        self.description = description
        self.area_in_m2 = area_in_m2
        self.geom = geom  # GeoJSON puro
        self.created_at = created_at or datetime.datetime.utcnow()
        self.updated_at = updated_at or datetime.datetime.utcnow()

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "description": self.description,
            "area_in_m2": self.area_in_m2,
            "geom": self.geom,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @staticmethod
    def from_dict(data):
        return ReforestedArea(
            id=uuid.UUID(data["id"]) if "id" in data else None,
            user_id=uuid.UUID(data["user_id"]),
            name=data["name"],
            description=data.get("description", ""),
            area_in_m2=data["area_in_m2"],
            geom=data["geom"],
            created_at=datetime.datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None
        )
