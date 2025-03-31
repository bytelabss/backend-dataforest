from marshmallow import Schema, fields, validates, validates_schema, ValidationError

from .models import UserRole


class UserSchema(Schema):
    id = fields.String(dump_only=True)
    full_name = fields.String(required=True)
    email = fields.Email(required=True)
    role = fields.Enum(UserRole, by_value=True, required=True)
    password = fields.String(load_only=True, required=True)
    confirm_password = fields.String(load_only=True, required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if "password" in data and "confirm_password" in data:
            if data["password"] != data["confirm_password"]:
                raise ValidationError(
                    "Passwords do not match.", field_names=["confirm_password"]
                )


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class PaginationSchema(Schema):
    offset = fields.Integer(missing=0, validate=lambda x: x >= 0)
    limit = fields.Integer(missing=10, validate=lambda x: x > 0)


pagination_schema = PaginationSchema()
