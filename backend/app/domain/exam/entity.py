from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class ExamStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"


class Exam:
    """Domain entity representing an exam."""
    
    def __init__(
        self,
        title: str,
        start_date: datetime,
        end_date: datetime,
        id: Optional[UUID] = None,
        description: Optional[str] = None,
        fee: Decimal = Decimal("0.00"),
        status: ExamStatus = ExamStatus.DRAFT,
        created_at: Optional[datetime] = None,
    ):
        if not title or not title.strip():
            raise ValueError("Title is required")
        
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date")
        
        if fee < 0:
            raise ValueError("fee must be >= 0")
        
        self.id = id or uuid4()
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.start_date = start_date
        self.end_date = end_date
        self.fee = fee
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def activate(self) -> None:
        """Activate the exam."""
        self.status = ExamStatus.ACTIVE
    
    def deactivate(self) -> None:
        """Deactivate the exam (set to draft)."""
        self.status = ExamStatus.DRAFT
    
    def __eq__(self, other):
        if not isinstance(other, Exam):
            return False
        return self.id == other.id
    
    def __repr__(self):
        return f"<Exam id={self.id} title={self.title} status={self.status}>"


