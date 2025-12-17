from typing import Dict, Any

from ...domain.content.entity import Content, ContentType, ContentStatus


class ContentMapper:
    """Mapper for converting between Content entity and MongoDB document."""
    
    @staticmethod
    def to_document(content: Content) -> Dict[str, Any]:
        """Convert Content entity to MongoDB document."""
        return {
            "id": str(content.id),
            "content_type": content.content_type.value,
            "title": content.title,
            "body": content.body,
            "metadata": content.metadata,
            "status": content.status.value,
            "seo_meta": content.seo_meta,
            "created_at": content.created_at,
            "updated_at": content.updated_at,
        }
    
    @staticmethod
    def to_entity(document: Dict[str, Any]) -> Content:
        """Convert MongoDB document to Content entity."""
        from datetime import datetime
        
        # Handle datetime conversion
        created_at = document.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()
        
        updated_at = document.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        elif not isinstance(updated_at, datetime):
            updated_at = datetime.now()
        
        from uuid import UUID
        
        return Content(
            id=UUID(document["id"]),
            content_type=ContentType(document["content_type"]),
            title=document["title"],
            body=document["body"],
            metadata=document.get("metadata", {}),
            status=ContentStatus(document["status"]),
            seo_meta=document.get("seo_meta", {}),
            created_at=created_at,
            updated_at=updated_at,
        )

