from datetime import datetime, timedelta, UTC

from sqlalchemy.orm import Session
import jwt

from ..config import Config
from ..users.services import UserService

TWO_WEEKS_IN_SECONDS = 1209600
ONE_YEAR_IN_SECONDS = 31536000

if Config.APP_ENV == "development":
    DEFAULT_EXPIRATION = ONE_YEAR_IN_SECONDS
else:
    DEFAULT_EXPIRATION = TWO_WEEKS_IN_SECONDS


class TokenService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def generate_token(self, user, expiration=DEFAULT_EXPIRATION):
        return jwt.encode(
            {
                "id": str(user.id),
                "email": user.email,
                "exp": datetime.now(UTC) + timedelta(seconds=expiration),
            },
            Config.SECRET_KEY,
            algorithm="HS256",
        )

    def verify_token(self, token):
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
            return self.user_service.get_user_by_email(data["email"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
