from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..application.exam.dto import ExamCreateRequest, ExamResponse, ExamUpdateRequest
from ..application.exam.services import ExamService
from ..application.registration.dto import RegistrationResponse
from ..application.registration.services import RegistrationService
from ..core.dependencies import get_current_user, get_current_user_role, get_exam_repository, get_registration_repository, get_user_repository
from ..domain.exam.repository import ExamRepository
from ..domain.registration.repository import RegistrationRepository
from ..domain.user.entity import User, UserRole
from ..domain.user.repository import UserRepository

router = APIRouter(prefix="/exams", tags=["exams"])


def get_exam_service(
    exam_repository: ExamRepository = Depends(get_exam_repository),
) -> ExamService:
    """Dependency to get exam service."""
    from ..application.exam.services import ExamService
    return ExamService(exam_repository)


def get_registration_service(
    registration_repository: RegistrationRepository = Depends(get_registration_repository),
    exam_repository: ExamRepository = Depends(get_exam_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> RegistrationService:
    """Dependency to get registration service."""
    from ..application.registration.services import RegistrationService
    return RegistrationService(registration_repository, exam_repository, user_repository)


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


@router.post("/{exam_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_exam(
    exam_id: UUID,
    current_user: User = Depends(get_current_user),
    registration_service: RegistrationService = Depends(get_registration_service),
):
    """Register current user for an exam. Only USER role can register."""
    if current_user.role != UserRole.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only USER role can register for exams",
        )
    
    try:
        registration = await registration_service.register_for_exam(
            current_user.id, exam_id
        )
        return registration_service.to_dto(registration)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        if "duplicate" in error_msg or "already registered" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

