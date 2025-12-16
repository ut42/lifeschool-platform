from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from ...domain.user.entity import UserRole


class UserDocument(BaseModel):
    """MongoDB document model for User."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "mobile": "1234567890",
                "role": "USER",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    )
    
    id: UUID
    email: EmailStr
    name: str
    mobile: Optional[str] = None
    role: UserRole = UserRole.USER
    created_at: datetime

