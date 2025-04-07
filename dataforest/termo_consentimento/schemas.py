from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from marshmallow import Schema, fields, ValidationError, validate

class ConsentimentoRepository:
    def __init__(self, session: Session):
        self.session = session

class TermSchema(Schema):
    id = fields.UUID(dump_only=True)
    version = fields.Str(required=True, validate=validate.Length(max=50))
    title = fields.Str(required=True, validate=validate.Length(max=100))
    active = fields.Bool(missing=True)
    created_at = fields.DateTime(dump_only=True)
    sections = fields.Nested('TermSectionSchema', many=True, required=False)
class TermSectionSchema(Schema):
    id = fields.UUID(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=200))
    description = fields.Str(required=True)
    required = fields.Bool(required=True)
    term_id = fields.UUID(dump_only=True)  # Será preenchido automaticamente

class UserConsentSectionSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(required=True)
    section_id = fields.UUID(required=True)
    accepted = fields.Bool(required=True)
    accepted_at = fields.DateTime(dump_only=True)

term_schema = TermSchema()
term_section_schema = TermSectionSchema(many=True)
user_consent_schema = UserConsentSectionSchema(many=True)

