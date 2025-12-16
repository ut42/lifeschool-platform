from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.security import TokenData, verify_token
from ..domain.exam.repository import ExamRepository
from ..domain.registration.repository import RegistrationRepository
from ..domain.user.entity import User, UserRole
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


async def get_current_user_role(
    current_user: User = Depends(get_current_user),
) -> UserRole:
    """Dependency to get current user's role."""
    from ..domain.user.entity import UserRole
    return current_user.role


# Exam repository dependency
_exam_repository: Optional[ExamRepository] = None


def set_exam_repository(repository: ExamRepository) -> None:
    """Set the exam repository instance."""
    global _exam_repository
    _exam_repository = repository


def get_exam_repository() -> ExamRepository:
    """Get the exam repository instance."""
    if _exam_repository is None:
        raise RuntimeError("Exam repository not initialized")
    return _exam_repository


# Registration repository dependency
_registration_repository: Optional[RegistrationRepository] = None


def set_registration_repository(repository: RegistrationRepository) -> None:
    """Set the registration repository instance."""
    global _registration_repository
    _registration_repository = repository


def get_registration_repository() -> RegistrationRepository:
    """Get the registration repository instance."""
    if _registration_repository is None:
        raise RuntimeError("Registration repository not initialized")
    return _registration_repository

