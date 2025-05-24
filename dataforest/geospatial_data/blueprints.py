from functools import wraps

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import traceback

from ..database import Session
from ..auth.decorators import requires_auth
from ..users.models import UserRole
from .services import GeospatialDataService
from .schemas import polygon_data_schema, geospatial_data_schema, geospatial_data_list_schema, polygon_data_list_schema
from .exceptions import GeospatialDataNotFoundError

bp = Blueprint("geospatial_data", __name__)

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return jsonify({"error": e.messages}), 400
        except GeospatialDataNotFoundError:
            return jsonify({"error": "Geospatial Data not found."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    return wrapper

@bp.route("/geospatial_data", methods=["POST"])
@handle_exceptions
@requires_auth(required_role=(UserRole.ADMINISTRATOR))
def get_data_from_coordinates():
    data = request.get_json()
    try:
        validated_data = polygon_data_schema.load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    traceback.print_exc()
    with Session() as session:
        service = GeospatialDataService(session)
        area = service.get_data_from_coordinates(**validated_data)

    return jsonify(geospatial_data_schema.dump(area)), 200

@bp.route("/geospatial_data/batch", methods=["POST"])
@handle_exceptions
@requires_auth(required_role=(UserRole.ADMINISTRATOR))
def get_batch_data_from_coordinates():
    data = request.get_json()

    try:
        if not isinstance(data, list):
            return jsonify({"error": "Input data must be a list of coordinate objects."}), 400

        validated_data = []
        for item in data:
            if not isinstance(item, dict) or "coordinates" not in item:
                return jsonify({"error": "Each item must be a dictionary containing 'coordinates'."}), 400
            validated_data.append(polygon_data_schema.load(item))
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    traceback.print_exc()
    print("Validated Data:", validated_data)
    with Session() as session:
        service = GeospatialDataService(session)
        areas = service.get_batch_data_from_coordinates(validated_data)

    areas = [geospatial_data_schema.dump(area) for area in areas]

    return jsonify(areas), 200
