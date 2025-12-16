from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.security import TokenData, verify_token
from ..domain.user.entity import User
from ..domain.user.exceptions import UserNotFoundError
from ..domain.user.repository import UserRepository

security = HTTPBearer()

# This will be set by the application startup
_user_repository: Optional[UserRepository] = None


def set_user_repository(repository: UserRepository) -> None:
    """Set the user repository instance."""
    global _user_repository
    _user_repository = repository


def get_user_repository() -> UserRepository:
    """Get the user repository instance."""
    if _user_repository is None:
        raise RuntimeError("User repository not initialized")
    return _user_repository


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    """Dependency to get current authenticated user."""
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_repository.get_by_id(token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

