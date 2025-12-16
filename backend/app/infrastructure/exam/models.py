from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ...domain.exam.entity import ExamStatus


class ExamDocument(BaseModel):
    """MongoDB document model for Exam."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Mathematics Exam",
                "description": "Final mathematics examination",
                "start_date": "2024-06-01T09:00:00",
                "end_date": "2024-06-01T12:00:00",
                "fee": "500.00",
                "status": "ACTIVE",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    )
    
    id: UUID
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    fee: Decimal
    status: ExamStatus
    created_at: datetime


