from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

from .models import Terms, TermSection, UserConsentSection

class ConsentimentoRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_terms(self) -> List[Terms]:
        return self.session.query(Terms).filter(Terms.active.is_(True)).all()

    def get_latest_term(self) -> Terms:
        return self.session.query(Terms)\
            .filter_by(active=True)\
            .order_by(Terms.version.desc())\
            .first()

    def insert(self, area: Terms) -> Optional[Terms]:
        try:
            self.session.add(area)
            self.session.commit()
            self.session.refresh(area)
            return area
        except IntegrityError:
            self.session.rollback()
            return None
            
    # def insert_user_consent(self, user_consent: UserConsent):
    #     self.session.add(user_consent)
    #     self.session.commit()
    #     self.session.refresh(user_consent)
    #     return user_consent

    # def insert_user_consent_sections(self, section_consents: list[UserConsentSection]):
    #     self.session.add_all(section_consents)
    #     self.session.commit()

    # def get_user_consent(self, user_id):
    #     return self.session.query(UserConsent).filter_by(user_id=user_id).first()

    # def delete_user_consent(self, user_consent):
    #     self.session.delete(user_consent)
    #     self.session.commit()
