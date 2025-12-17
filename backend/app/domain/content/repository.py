from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entity import Content, ContentType


class ContentRepository(ABC):
    """Repository interface for Content entity."""
    
    @abstractmethod
    async def create(self, content: Content) -> Content:
        """Create a new content."""
        pass
    
    @abstractmethod
    async def update(self, content: Content) -> Content:
        """Update existing content."""
        pass
    
    @abstractmethod
    async def get_by_id(self, content_id: UUID) -> Optional[Content]:
        """Get content by ID."""
        pass
    
    @abstractmethod
    async def get_by_type_for_admin(self, content_type: ContentType) -> List[Content]:
        """Get all content of a type (for admin - includes DRAFT and PUBLISHED)."""
        pass
    
    @abstractmethod
    async def get_published_by_type(self, content_type: ContentType) -> List[Content]:
        """Get published content of a type (for public access)."""
        pass

