import pytest
from datetime import datetime, timezone

from app.application.content.services import ContentService
from app.domain.content.entity import Content, ContentStatus, ContentType
from app.domain.content.repository import ContentRepository
from app.domain.user.entity import UserRole


class InMemoryContentRepository(ContentRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._contents = {}
    
    async def create(self, content: Content) -> Content:
        self._contents[str(content.id)] = content
        return content
    
    async def update(self, content: Content) -> Content:
        if str(content.id) not in self._contents:
            from app.domain.content.exceptions import ContentNotFoundError
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
async def test_draft_not_visible_to_users_or_guests():
    """Test that draft content is not visible to users or guests."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    content = await service.create_content(
        title="Draft",
        body="Body",
        content_type="BLOG",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    
    # Admin can see draft via admin list
    admin_items = await service.list_content_admin("BLOG", UserRole.ADMIN)
    assert len(admin_items) == 1
    
    # USER/GUEST sees nothing in public list
    user_items = await service.list_content_public("BLOG")
    assert len(user_items) == 0


@pytest.mark.asyncio
async def test_published_visible_to_all():
    """Test that published content is visible to all."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    content = await service.create_content(
        title="Published",
        body="Body",
        content_type="COURSE",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    await service.publish_content(content.id, UserRole.ADMIN)
    
    # Public list shows published content
    items = await service.list_content_public("COURSE")
    assert len(items) == 1
    assert items[0].title == "Published"
    assert items[0].status == ContentStatus.PUBLISHED


@pytest.mark.asyncio
async def test_invalid_content_type_rejected():
    """Test that invalid content type is rejected."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    with pytest.raises(Exception):  # InvalidContentTypeError
        await service.list_content_public("INVALID_TYPE")


@pytest.mark.asyncio
async def test_get_content_public_only_returns_published():
    """Test that get_content_public only returns published content."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    # Create draft content
    draft = await service.create_content(
        title="Draft",
        body="Body",
        content_type="BLOG",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    
    # Try to get draft as public - should fail
    with pytest.raises(Exception):  # ContentNotFoundError
        await service.get_content_public(draft.id)
    
    # Publish and try again - should succeed
    await service.publish_content(draft.id, UserRole.ADMIN)
    published = await service.get_content_public(draft.id)
    assert published.status == ContentStatus.PUBLISHED

