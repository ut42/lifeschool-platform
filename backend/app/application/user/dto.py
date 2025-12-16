from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ...domain.user.entity import UserRole


class GoogleLoginRequest(BaseModel):
    """DTO for Google login request."""
    email: EmailStr
    name: str = Field(..., min_length=1)


class MobileUpdateRequest(BaseModel):
    """DTO for mobile number update request."""
    mobile: str = Field(..., min_length=1)  # Domain layer validates exact length


class UserResponse(BaseModel):
    """DTO for user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: str
    name: str
    mobile: Optional[str]
    role: UserRole
    created_at: datetime
    is_profile_complete: bool


class AuthResponse(BaseModel):
    """DTO for authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

