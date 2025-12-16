from typing import Optional
from uuid import UUID

from ...domain.user.entity import User, UserRole
from ...domain.user.exceptions import UserNotFoundError
from ...domain.user.repository import UserRepository
from .dto import GoogleLoginRequest, MobileUpdateRequest, UserResponse


class UserService:
    """Application service for user operations."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def login_with_google(self, request: GoogleLoginRequest) -> User:
        """Handle Google login - create user if not exists, return existing if exists."""
        existing_user = await self.user_repository.get_by_email(request.email)
        
        if existing_user:
            return existing_user
        
        # Create new user
        new_user = User(
            email=request.email,
            name=request.name,
            role=UserRole.USER,
        )
        
        return await self.user_repository.create(new_user)
    
    async def update_mobile(self, user_id: UUID, request: MobileUpdateRequest) -> User:
        """Update user's mobile number."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        user.update_mobile(request.mobile)
        return await self.user_repository.update(user)
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        return user
    
    @staticmethod
    def to_dto(user: User) -> UserResponse:
        """Convert domain entity to DTO."""
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            mobile=user.mobile,
            role=user.role,
            created_at=user.created_at,
            is_profile_complete=user.is_profile_complete,
        )

