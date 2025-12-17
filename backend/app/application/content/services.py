from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from ...domain.content.entity import Content, ContentType, ContentStatus
from ...domain.content.repository import ContentRepository
from ...domain.content.exceptions import ContentNotFoundError, InvalidContentTypeError
from ...domain.user.entity import UserRole
from .dto import ContentResponse


class ContentService:
    """Service for managing CMS content."""
    
    VALID_CONTENT_TYPES = {ContentType.COURSE, ContentType.BLOG, ContentType.GALLERY}
    
    def __init__(self, content_repository: ContentRepository):
        self.content_repository = content_repository
    
    def _validate_content_type(self, content_type_str: str) -> ContentType:
        """Validate and convert content type string to enum."""
        try:
            content_type = ContentType(content_type_str.upper())
            if content_type not in self.VALID_CONTENT_TYPES:
                raise InvalidContentTypeError(f"Invalid content type: {content_type_str}")
            return content_type
        except ValueError:
            raise InvalidContentTypeError(f"Invalid content type: {content_type_str}")
    
    def to_dto(self, content: Content) -> ContentResponse:
        """Convert Content entity to DTO."""
        return ContentResponse(
            id=content.id,
            content_type=content.content_type,
            title=content.title,
            body=content.body,
            metadata=content.metadata,
            status=content.status,
            seo_meta=content.seo_meta,
            created_at=content.created_at,
            updated_at=content.updated_at,
        )
    
    async def create_content(
        self,
        title: str,
        body: str,
        content_type: str,
        metadata: Optional[dict] = None,
        seo_meta: Optional[dict] = None,
        user_role: UserRole = None,
    ) -> Content:
        """
        Create new content.
        Only ADMIN can create content.
        """
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can create content")
        
        content_type_enum = self._validate_content_type(content_type)
        
        content = Content(
            content_type=content_type_enum,
            title=title,
            body=body,
            metadata=metadata or {},
            seo_meta=seo_meta or {},
            status=ContentStatus.DRAFT,
        )
        
        return await self.content_repository.create(content)
    
    async def update_content(
        self,
        content_id: UUID,
        title: Optional[str] = None,
        body: Optional[str] = None,
        metadata: Optional[dict] = None,
        seo_meta: Optional[dict] = None,
        user_role: UserRole = None,
    ) -> Content:
        """
        Update existing content.
        Only ADMIN can update content.
        Only DRAFT content can be updated.
        """
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can update content")
        
        content = await self.content_repository.get_by_id(content_id)
        if not content:
            raise ContentNotFoundError(f"Content with id {content_id} not found")
        
        if content.status != ContentStatus.DRAFT:
            raise ValueError("Only DRAFT content can be updated")
        
        # Update fields if provided
        if title is not None:
            content.title = title.strip()
        if body is not None:
            content.body = body.strip()
        if metadata is not None:
            content.metadata = metadata
        if seo_meta is not None:
            content.seo_meta = seo_meta
        
        content.updated_at = datetime.now(timezone.utc)
        
        return await self.content_repository.update(content)
    
    async def publish_content(
        self,
        content_id: UUID,
        user_role: UserRole = None,
    ) -> Content:
        """
        Publish content (change status from DRAFT to PUBLISHED).
        Only ADMIN can publish content.
        """
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can publish content")
        
        content = await self.content_repository.get_by_id(content_id)
        if not content:
            raise ContentNotFoundError(f"Content with id {content_id} not found")
        
        content.status = ContentStatus.PUBLISHED
        content.updated_at = datetime.now(timezone.utc)
        
        return await self.content_repository.update(content)
    
    async def list_content_admin(
        self,
        content_type: str,
        user_role: UserRole = None,
    ) -> List[ContentResponse]:
        """
        List content for admin (includes DRAFT and PUBLISHED).
        Only ADMIN can access this.
        """
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can list all content")
        
        content_type_enum = self._validate_content_type(content_type)
        contents = await self.content_repository.get_by_type_for_admin(content_type_enum)
        
        return [self.to_dto(content) for content in contents]
    
    async def list_content_public(
        self,
        content_type: str,
    ) -> List[ContentResponse]:
        """
        List published content for public access.
        No authentication required (GUEST or USER can access).
        """
        content_type_enum = self._validate_content_type(content_type)
        contents = await self.content_repository.get_published_by_type(content_type_enum)
        
        return [self.to_dto(content) for content in contents]
    
    async def get_content_public(
        self,
        content_id: UUID,
    ) -> ContentResponse:
        """
        Get published content by ID for public access.
        Returns content only if it's PUBLISHED.
        """
        content = await self.content_repository.get_by_id(content_id)
        if not content:
            raise ContentNotFoundError(f"Content with id {content_id} not found")
        
        if content.status != ContentStatus.PUBLISHED:
            raise ContentNotFoundError(f"Content with id {content_id} is not published")
        
        return self.to_dto(content)

