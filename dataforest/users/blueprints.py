from functools import wraps

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..database import Session
from ..auth.decorators import requires_auth
from .models import UserRole
from .services import UserService
from .exceptions import UserNotFoundError, EmailAlreadyInUseError, InvalidUserDataError
from .schemas import user_schema, users_schema, pagination_schema

bp = Blueprint("users", __name__)


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({"error": e.messages}), 400
        except UserNotFoundError:
            return jsonify({"error": "User not found."}), 404
        except EmailAlreadyInUseError:
            return jsonify({"error": "Email is already in use."}), 409
        except InvalidUserDataError:
            return jsonify({"error": "Invalid input data."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return wrapper


@bp.route("/users", methods=["POST"])
@handle_exceptions
@requires_auth(required_role=UserRole.ADMINISTRATOR)
def create_user():
    session = Session()
    service = UserService(session)
    data = request.get_json()
    validated_data = user_schema.load(data)
    user = service.create_user(
        full_name=validated_data["full_name"],
        email=validated_data["email"],
        role=validated_data["role"],
        password=validated_data["password"],
    )
    return jsonify(user_schema.dump(user)), 201


@bp.route("/users/<uuid:user_id>", methods=["GET"])
@handle_exceptions
@requires_auth(required_role=UserRole.ADMINISTRATOR)
def get_user(user_id):
    session = Session()
    service = UserService(session)
    user = service.get_user_by_id(user_id)
    return jsonify(user_schema.dump(user)), 200


@bp.route("/users/<uuid:user_id>", methods=["PUT"])
@handle_exceptions
@requires_auth(required_role=UserRole.ADMINISTRATOR)
def update_user(user_id):
    session = Session()
    service = UserService(session)
    data = request.get_json()
    validated_data = user_schema.load(data, partial=True)
    user = service.update_user(
        user_id,
        validated_data.get("full_name"),
        validated_data.get("email"),
        validated_data.get("role"),
    )
    return jsonify(user_schema.dump(user)), 200


@bp.route("/users/<uuid:user_id>", methods=["DELETE"])
@handle_exceptions
@requires_auth(required_role=UserRole.ADMINISTRATOR)
def delete_user(user_id):
    session = Session()
    service = UserService(session)
    service.delete_user(user_id)
    return jsonify({"message": "User deleted successfully."}), 200


@bp.route("/users", methods=["GET"])
@handle_exceptions
@requires_auth(required_role=UserRole.ADMINISTRATOR)
def list_users():
    session = Session()
    service = UserService(session)
    validated_data = pagination_schema.load(request.args)
    users = service.list_users(validated_data["offset"], validated_data["limit"])
    return jsonify(users_schema.dump(users)), 200
