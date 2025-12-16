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

