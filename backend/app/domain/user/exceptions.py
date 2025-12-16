"""Domain exceptions for user module."""


class UserNotFoundError(Exception):
    """Raised when a user is not found."""
    pass


class UserAlreadyExistsError(Exception):
    """Raised when attempting to create a user that already exists."""
    pass


class InvalidMobileNumberError(Exception):
    """Raised when mobile number validation fails."""
    pass

