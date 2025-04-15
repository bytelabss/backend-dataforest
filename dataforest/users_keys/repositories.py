from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import UsersKeys


class UserKeysRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert(self, user: UsersKeys) -> Optional[UsersKeys]:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except IntegrityError:
            self.session.rollback()
            return None
