import json
from uuid import UUID
from typing import List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.orm import Session

from .models import User, UserRole
from .repositories import UserRepository
from .exceptions import (
    UserNotFoundError,
    EmailAlreadyInUseError,
    InvalidUserDataError,
)
from cryptography.fernet import Fernet
from ..database import SecondarySession
from ..users_keys.services import UsersKeysService
from ..redis_client import redis_client


class UserService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

    def create_user(self, full_name: str, email: str, role: UserRole, password: str) -> User:
        session2 = SecondarySession()
        service2 = UsersKeysService(session2)

        if not full_name or not email or not password:
            raise InvalidUserDataError

        if self.repository.get_by_email(email):
            raise EmailAlreadyInUseError
        
        encryption_key = Fernet.generate_key()
        fernet = Fernet(encryption_key)
    
        encrypted_email = fernet.encrypt(email.encode("utf-8")).decode()
        encrypted_full_name = fernet.encrypt(full_name.encode("utf-8")).decode()

        user = User(full_name=encrypted_full_name, email=encrypted_email, role=role)
        user.set_password(password)

        user = self.repository.insert(user)

        encryption_data = {
            "user_id": user.id,
            "encryption_key": encryption_key.decode() 
        }

        service2.create_user(
            user_id=encryption_data["user_id"],
            encryption_key=encryption_data["encryption_key"]
        )

        user_data = {
            'id' : str(user.id),
            'full_name': full_name,
            'email': email,
        }

        users = redis_client.get(f"users")

        if users:
            users = json.loads(users)  
        else:
            users = [] 

        users.append(user_data)

        redis_client.setex(f"users", 3600, json.dumps(users))

        return user

    def get_user_by_id(self, id: UUID) -> User:
        user = self.repository.get_by_id(id)
        
        usersRedi = redis_client.get(f"users")

        if usersRedi:
            users = json.loads(usersRedi)  
        else:
            users = [] 

        for user_json in users:
            if str(user.id) == str(user_json["id"]):
                user.email = user_json["email"]
                user.full_name = user_json["full_name"]
                break

        if not user:
            raise UserNotFoundError
        return user

    def get_user_by_email(self, email: str) -> User:
        usuarios = self.list_users()
        usuario = None
        for user in usuarios:
            if user.email == email:
                usuario = user
        if not usuario:
            raise UserNotFoundError
        return usuario

    def update_user_postgres(
            self, 
            id: UUID, 
            full_name: str = None, 
            email: str = None, 
            role: UserRole = None,
            password: str = None
            ) -> User:
        secondary_session = SecondarySession()
        service2 = UsersKeysService(secondary_session)
        user_key = service2.get_user_by_user_id(id)

        if not user_key:
            raise UserNotFoundError

        fernet = Fernet(user_key.encryption_key)

        user = self.get_user_by_id(id)

        if email:
            
            if user.email != email:
                    if self.repository.get_by_email(email):
                        raise EmailAlreadyInUseError
                    user.email = email

        if full_name:
            
            if user.full_name != full_name:
                user.full_name = full_name
        if role:
            user.role = role
        if password:
            user.set_password(password)

        user.email = fernet.encrypt(user.email.encode("utf-8")).decode()
        user.full_name = fernet.encrypt(user.full_name.encode("utf-8")).decode()

        return self.repository.update(user)

    def update_user_redis(self, user: UUID) -> User:
        secondary_session = SecondarySession()
        service2 = UsersKeysService(secondary_session)
        user_key = service2.get_user_by_user_id(user.id)

        if not user_key:
            raise UserNotFoundError

        fernet = Fernet(user_key.encryption_key)

        found = False
        user_data = {
            'id' : str(user.id),
            'full_name': fernet.decrypt(user.full_name.encode("utf-8")).decode(),
            'email': fernet.decrypt(user.email.encode("utf-8")).decode(),
        }

        users = redis_client.get(f"users")

        if users:
            users = json.loads(users)  
        else:
            users = [] 

        for i, user_json in enumerate(users):
            if str(user.id) == str(user_json["id"]):
                users[i] = user_data
                found = True
                break

        if not found:
            users.append(user_data)

        redis_client.setex(f"users", 3600, json.dumps(users))

    def update_user(
            self, 
            id: UUID, 
            full_name: str = None, 
            email: str = None, 
            role: UserRole = None,
            password: str = None
            ) -> User:
        user = self.update_user_postgres(id, full_name, email, role, password)
        self.update_user_redis(user)
        if user:
            user.email = email
            user.full_name = full_name

        return user

    def delete_user(self, id: UUID) -> None:
        userDelete = self.repository.get_by_id(id)

        if not userDelete:
            raise UserNotFoundError

        session2 = SecondarySession()
        service2 = UsersKeysService(session2)

        usuarios = self.list_users()

        usersRedis = [] 

        for usuario in usuarios:

            if(userDelete.id == usuario.id):
                continue

            user_data = {
                'id' : str(usuario.id),
                'full_name': usuario.full_name,
                'email': usuario.email,
            }

            usersRedis.append(user_data)

        redis_client.setex(f"users", 3600, json.dumps(usersRedis))

        service2.delete_user(id)

    def list_users_criptografados(self) -> List[User]:
       
        usuarios = self.repository.list_users()

        return usuarios

    def list_users(self) -> List[User]:

        user_list: List[User] = []

        users_redis = redis_client.get(f"users")

        if users_redis:
            users = json.loads(users_redis)  
        else:
            users = [] 

        usuarios = self.repository.list_users()

        for user in usuarios:
            for user_json in users:
                if str(user.id) == str(user_json["id"]):
                    user.email = user_json["email"]
                    user.full_name = user_json["full_name"]
                    user_list.append(user)
                    break

        return user_list


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
