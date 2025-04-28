from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import Length, Range
from shapely.geometry import shape
from geoalchemy2 import WKBElement

class GeoJSONField(fields.Field):
    """Custom field for handling GeoJSON serialization and validation."""

    def _serialize(self, value, attr, obj, **kwargs):
        value = obj.to_geojson() if value and isinstance(value, WKBElement) else value

        return value if value else None 

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            geom = shape(value)
            if not geom.is_valid or geom.geom_type != "Polygon":
                raise ValidationError("Invalid GeoJSON. Must be a valid Polygon.")
            return value
        except Exception:
            raise ValidationError("Invalid GeoJSON format.")


class ReforestedAreaSchema(Schema):
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(required=True)
    name = fields.String(required=True, validate=Length(min=3, max=100))
    description = fields.String(validate=Length(max=500))
    area_in_m2 = fields.Float(required=True, validate=Range(min=0.1))
    geom = GeoJSONField(required=True)  # Handle GeoJSON directly
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


reforested_area_schema = ReforestedAreaSchema()
reforested_areas_schema = ReforestedAreaSchema(many=True)
