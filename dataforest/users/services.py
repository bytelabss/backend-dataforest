from uuid import UUID
from typing import List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from .models import User
from .repositories import UserRepository
from .exceptions import (
    UserNotFoundError,
    EmailAlreadyInUseError,
    InvalidUserDataError,
)


class UserService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

    def create_user(self, full_name: str, email: str, password: str) -> User:
        if not full_name or not email or not password:
            raise InvalidUserDataError

        if self.repository.get_by_email(email):
            raise EmailAlreadyInUseError

        user = User(full_name=full_name, email=email)
        user.set_password(password)
        return self.repository.insert(user)

    def get_user_by_id(self, id: UUID) -> User:
        user = self.repository.get_by_id(id)
        if not user:
            raise UserNotFoundError
        return user

    def get_user_by_email(self, email: str) -> User:
        user = self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError
        return user

    def update_user(self, id: UUID, full_name: str = None, email: str = None) -> User:
        user = self.get_user_by_id(id)

        if email and user.email != email and self.repository.get_by_email(email):
            raise EmailAlreadyInUseError

        if full_name:
            user.full_name = full_name
        if email:
            user.email = email

        return self.repository.update(user)

    def delete_user(self, id: UUID) -> None:
        user = self.repository.get_by_id(id)
        if not user:
            raise UserNotFoundError
        self.repository.delete(user)

    def list_users(self, offset: int = 0, limit: int = 10) -> List[User]:
        if offset < 0 or limit <= 0:
            raise InvalidUserDataError

        return self.repository.list_users(offset, limit)


class PasswordService:
    _hasher = PasswordHasher()

    @classmethod
    def hash_password(cls, plaintext_password: str) -> str:
        return cls._hasher.hash(plaintext_password)

    @classmethod
    def verify_password(cls, hashed_password: str, plaintext_password: str) -> bool:
        try:
            return cls._hasher.verify(hashed_password, plaintext_password)
        except VerifyMismatchError:
            return False
