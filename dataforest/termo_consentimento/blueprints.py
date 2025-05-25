from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from dataforest.auth.decorators import requires_auth
from dataforest.users.models import UserRole
from dataforest.users.services import UserService
from .services import TermService
from .schemas import term_schema, user_consent_schema
import uuid
from ..database import Session
from flask import g

bp = Blueprint('consent', __name__)

@bp.route('/terms', methods=['POST'])
@requires_auth(required_role=UserRole.ADMINISTRATOR)
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
@requires_auth(required_role=None)
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

@bp.route('/terms/aceite', methods=['POST'])
@requires_auth()
def accept_terms():
    session = Session()
    service = TermService(session)
    user_id = g.current_user.id
    
    try:
        data = request.get_json()
        
        sections = data.get('sections', [])

        result = service.register_consents(user_id, sections)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        session.rollback()
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
    finally:
        session.close()

@bp.route('/terms/atualizar', methods=['PUT'])
@requires_auth()
def update_terms():
    session = Session()
    service = TermService(session)
    user_id = g.current_user.id

    try:
        data = request.get_json()
        sections = data.get('sections', [])

        result = service.update_consents(user_id, sections)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    finally:
        session.close()

@bp.route('/terms/verifica', methods=['GET'])
@requires_auth()
def verifica_termo():
    session = Session()
    service = TermService(session)
    user_id = g.current_user.id

    has_user_accepted_latest_term = service.has_user_accepted_latest(user_id)
    if has_user_accepted_latest_term:
        return jsonify({
            "success": False,
            "message": "User has already accepted the latest term."
        }), 400
    else:
        return jsonify({
            "success": True,
            "message": "User has not accepted the latest term."
        }), 200