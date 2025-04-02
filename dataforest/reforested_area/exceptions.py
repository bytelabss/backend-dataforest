class ReforestedAreaServiceError(Exception):
    """Base exception for reforested area service errors."""
    pass


class ReforestedAreaNotFoundError(ReforestedAreaServiceError):
    """Raised when a reforested area is not found."""
    pass


class InvalidReforestedAreaDataError(ReforestedAreaServiceError):
    """Raised when reforested area data is invalid."""
    pass
