from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.content.entity import Content, ContentType, ContentStatus
from ...domain.content.repository import ContentRepository
from ...domain.content.exceptions import ContentNotFoundError
from .mapper import ContentMapper


class MongoDBContentRepository(ContentRepository):
    """MongoDB implementation of ContentRepository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.content
    
    async def create(self, content: Content) -> Content:
        """Create a new content."""
        document = ContentMapper.to_document(content)
        await self.collection.insert_one(document)
        return content
    
    async def update(self, content: Content) -> Content:
        """Update existing content."""
        document = ContentMapper.to_document(content)
        await self.collection.update_one(
            {"id": str(content.id)},
            {"$set": document}
        )
        return content
    
    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        """Get content by ID."""
        document = await self.collection.find_one({"id": str(content_id)})
        if not document:
            return None
        return ContentMapper.to_entity(document)
    
    async def get_by_type_for_admin(self, content_type: ContentType) -> List[Content]:
        """Get all content of a type (for admin - includes DRAFT and PUBLISHED)."""
        cursor = self.collection.find({"content_type": content_type.value})
        documents = await cursor.to_list(length=None)
        return [ContentMapper.to_entity(doc) for doc in documents]
    
    async def get_published_by_type(self, content_type: ContentType) -> List[Content]:
        """Get published content of a type (for public access)."""
        cursor = self.collection.find({
            "content_type": content_type.value,
            "status": ContentStatus.PUBLISHED.value,
        })
        documents = await cursor.to_list(length=None)
        return [ContentMapper.to_entity(doc) for doc in documents]

