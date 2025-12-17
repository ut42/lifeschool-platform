from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from ..application.content.dto import ContentCreateRequest, ContentUpdateRequest, ContentResponse
from ..application.content.services import ContentService
from ..core.dependencies import get_current_user, get_current_user_role, get_content_repository
from ..domain.content.repository import ContentRepository
from ..domain.content.exceptions import ContentNotFoundError, InvalidContentTypeError
from ..domain.user.entity import User, UserRole

router = APIRouter(prefix="/content", tags=["content"])


def get_content_service(
    content_repository: ContentRepository = Depends(get_content_repository),
) -> ContentService:
    """Dependency to get ContentService."""
    return ContentService(content_repository)


# Admin APIs
admin_router = APIRouter(prefix="/admin/content", tags=["admin-content"])


@admin_router.post("", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    request: ContentCreateRequest,
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    content_service: ContentService = Depends(get_content_service),
):
    """Create new content. ADMIN only."""
    try:
        content = await content_service.create_content(
            title=request.title,
            body=request.body,
            content_type=request.content_type,
            metadata=request.metadata or {},
            seo_meta=request.seo_meta or {},
            user_role=user_role,
        )
        return content_service.to_dto(content)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except InvalidContentTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    request: ContentUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    content_service: ContentService = Depends(get_content_service),
):
    """Update content. ADMIN only. Only DRAFT can be updated."""
    try:
        content = await content_service.update_content(
            content_id=content_id,
            title=request.title,
            body=request.body,
            metadata=request.metadata,
            seo_meta=request.seo_meta,
            user_role=user_role,
        )
        return content_service.to_dto(content)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ContentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@admin_router.post("/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    content_service: ContentService = Depends(get_content_service),
):
    """Publish content. ADMIN only."""
    try:
        content = await content_service.publish_content(content_id, user_role)
        return content_service.to_dto(content)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ContentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@admin_router.get("", response_model=List[ContentResponse])
async def list_content_admin(
    type: str = Query(..., description="Content type: COURSE, BLOG, or GALLERY"),
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    content_service: ContentService = Depends(get_content_service),
):
    """List all content (DRAFT + PUBLISHED) for admin. ADMIN only."""
    try:
        return await content_service.list_content_admin(type, user_role)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except (InvalidContentTypeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Public APIs
@router.get("", response_model=List[ContentResponse])
async def list_content_public(
    type: str = Query(..., description="Content type: COURSE, BLOG, or GALLERY"),
    content_service: ContentService = Depends(get_content_service),
):
    """List published content. Public access (no auth required)."""
    try:
        return await content_service.list_content_public(type)
    except (InvalidContentTypeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content_public(
    content_id: UUID,
    content_service: ContentService = Depends(get_content_service),
):
    """Get published content by ID. Public access (no auth required)."""
    try:
        return await content_service.get_content_public(content_id)
    except ContentNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

