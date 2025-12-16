"""Domain exceptions for registration module."""


class RegistrationNotFoundError(Exception):
    """Raised when a registration is not found."""
    pass


class DuplicateRegistrationError(Exception):
    """Raised when attempting to register for the same exam twice."""
    pass


class InvalidRegistrationError(Exception):
    """Raised when registration data validation fails."""
    pass

