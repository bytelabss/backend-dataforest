class GeospatialDataServiceError(Exception):
    """Base exception for geospatial data service errors."""
    pass


class GeospatialDataNotFoundError(GeospatialDataServiceError):
    """Raised when a geospatial data is not found."""
    pass


class InvalidGeospatialDataDataError(GeospatialDataServiceError):
    """Raised when geospatial data is invalid."""
    pass
