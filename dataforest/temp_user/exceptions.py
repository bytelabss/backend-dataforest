class UserServiceError(Exception):
    """Base exception for user service errors."""

    pass


class UserNotFoundError(UserServiceError):
    """Raised when a user is not found."""

    pass


class EmailAlreadyInUseError(UserServiceError):
    """Raised when the email is already associated with another user."""

    pass


class InvalidUserDataError(UserServiceError):
    """Raised when user data is invalid."""

    pass
