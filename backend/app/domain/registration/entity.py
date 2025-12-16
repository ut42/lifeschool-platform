from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class RegistrationStatus(str, Enum):
    REGISTERED = "REGISTERED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAID = "PAID"
    ENROLLED = "ENROLLED"


class ExamRegistration:
    """Domain entity representing an exam registration."""
    
    def __init__(
        self,
        user_id: UUID,
        exam_id: UUID,
        id: Optional[UUID] = None,
        status: RegistrationStatus = RegistrationStatus.REGISTERED,
        created_at: Optional[datetime] = None,
    ):
        if not user_id:
            raise ValueError("user_id is required")
        if not exam_id:
            raise ValueError("exam_id is required")
        
        self.id = id or uuid4()
        self.user_id = user_id
        self.exam_id = exam_id
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def __eq__(self, other):
        if not isinstance(other, ExamRegistration):
            return False
        return self.id == other.id
    
    def __repr__(self):
        return f"<ExamRegistration id={self.id} user_id={self.user_id} exam_id={self.exam_id}>"

