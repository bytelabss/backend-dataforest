from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from .services import TermService
from .schemas import term_schema
import uuid
from ..database import Session

bp = Blueprint('consent', __name__)

@bp.route('/terms', methods=['POST'])
def create_term():
    session = Session()
    service = TermService(session)
    try:
        data = request.get_json()
        validated_data = term_schema.load(data)
        term = service.create_term(**validated_data)
        
        return jsonify(term_schema.dump(term)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@bp.route("/terms", methods=["GET"])
def list_terms():
    session = Session()
    service = TermService(session)
    terms = service.list_active_terms()
    return jsonify(term_schema.dump(terms, many=True)), 200

@bp.route('/terms/ativo', methods=['GET'])
def get_latest_active_term():
    session = Session()
    service = TermService(session)
    try:
        latest_term = service.get_latest_active_term()
        return jsonify(term_schema.dump(latest_term)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
