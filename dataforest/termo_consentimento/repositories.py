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

    def insert(self, term: Terms) -> Optional[Terms]:
        try:
            self.session.add(term)
            self.session.commit()
            self.session.refresh(term)
            return term
        except IntegrityError:
            self.session.rollback()
            return None
        
    def update_consent(self, user_id: UUID, section_id: UUID, accepted: bool) -> Optional[UserConsentSection]:
        try:
            consent = self.session.query(UserConsentSection).filter_by(
                user_id=user_id,
                section_id=section_id
            ).one_or_none()

            if consent:
                consent.accepted = accepted
            else:
                consent = UserConsentSection(
                    user_id=user_id,
                    section_id=section_id,
                    accepted=accepted
                )
                self.session.add(consent)

            self.session.commit()
            return consent

        except Exception as e:
            self.session.rollback()
            print(f"[ERRO AO ATUALIZAR CONSENTIMENTO] {e}")
            return None