from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

from ...domain.registration.entity import RegistrationStatus


class EnrollmentResponse(BaseModel):
    """Response DTO for single enrollment."""
    registration_id: UUID
    status: RegistrationStatus = Field(..., description="New status of the registration")
    enrolled_at: datetime = Field(..., description="Timestamp when enrollment occurred")
    message: str = "Registration enrolled successfully."


class BulkEnrollmentRequest(BaseModel):
    """Request DTO for bulk enrollment."""
    registration_ids: List[UUID] = Field(..., description="List of registration IDs to enroll")


class FailedEnrollmentItem(BaseModel):
    """DTO for a failed enrollment in bulk operation."""
    registration_id: UUID
    reason: str = Field(..., description="Reason why enrollment failed")


class BulkEnrollmentResponse(BaseModel):
    """Response DTO for bulk enrollment."""
    success: List[UUID] = Field(..., description="List of successfully enrolled registration IDs")
    failed: List[FailedEnrollmentItem] = Field(default_factory=list, description="List of failed enrollments with reasons")

