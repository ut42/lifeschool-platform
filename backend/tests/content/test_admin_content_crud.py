import pytest
from datetime import datetime, timezone

from app.application.content.services import ContentService
from app.domain.content.entity import Content, ContentStatus, ContentType
from app.domain.content.repository import ContentRepository
from app.domain.user.entity import UserRole
from app.domain.content.exceptions import ContentNotFoundError, InvalidContentTypeError


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
async def test_admin_can_create_and_update_draft_content():
    """Test that admin can create and update draft content."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    # Admin creates draft content
    content = await service.create_content(
        title="Test Course",
        body="Course body",
        content_type="COURSE",
        metadata={"level": "beginner"},
        seo_meta={"slug": "test-course"},
        user_role=UserRole.ADMIN,
    )
    
    assert content.title == "Test Course"
    assert content.status == ContentStatus.DRAFT
    assert content.content_type == ContentType.COURSE
    
    # Admin updates draft
    updated = await service.update_content(
        content_id=content.id,
        title="Updated Course",
        body="Updated body",
        metadata={"level": "advanced"},
        seo_meta={"slug": "updated-course"},
        user_role=UserRole.ADMIN,
    )
    
    assert updated.title == "Updated Course"
    assert updated.metadata["level"] == "advanced"
    assert updated.status == ContentStatus.DRAFT


@pytest.mark.asyncio
async def test_only_admin_can_create_update_publish():
    """Test that only admin can create, update, and publish content."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    # Non-admin cannot create
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.create_content(
            title="Not allowed",
            body="",
            content_type="COURSE",
            metadata={},
            seo_meta={},
            user_role=UserRole.USER,
        )
    
    # Create content as admin
    content = await service.create_content(
        title="Admin Content",
        body="Body",
        content_type="BLOG",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    
    # Non-admin cannot update
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.update_content(
            content_id=content.id,
            title="Hacked",
            body="",
            metadata={},
            seo_meta={},
            user_role=UserRole.USER,
        )
    
    # Non-admin cannot publish
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.publish_content(content.id, UserRole.USER)


@pytest.mark.asyncio
async def test_cannot_update_published_content():
    """Test that published content cannot be updated."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    # Create and publish content
    content = await service.create_content(
        title="Published",
        body="Body",
        content_type="BLOG",
        metadata={},
        seo_meta={},
        user_role=UserRole.ADMIN,
    )
    
    await service.publish_content(content.id, UserRole.ADMIN)
    
    # Try to update published content - should fail
    with pytest.raises(ValueError, match="Only DRAFT"):
        await service.update_content(
            content_id=content.id,
            title="Updated",
            body="New body",
            metadata={},
            seo_meta={},
            user_role=UserRole.ADMIN,
        )


@pytest.mark.asyncio
async def test_invalid_content_type_rejected():
    """Test that invalid content type is rejected."""
    repo = InMemoryContentRepository()
    service = ContentService(repo)
    
    with pytest.raises(InvalidContentTypeError):
        await service.create_content(
            title="Test",
            body="Body",
            content_type="INVALID_TYPE",
            metadata={},
            seo_meta={},
            user_role=UserRole.ADMIN,
        )

