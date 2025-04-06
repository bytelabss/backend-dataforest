from flask import Blueprint, request, jsonify, g
from sqlalchemy.orm import Session
from marshmallow import Schema, fields, ValidationError, validate

class ConsentimentoRepository:
    def __init__(self, session: Session):
        self.session = session

    # def get_term_by_id(self, term_id):
    #     return self.session.get(Terms, term_id)

    # def insert_user_consent(self, user_consent: UserConsent):
    #     self.session.add(user_consent)
    #     self.session.commit()
    #     self.session.refresh(user_consent)
    #     return user_consent

    # def get_user_consent(self, user_id):
    #     return self.session.query(UserConsent).filter_by(user_id=user_id).first()

    # def delete_user_consent(self, user_consent):
    #     self.session.delete(user_consent)
    #     self.session.commit()

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

class UserConsentCreateSchema(Schema):
    user_id = fields.UUID(required=True)
    section_id = fields.UUID(required=True)
    accepted = fields.Bool(required=True)

term_schema = TermSchema()
term_section_schema = TermSectionSchema(many=True)