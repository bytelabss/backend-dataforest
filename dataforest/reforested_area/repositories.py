from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from .models import ReforestedArea


class ReforestedAreaRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, area: ReforestedArea) -> Optional[ReforestedArea]:
        try:
            self.session.add(area)
            self.session.commit()
            self.session.refresh(area)
            return area
        except IntegrityError:
            self.session.rollback()
            return None

    def get_by_id(self, area_id: UUID) -> Optional[ReforestedArea]:
        return self.session.get(ReforestedArea, area_id)

    def list_areas(self, offset: int = 0, limit: int = 10) -> List[ReforestedArea]:
        return self.session.query(ReforestedArea).offset(offset).limit(limit).all()

    def update(self, area: ReforestedArea) -> Optional[ReforestedArea]:
        try:
            self.session.commit()
            self.session.refresh(area)
            return area
        except IntegrityError:
            self.session.rollback()
            return None

    def delete(self, area: ReforestedArea) -> bool:
        try:
            self.session.delete(area)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
