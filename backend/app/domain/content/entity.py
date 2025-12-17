from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional
from uuid import UUID, uuid4


class ContentType(str, Enum):
    """Content type enumeration."""
    COURSE = "COURSE"
    BLOG = "BLOG"
    GALLERY = "GALLERY"


class ContentStatus(str, Enum):
    """Content status enumeration."""
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"


class Content:
    """Domain entity representing CMS content."""
    
    def __init__(
        self,
        content_type: ContentType,
        title: str,
        body: str,
        id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
        status: ContentStatus = ContentStatus.DRAFT,
        seo_meta: Optional[Dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        if not title or not title.strip():
            raise ValueError("title is required")
        if not body or not body.strip():
            raise ValueError("body is required")
        if not content_type:
            raise ValueError("content_type is required")
        
        self.id = id or uuid4()
        self.content_type = content_type
        self.title = title.strip()
        self.body = body.strip()
        self.metadata = metadata or {}
        self.status = status
        self.seo_meta = seo_meta or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    def __eq__(self, other):
        if not isinstance(other, Content):
            return False
        return self.id == other.id
    
    def __repr__(self):
        return f"<Content id={self.id} type={self.content_type.value} title={self.title[:30]}>"

