"""Domain exceptions for exam module."""


class ExamNotFoundError(Exception):
    """Raised when an exam is not found."""
    pass


class ExamAlreadyExistsError(Exception):
    """Raised when attempting to create an exam that already exists."""
    pass


class InvalidExamDataError(Exception):
    """Raised when exam data validation fails."""
    pass


