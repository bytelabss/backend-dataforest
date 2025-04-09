from typing import List, Dict, Optional
import uuid
from sqlalchemy.orm import Session
from .models import Terms, TermSection, UserConsentSection
from .repositories import ConsentimentoRepository
from datetime import datetime

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

    def list_active_terms(self) -> List[Terms]:
        return self.repository.get_terms()
    
    def get_latest_active_term(self) -> Terms:
        return self.repository.get_latest_term()
    
    def register_consents(self, user_id: uuid, sections: list) -> dict:
        try:

            # Process each section
            for section in sections:
                # Create consent record
                consent = UserConsentSection(
                    user_id=user_id,
                    section_id=section['section_id'],
                    accepted=section['accepted'],
                    accepted_at=datetime.utcnow()
                                                  )
                self.repository.insert(consent)
            
            return {"success": True, "message": "Termos aceitos com sucesso"}
            
        except Exception as e:
            return {"success": False, "message": f"Erro ao registrar termos: {str(e)}"}
        
    def update_consents(self, user_id, sections: list) -> dict:
        try:
            for item in sections:
                section_id = item.get("section_id")
                accepted = item.get("accepted")

                self.repository.update_consent(section_id=section_id, user_id=user_id, accepted=accepted)
            return {"success": True, "message": "Termos atualizados com sucesso"}

        except Exception as e:
            self.session.rollback()
            return {"success": False, "message": "Erro ao atualizar termos"}
