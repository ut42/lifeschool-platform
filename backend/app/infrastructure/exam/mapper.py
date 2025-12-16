from ...domain.exam.entity import Exam
from .models import ExamDocument


class ExamMapper:
    """Mapper between domain entity and MongoDB document."""
    
    @staticmethod
    def to_document(exam: Exam) -> dict:
        """Convert domain entity to MongoDB document."""
        return {
            "_id": str(exam.id),
            "id": str(exam.id),
            "title": exam.title,
            "description": exam.description,
            "start_date": exam.start_date,
            "end_date": exam.end_date,
            "fee": str(exam.fee),
            "status": exam.status.value,
            "created_at": exam.created_at,
        }
    
    @staticmethod
    def to_entity(document: dict) -> Exam:
        """Convert MongoDB document to domain entity."""
        from decimal import Decimal
        from uuid import UUID
        from ...domain.exam.entity import ExamStatus
        
        # Handle both string and UUID id
        exam_id = document.get("id") or document.get("_id")
        if isinstance(exam_id, str):
            exam_id = UUID(exam_id)
        
        return Exam(
            id=exam_id,
            title=document["title"],
            description=document.get("description"),
            start_date=document["start_date"],
            end_date=document["end_date"],
            fee=Decimal(str(document.get("fee", "0.00"))),
            status=ExamStatus(document["status"]),
            created_at=document["created_at"],
        )


