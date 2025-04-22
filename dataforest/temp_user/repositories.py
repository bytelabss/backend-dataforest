from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import TempUser


class TempUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, user: TempUser) -> Optional[TempUser]:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            return None
        
    def get_by_user_id(self, user_id: UUID) -> Optional[TempUser]:
        return self.session.query(TempUser).filter_by(id=str(user_id)).first()
    
    def delete(self, user: TempUser) -> bool:
        try:
            self.session.delete(user)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
    
    def list_users(self) -> Optional[TempUser]:
        return self.session.query(TempUser)
