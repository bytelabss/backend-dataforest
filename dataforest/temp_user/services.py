from uuid import UUID
from typing import List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from .models import TempUser
from .repositories import TempUserRepository
from .exceptions import (
    UserNotFoundError,
    EmailAlreadyInUseError,
    InvalidUserDataError,
)


class TempUsersService:
    def __init__(self, session: Session):
        self.repository = TempUserRepository(session)

    def create_user(self, id: str, full_name: str, email: str) -> TempUser:
        userKeys = TempUser(id=id, full_name=full_name,email=email)
        return self.repository.insert(userKeys)
    
    def get_user_by_user_id(self, user_id: UUID) -> TempUser:
        userKey = self.repository.get_by_user_id(user_id)
        if not userKey:
            raise UserNotFoundError
        return userKey
    
    def delete_user(self, id: UUID) -> None:
        user = self.repository.get_by_user_id(id)

        if not user:
            raise UserNotFoundError
        self.repository.delete(user)

    def list_users(self) -> List[TempUser]:

        usuarios = self.repository.list_users()

        return usuarios