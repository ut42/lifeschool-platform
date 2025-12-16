from fastapi import APIRouter, Depends, HTTPException, status

from ..application.user.dto import (
    AuthResponse,
    GoogleLoginRequest,
    MobileUpdateRequest,
    UserResponse,
)
from ..application.user.services import UserService
from ..core.dependencies import get_current_user, get_user_repository
from ..core.security import create_access_token
from ..domain.user.entity import User
from ..domain.user.repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Dependency to get user service."""
    from ..application.user.services import UserService
    return UserService(user_repository)


@router.post("/google", response_model=AuthResponse)
async def google_login(
    request: GoogleLoginRequest,
    user_service: UserService = Depends(get_user_service),
):
    """Handle Google login (mocked)."""
    user = await user_service.login_with_google(request)
    
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )
    
    return AuthResponse(
        access_token=access_token,
        user=user_service.to_dto(user),
    )


@router.post("/mobile", response_model=UserResponse)
async def update_mobile(
    request: MobileUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update user's mobile number."""
    try:
        user = await user_service.update_mobile(current_user.id, request)
        return user_service.to_dto(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get current user's profile."""
    return user_service.to_dto(current_user)

