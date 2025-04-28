from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, user: User) -> Optional[User]:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            return None

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()

    def update(self, user: User) -> Optional[User]:
        try:
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            return None

    def delete(self, user: User) -> bool:
        try:
            self.session.delete(user)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False

    def list_users(self) -> List[User]:
        return self.session.query(User).all()
