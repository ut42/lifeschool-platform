from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ...domain.registration.entity import RegistrationStatus


class PaymentInitiationResponse(BaseModel):
    """DTO for payment initiation response."""
    model_config = ConfigDict(from_attributes=True)
    
    registration_id: UUID
    status: RegistrationStatus
    payment_id: UUID
    message: str


class PaymentConfirmationResponse(BaseModel):
    """DTO for payment confirmation response."""
    model_config = ConfigDict(from_attributes=True)
    
    registration_id: UUID
    status: RegistrationStatus
    payment_id: UUID
    confirmed_at: datetime
    message: str

