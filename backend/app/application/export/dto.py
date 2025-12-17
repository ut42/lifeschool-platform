from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CSVRegistrationRow(BaseModel):
    """DTO for a single CSV row representing a registration."""
    registration_id: UUID
    user_id: UUID
    user_name: str
    email: str
    mobile: Optional[str]
    registration_status: str
    enrollment_status: str
    payment_status: str
    paid_at: Optional[datetime]
    enrolled_at: Optional[datetime]
    registered_at: datetime

