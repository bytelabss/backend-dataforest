from typing import List, Dict, Optional
import uuid
from sqlalchemy.orm import Session
from .models import Terms, TermSection, UserConsentSection
from .repositories import ConsentimentoRepository

class TermService:
    def __init__(self, session: Session):
        self.repository = ConsentimentoRepository(session)


    def create_term(self, version: str, title: str, sections: List[Dict], active: bool = True) -> Dict:
        """Cria um novo termo com seções"""
        try:
            # Cria o termo principal
            new_term = Terms(
                version=version,
                title=title,
                active=active
            )

            # Adiciona seções
            created_sections = []
            for section in sections:
                new_section = TermSection(
                    term_id=new_term.id,
                    title=section['title'],
                    description=section['description'],
                    required=section.get('required', False)
                )
                self.repository.insert(new_section)
                created_sections.append(new_section)
                
                new_term.sections = created_sections
            return self.repository.insert(new_term)

        except Exception as e:
            raise ValueError(f"Erro ao criar termo: {str(e)}")

    # def get_user_consents(self, user_id: str) -> Dict:
    #     """Obtém todos os consentimentos de um usuário"""
    #     try:
    #         user_uuid = uuid.UUID(user_id)
    #     except ValueError:
    #         raise ValueError("ID de usuário inválido")

    #     consents = self.db.query(UserConsentSection)\
    #                     .filter_by(user_id=user_uuid)\
    #                     .all()
        
    #     required_sections = self.db.query(TermSection)\
    #                             .filter_by(required=True)\
    #                             .all()

    #     return {
    #         'consents': consents,
    #         'required_sections': required_sections
    #     }

    # def register_consent(self, user_id: str, section_id: str, accepted: bool) -> UserConsentSection:
    #     """Registra o aceite/rejeição de uma seção"""
    #     try:
    #         user_uuid = uuid.UUID(user_id)
    #         section_uuid = uuid.UUID(section_id)
    #     except ValueError:
    #         raise ValueError("ID inválido")

    #     # Verifica se a seção existe
    #     section = self.db.get(TermSection, section_uuid)
    #     if not section:
    #         raise ValueError("Seção não encontrada")

    #     # Registra o consentimento
    #     consent = UserConsentSection(
    #         user_id=user_uuid,
    #         section_id=section_uuid,
    #         accepted=accepted
    #     )
        
    #     try:
    #         self.db.add(consent)
    #         self.db.commit()
    #         return consent
    #     except Exception as e:
    #         self.db.rollback()
    #         raise ValueError(f"Erro ao registrar consentimento: {str(e)}")

    def list_active_terms(self) -> List[Terms]:
        return self.repository.get_terms()
    
    def get_latest_active_term(self) -> Terms:
        return self.repository.get_latest_term()

