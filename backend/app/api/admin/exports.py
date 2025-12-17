from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ...application.export.service import ExportService
from ...core.dependencies import get_current_user_role, get_exam_repository, get_registration_repository, get_user_repository
from ...domain.exam.repository import ExamRepository
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import UserRole
from ...domain.user.repository import UserRepository
from ...domain.exam.exceptions import ExamNotFoundError

router = APIRouter(prefix="/admin/exams", tags=["admin-exports"])


def get_export_service(
    registration_repository: RegistrationRepository = Depends(get_registration_repository),
    exam_repository: ExamRepository = Depends(get_exam_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> ExportService:
    """Dependency to get export service."""
    from ...application.export.service import ExportService
    return ExportService(registration_repository, exam_repository, user_repository)


@router.get("/{exam_id}/registrations/export")
async def export_exam_registrations_csv(
    exam_id: UUID,
    user_role: UserRole = Depends(get_current_user_role),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export all registrations for an exam as CSV.
    Only ADMIN can access this endpoint.
    """
    if user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can export registrations",
        )
    
    try:
        csv_content = await export_service.export_exam_registrations_to_csv(exam_id)
        
        # Set response headers
        filename = f"exam_{exam_id}_registrations.csv"
        headers = {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        
        return Response(
            content=csv_content,
            headers=headers,
            media_type="text/csv",
        )
    except ExamNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

