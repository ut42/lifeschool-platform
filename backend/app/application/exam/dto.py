from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ...domain.exam.entity import ExamStatus


class ExamCreateRequest(BaseModel):
    """DTO for exam creation request."""
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    status: ExamStatus = ExamStatus.DRAFT


class ExamUpdateRequest(BaseModel):
    """DTO for exam update request."""
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    fee: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ExamStatus] = None


class ExamResponse(BaseModel):
    """DTO for exam response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    fee: Decimal
    status: ExamStatus
    created_at: datetime

