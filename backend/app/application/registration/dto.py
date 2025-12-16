from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ...domain.registration.entity import RegistrationStatus


class RegistrationResponse(BaseModel):
    """DTO for registration response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    exam_id: UUID
    status: RegistrationStatus
    created_at: datetime


class UserInfoDTO(BaseModel):
    """DTO for user information in admin queries."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    email: str
    mobile: Optional[str] = None


class RegistrationWithUserResponse(BaseModel):
    """DTO for registration with user details (admin view)."""
    model_config = ConfigDict(from_attributes=True)
    
    registration_id: UUID
    user: UserInfoDTO
    status: RegistrationStatus
    registered_at: datetime

