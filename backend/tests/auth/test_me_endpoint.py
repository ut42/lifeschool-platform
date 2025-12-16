import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import set_user_repository
from app.domain.user.entity import User, UserRole
from app.domain.user.repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._users = {}
        self._users_by_email = {}
    
    async def create(self, user: User) -> User:
        if user.email in self._users_by_email:
            from app.domain.user.exceptions import UserAlreadyExistsError
            raise UserAlreadyExistsError(f"User with email {user.email} already exists")
        
        self._users[str(user.id)] = user
        self._users_by_email[user.email] = user
        return user
    
    async def get_by_id(self, user_id) -> User:
        return self._users.get(str(user_id))
    
    async def get_by_email(self, email: str) -> User:
        return self._users_by_email.get(email.lower())
    
    async def update(self, user: User) -> User:
        if str(user.id) not in self._users:
            from app.domain.user.exceptions import UserNotFoundError
            raise UserNotFoundError(f"User with id {user.id} not found")
        
        self._users[str(user.id)] = user
        self._users_by_email[user.email] = user
        return user


@pytest.fixture
def client():
    """Create test client with in-memory repository."""
    repository = InMemoryUserRepository()
    set_user_repository(repository)
    
    return TestClient(app)


@pytest.fixture
def test_user(client):
    """Create a test user and return user data with token."""
    # Create user via login
    response = client.post(
        "/auth/google",
        json={"email": "test@example.com", "name": "Test User"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    return {
        "user": data["user"],
        "token": data["access_token"],
    }


def test_me_returns_authenticated_user_details(client, test_user):
    """Test that /me returns authenticated user details."""
    token = test_user["token"]
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "created_at" in data
    assert "is_profile_complete" in data


def test_unauthorized_request_to_me_fails(client):
    """Test that unauthorized request to /me fails."""
    # Request without token
    response = client.get("/auth/me")
    # FastAPI returns 401 or 403 for missing/invalid auth
    assert response.status_code in [401, 403, 422]
    
    # Request with invalid token
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

