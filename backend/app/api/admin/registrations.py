from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.registration.admin_query_service import AdminRegistrationQueryService
from ...application.registration.dto import RegistrationWithUserResponse
from ...core.dependencies import get_current_user_role, get_exam_repository, get_registration_repository, get_user_repository
from ...domain.exam.repository import ExamRepository
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import UserRole
from ...domain.user.repository import UserRepository

router = APIRouter(prefix="/admin", tags=["admin"])


def get_admin_registration_query_service(
    registration_repository: RegistrationRepository = Depends(get_registration_repository),
    exam_repository: ExamRepository = Depends(get_exam_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> AdminRegistrationQueryService:
    """Dependency to get admin registration query service."""
    from ...application.registration.admin_query_service import AdminRegistrationQueryService
    return AdminRegistrationQueryService(registration_repository, exam_repository, user_repository)


@router.get("/exams/{exam_id}/registrations", response_model=list[RegistrationWithUserResponse])
async def get_exam_registrations(
    exam_id: UUID,
    user_role: UserRole = Depends(get_current_user_role),
    query_service: AdminRegistrationQueryService = Depends(get_admin_registration_query_service),
):
    """Get all registrations for an exam with user details. Only ADMIN can access."""
    try:
        registrations = await query_service.get_exam_registrations(exam_id, user_role)
        return registrations
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise

