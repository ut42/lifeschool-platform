"""Domain exceptions for Content entity."""


class ContentNotFoundError(Exception):
    """Raised when content is not found."""
    pass


class InvalidContentTypeError(Exception):
    """Raised when content type is invalid."""
    pass

