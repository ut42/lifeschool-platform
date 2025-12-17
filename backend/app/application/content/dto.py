from datetime import datetime
from typing import Dict, Optional
from uuid import UUID
from pydantic import BaseModel

from ...domain.content.entity import ContentStatus, ContentType


class ContentCreateRequest(BaseModel):
    """Request DTO for creating content."""
    title: str
    body: str
    content_type: str
    metadata: Optional[Dict] = None
    seo_meta: Optional[Dict] = None


class ContentUpdateRequest(BaseModel):
    """Request DTO for updating content."""
    title: Optional[str] = None
    body: Optional[str] = None
    metadata: Optional[Dict] = None
    seo_meta: Optional[Dict] = None


class ContentResponse(BaseModel):
    """Response DTO for content."""
    id: UUID
    content_type: ContentType
    title: str
    body: str
    metadata: Dict
    status: ContentStatus
    seo_meta: Dict
    created_at: datetime
    updated_at: datetime

