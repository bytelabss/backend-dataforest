from marshmallow import Schema, fields, validates, validates_schema, ValidationError


class TempUserSchema(Schema):
    id = fields.String(dump_only=True)
    full_name = fields.String(required=True)
    email = fields.String(required=True)


temp_user_schema = TempUserSchema()
temp_user_schema = TempUserSchema(many=True)