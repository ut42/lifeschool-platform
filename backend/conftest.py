"""Pytest configuration and fixtures."""
import pytest
from app.core.dependencies import set_user_repository
from app.domain.user.repository import UserRepository


@pytest.fixture(autouse=True)
def reset_repository():
    """Reset repository before each test."""
    # This ensures clean state for each test
    yield
    set_user_repository(None)

