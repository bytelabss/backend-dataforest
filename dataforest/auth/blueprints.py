from flask import request, Blueprint

from ..database import Session
from ..users.services import UserService
from .services import TokenService

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/token", methods=["POST"])
def get_token():
    data = request.get_json()
    if "email" not in data or "password" not in data:
        return { "error": "Missing credentials" }, 400

    session = Session()
    user_service = UserService(session)
    token_service = TokenService(user_service)

    user = user_service.get_user_by_email(data["email"])
    if user and user.check_password(data["password"]):
        return { "token": token_service.generate_token(user) }

    return { "error": "Invalid credentials" }, 400
