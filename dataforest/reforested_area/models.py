import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry, WKBElement
from shapely.geometry import shape

from ..database import Base


class ReforestedArea(Base):
    __tablename__ = "reforested_areas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str]
    description: Mapped[str]
    area_in_m2: Mapped[float]
    geom: Mapped[WKBElement] = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="reforested_areas")

    def set_geometry_from_geojson(self, geojson):
        self.geom = shape(geojson)  # Convert GeoJSON to Shapely and store as POLYGON

    def to_geojson(self):
        from geoalchemy2.shape import to_shape
        return to_shape(self.geom).__geo_interface__  # Convert to GeoJSON

    def __repr__(self) -> str:
        return f"ReforestedArea(id='{self.id}', name='{self.name}', area={self.area})"
