import pytest
from uuid import uuid4

from app.application.user.dto import GoogleLoginRequest
from app.application.user.services import UserService
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


@pytest.mark.asyncio
async def test_user_is_created_on_first_google_login():
    """Test that a new user is created on first Google login."""
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    request = GoogleLoginRequest(email="test@example.com", name="Test User")
    user = await service.login_with_google(request)
    
    assert user is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.role == UserRole.USER
    assert user.mobile is None
    assert not user.is_profile_complete


@pytest.mark.asyncio
async def test_existing_user_is_returned_on_subsequent_login():
    """Test that existing user is returned on subsequent login."""
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # First login
    request1 = GoogleLoginRequest(email="test@example.com", name="Test User")
    user1 = await service.login_with_google(request1)
    user1_id = user1.id
    
    # Second login with same email
    request2 = GoogleLoginRequest(email="test@example.com", name="Updated Name")
    user2 = await service.login_with_google(request2)
    
    assert user2.id == user1_id
    assert user2.email == "test@example.com"
    # Name should remain as original (not updated)
    assert user2.name == "Test User"


@pytest.mark.asyncio
async def test_jwt_token_is_issued_after_login():
    """Test that JWT token is issued after login."""
    from app.core.security import create_access_token, verify_token
    
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    request = GoogleLoginRequest(email="test@example.com", name="Test User")
    user = await service.login_with_google(request)
    
    # Create token
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Verify token
    token_data = verify_token(token)
    assert token_data is not None
    assert token_data.user_id == user.id
    assert token_data.email == user.email
    assert token_data.role == user.role

