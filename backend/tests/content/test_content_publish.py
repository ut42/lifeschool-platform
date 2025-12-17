import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.application.content.services import ContentService
from app.domain.content.entity import Content, ContentStatus, ContentType
from app.domain.content.repository import ContentRepository
from app.domain.user.entity import UserRole
from app.domain.content.exceptions import ContentNotFoundError


class InMemoryContentRepository(ContentRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._contents = {}
    
    async def create(self, content: Content) -> Content:
        self._contents[str(content.id)] = content
        return content
    
    async def update(self, content: Content) -> Content:
        if str(content.id) not in self._contents:
            raise ContentNotFoundError(f"Content {content.id} not found")
        self._contents[str(content.id)] = content
        return content
    
    async def get_by_id(self, content_id):
        return self._contents.get(str(content_id))
    
    async def get_by_type_for_admin(self, content_type: ContentType):
        return [c for c in self._contents.values() if c.content_type == content_type]
    
    async def get_published_by_type(self, content_type: ContentType):
        return [
            c for c in self._contents.values()
            if c.content_type == content_type and c.status == ContentStatus.PUBLISHED
        ]


@pytest.mark.asyncio
async def test_publish_updates_status_and_timestamps():
    """Test that publishing updates status and timestamps."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    content = await service.create_content(
        title="Draft",
        body="Body",
        content_type="COURSE",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    
    original_updated_at = content.updated_at
    
    published = await service.publish_content(content.id, UserRole.ADMIN)
    
    assert published.status == ContentStatus.PUBLISHED
    assert published.updated_at >= original_updated_at


@pytest.mark.asyncio
async def test_publish_nonexistent_content_raises():
    """Test that publishing non-existent content raises error."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    fake_id = uuid4()
    
    with pytest.raises(ContentNotFoundError):
        await service.publish_content(fake_id, UserRole.ADMIN)

