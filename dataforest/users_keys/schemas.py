from marshmallow import Schema, fields, validates, validates_schema, ValidationError


class UsersKeysSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.String(required=True)
    encryption_key = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)


user_schema = UsersKeysSchema()
users_schema = UsersKeysSchema(many=True)