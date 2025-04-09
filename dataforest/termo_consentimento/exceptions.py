class ConsentimentoServiceError(Exception):
    """Base exception for consent service errors."""
    pass

class TermNotFoundError(ConsentimentoServiceError):
    """Raised when a requested term is not found."""
    pass

class UserConsentNotFoundError(ConsentimentoServiceError):
    """Raised when no consent record is found for a user."""
    pass