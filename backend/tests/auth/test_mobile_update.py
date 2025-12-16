import pytest

from app.application.user.dto import MobileUpdateRequest
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
async def test_mobile_number_must_be_exactly_10_digits():
    """Test that mobile number must be exactly 10 digits."""
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user
    user = User(email="test@example.com", name="Test User")
    await repository.create(user)
    
    # Test with 9 digits - should fail
    with pytest.raises(ValueError, match="exactly 10 digits"):
        request = MobileUpdateRequest(mobile="123456789")
        await service.update_mobile(user.id, request)
    
    # Test with 11 digits - should fail
    with pytest.raises(ValueError, match="exactly 10 digits"):
        request = MobileUpdateRequest(mobile="12345678901")
        await service.update_mobile(user.id, request)
    
    # Test with non-digits - should fail
    with pytest.raises(ValueError, match="only digits"):
        request = MobileUpdateRequest(mobile="123456789a")
        await service.update_mobile(user.id, request)
    
    # Test with exactly 10 digits - should succeed
    request = MobileUpdateRequest(mobile="1234567890")
    updated_user = await service.update_mobile(user.id, request)
    
    assert updated_user.mobile == "1234567890"
    assert updated_user.is_profile_complete


@pytest.mark.asyncio
async def test_user_cannot_be_marked_profile_complete_without_mobile():
    """Test that user cannot be marked profile-complete without mobile."""
    repository = InMemoryUserRepository()
    service = UserService(repository)
    
    # Create a user without mobile
    user = User(email="test@example.com", name="Test User")
    await repository.create(user)
    
    assert not user.is_profile_complete
    assert user.mobile is None
    
    # Update with mobile
    request = MobileUpdateRequest(mobile="1234567890")
    updated_user = await service.update_mobile(user.id, request)
    
    assert updated_user.is_profile_complete
    assert updated_user.mobile == "1234567890"

