from functools import wraps

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import traceback

from ..database import Session
from ..auth.decorators import requires_auth
from ..users.models import UserRole
from .services import GeospatialDataService
from .schemas import polygon_data_schema, geospatial_data_schema
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
    session = Session()
    service = GeospatialDataService(session)
    data = request.get_json()
    try:
        validated_data = polygon_data_schema.load(data)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400
    traceback.print_exc()
    area = service.get_data_from_coordinates(**validated_data)
    print(area)
    print(type(area))
    
    return jsonify(geospatial_data_schema.dump(area)), 201

    