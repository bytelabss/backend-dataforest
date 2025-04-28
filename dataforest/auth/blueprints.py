from flask import request, Blueprint

from ..database import Session
from ..users.services import UserService
from .services import TokenService
from cryptography.fernet import Fernet
from ..database import SecondarySession
from ..users_keys.services import UsersKeysService

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/token", methods=["POST"])
def get_token():
    data = request.get_json()
    if "email" not in data or "password" not in data:
        return { "error": "Missing credentials" }, 400

    session = Session()
    user_service = UserService(session)
    token_service = TokenService(user_service)

    users = user_service.list_users()
    for user in users:
        if user.email == data["email"]:
            if user.check_password(data["password"]):
                return {
                    "token": token_service.generate_token(user),
                    "id": user.id
                }

    return { "error": "Invalid credentials" }, 400
