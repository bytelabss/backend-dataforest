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


@bp.route("/portabilidade/consentimento", methods=["POST"])
def consentimento():
    data = request.get_json()

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Authorization token required"}, 401

    token = auth_header.split(" ")[1]
    session = Session()
    user_service = UserService(session)
    token_service = TokenService(user_service)

    user = token_service.verify_token_criptografado(token)

    if not user:
        return {"error": "User not found"}, 404

    if not data or not data.get("accept"):
        return {"error": "Consentimento necessário."}, 400

    if data.get("accept") is not True:
        return {"error": "Portabilidade não autorizada."}, 403

    user.data_portability = True
    session.commit()

    return {"message": "Consentimento registrado com sucesso."}, 200

@bp.route("/portabilidade", methods=["GET"])
def portability():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Authorization token required"}, 401

    token = auth_header.split(" ")[1]
    session = Session()
    user_service = UserService(session)
    token_service = TokenService(user_service)

    user_id = token_service.verify_token(token)
    user = user_service.get_user_by_id(user_id.id)

    if not user:
        return {"error": "User not found"}, 404

    # Verificar se o usuário deu consentimento
    if not getattr(user, "data_portability", False):
        return {"error": "Consentimento não encontrado para portabilidade."}, 403

    personal_data = {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "created_at": str(user.created_at),
    }

    return personal_data, 200