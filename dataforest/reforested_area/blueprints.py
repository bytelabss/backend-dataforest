from functools import wraps

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from ..database import Session
from .services import ReforestedAreaService
from .schemas import reforested_area_schema, reforested_areas_schema
from .exceptions import ReforestedAreaNotFoundError

bp = Blueprint("reforested_areas", __name__)


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({"error": e.messages}), 400
        except ReforestedAreaNotFoundError:
            return jsonify({"error": "Reforested Area not found."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return wrapper


@bp.route("/reforested_areas", methods=["POST"])
@handle_exceptions
def create_area():
    service = ReforestedAreaService()
    data = request.get_json()
    print(data)
    validated_data = reforested_area_schema.load(data)
    area = service.create_area(**validated_data)
    return jsonify(reforested_area_schema.dump(area)), 201


@bp.route("/reforested_areas/<uuid:area_id>", methods=["PUT"])
@handle_exceptions
def update_area(area_id):
    service = ReforestedAreaService()
    data = request.get_json()
    validated_data = reforested_area_schema.load(data)
    
    # Tenta buscar a área com o ID fornecido
    area = service.get_area_by_id(area_id)
    
    # Atualiza a área com os dados validados
    updated_area = service.update_area(area, **validated_data)
    
    # Retorna a área atualizada
    return jsonify(reforested_area_schema.dump(updated_area)), 200


@bp.route("/reforested_areas/<uuid:area_id>", methods=["GET"])
@handle_exceptions
def get_area(area_id):
    service = ReforestedAreaService()
    area = service.get_area_by_id(area_id)
    return jsonify(reforested_area_schema.dump(area)), 200

@bp.route("/reforested_areas", methods=["GET"])
@handle_exceptions
def list_areas():
    offset = request.args.get("offset", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    service = ReforestedAreaService()
    areas = service.list_areas(offset=offset, limit=limit)

    return jsonify(reforested_areas_schema.dump(areas)), 200

@bp.route("/reforested_areas/<uuid:area_id>", methods=["DELETE"])
@handle_exceptions
def delete_area(area_id):
    service = ReforestedAreaService()
    service.delete_area(area_id)
    return jsonify({"message": "Reforested Area deleted successfully."}), 204