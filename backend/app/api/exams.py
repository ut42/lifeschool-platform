from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..application.exam.dto import ExamCreateRequest, ExamResponse, ExamUpdateRequest
from ..application.exam.services import ExamService
from ..core.dependencies import get_current_user_role, get_exam_repository
from ..domain.exam.repository import ExamRepository
from ..domain.user.entity import UserRole

router = APIRouter(prefix="/exams", tags=["exams"])


def get_exam_service(
    exam_repository: ExamRepository = Depends(get_exam_repository),
) -> ExamService:
    """Dependency to get exam service."""
    from ..application.exam.services import ExamService
    return ExamService(exam_repository)


@router.post("/admin", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
async def create_exam(
    request: ExamCreateRequest,
    exam_service: ExamService = Depends(get_exam_service),
    user_role: UserRole = Depends(get_current_user_role),
):
    """Create a new exam. Only ADMIN can create exams."""
    try:
        exam = await exam_service.create_exam(request, user_role)
        return exam_service.to_dto(exam)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=list[ExamResponse])
async def list_exams(
    exam_service: ExamService = Depends(get_exam_service),
    user_role: UserRole = Depends(get_current_user_role),
):
    """List exams. ADMIN sees all, USER sees only ACTIVE."""
    exams = await exam_service.list_exams(user_role)
    return [exam_service.to_dto(exam) for exam in exams]


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: UUID,
    exam_service: ExamService = Depends(get_exam_service),
    user_role: UserRole = Depends(get_current_user_role),
):
    """Get exam by ID. USER cannot access DRAFT exams."""
    try:
        exam = await exam_service.get_exam_by_id(exam_id, user_role)
        return exam_service.to_dto(exam)
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


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: UUID,
    request: ExamUpdateRequest,
    exam_service: ExamService = Depends(get_exam_service),
    user_role: UserRole = Depends(get_current_user_role),
):
    """Update an exam. Only ADMIN can update exams."""
    try:
        exam = await exam_service.update_exam(exam_id, request, user_role)
        return exam_service.to_dto(exam)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise

