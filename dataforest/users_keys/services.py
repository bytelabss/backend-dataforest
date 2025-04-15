from uuid import UUID
from typing import List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from .models import UsersKeys
from .repositories import UserKeysRepository
from .exceptions import (
    UserNotFoundError,
    EmailAlreadyInUseError,
    InvalidUserDataError,
)


class UsersKeysService:
    def __init__(self, session: Session):
        self.repository = UserKeysRepository(session)

    def create_user(self, user_id: str, encryption_key: str) -> UsersKeys:
        userKeys = UsersKeys(user_id=user_id, encryption_key=encryption_key)
        return self.repository.insert(userKeys)
