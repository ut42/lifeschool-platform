from ...domain.user.entity import User
from .models import UserDocument


class UserMapper:
    """Mapper between domain entity and MongoDB document."""
    
    @staticmethod
    def to_document(user: User) -> dict:
        """Convert domain entity to MongoDB document."""
        return {
            "_id": str(user.id),
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "mobile": user.mobile,
            "role": user.role.value,
            "created_at": user.created_at,
        }
    
    @staticmethod
    def to_entity(document: dict) -> User:
        """Convert MongoDB document to domain entity."""
        from uuid import UUID
        from ...domain.user.entity import UserRole
        
        # Handle both string and UUID id
        user_id = document.get("id") or document.get("_id")
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        
        return User(
            id=user_id,
            email=document["email"],
            name=document["name"],
            mobile=document.get("mobile"),
            role=UserRole(document["role"]),
            created_at=document["created_at"],
        )

