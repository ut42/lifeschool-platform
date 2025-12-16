from ...domain.registration.entity import ExamRegistration
from ...domain.registration.entity import RegistrationStatus


class RegistrationMapper:
    """Mapper between domain entity and MongoDB document."""
    
    @staticmethod
    def to_document(registration: ExamRegistration) -> dict:
        """Convert domain entity to MongoDB document."""
        return {
            "_id": str(registration.id),
            "id": str(registration.id),
            "user_id": str(registration.user_id),
            "exam_id": str(registration.exam_id),
            "status": registration.status.value,
            "created_at": registration.created_at,
        }
    
    @staticmethod
    def to_entity(document: dict) -> ExamRegistration:
        """Convert MongoDB document to domain entity."""
        from uuid import UUID
        
        # Handle both string and UUID id
        reg_id = document.get("id") or document.get("_id")
        if isinstance(reg_id, str):
            reg_id = UUID(reg_id)
        
        user_id = document.get("user_id")
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        
        exam_id = document.get("exam_id")
        if isinstance(exam_id, str):
            exam_id = UUID(exam_id)
        
        return ExamRegistration(
            id=reg_id,
            user_id=user_id,
            exam_id=exam_id,
            status=RegistrationStatus(document["status"]),
            created_at=document["created_at"],
        )

