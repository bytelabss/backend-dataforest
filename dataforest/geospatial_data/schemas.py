from marshmallow import Schema, fields, validate, validates, ValidationError
from shapely.geometry import Polygon


class GeospatialDataSchema(Schema):
    id = fields.String(dump_only=True)
    geom = fields.String(required=True)
    raster = fields.Dict(required=True)


class PolygonDataSchema(Schema):
    coordinates = fields.List(
        fields.List(
            fields.Float(), 
            required=True,
        ), 
        required=True
    )

    @validates("coordinates")
    def validate_coordinates(self, value):
        if len(value) < 4:
            raise ValidationError("Coordinates must have at least 4 points.")
        for point in value:
            if len(point) != 2:
                raise ValidationError("Each coordinate must have exactly 2 values (latitude and longitude).")


# Schemas for single objects
geospatial_data_schema = GeospatialDataSchema()
polygon_data_schema = PolygonDataSchema()

# Schemas for lists of objects
geospatial_data_list_schema = fields.List(fields.Nested(GeospatialDataSchema))
polygon_data_list_schema = fields.List(fields.Nested(PolygonDataSchema))
