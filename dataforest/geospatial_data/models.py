import uuid

from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from sqlalchemy import Column

from ..database import Base

class GeoSpatialData(Base):
    __tablename__ = "dados_geoespaciais"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    raster: Mapped[dict] = mapped_column(JSON, nullable=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)

    def __repr__(self):
        return f"<GeoSpatialData(id={self.id}, raster={self.raster}, geom={self.geom})>"
