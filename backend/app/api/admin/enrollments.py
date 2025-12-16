from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ...application.enrollment.dto import EnrollmentResponse, BulkEnrollmentRequest, BulkEnrollmentResponse
from ...application.enrollment.services import EnrollmentService
from ...core.dependencies import get_current_user, get_current_user_role, get_registration_repository
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import User, UserRole
from ...domain.registration.exceptions import RegistrationNotFoundError

router = APIRouter(prefix="/admin/registrations", tags=["admin-enrollments"])


def get_enrollment_service(
    registration_repository: RegistrationRepository = Depends(get_registration_repository),
) -> EnrollmentService:
    """Dependency to get enrollment service."""
    return EnrollmentService(registration_repository)


@router.post("/{registration_id}/enroll", response_model=EnrollmentResponse, status_code=status.HTTP_200_OK)
async def enroll_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    """
    Enroll a single registration.
    Only ADMIN can access this endpoint.
    Transitions status from PAID/REGISTERED/PAYMENT_PENDING to ENROLLED.
    """
    if user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can enroll registrations",
        )
    
    try:
        result = await enrollment_service.enroll_registration(
            registration_id, current_user.id, current_user.role
        )
        return EnrollmentResponse(**result)
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except (ValueError, RegistrationNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if isinstance(e, ValueError) else status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/enroll/bulk", response_model=BulkEnrollmentResponse, status_code=status.HTTP_200_OK)
async def bulk_enroll_registrations(
    request: BulkEnrollmentRequest,
    current_user: User = Depends(get_current_user),
    user_role: UserRole = Depends(get_current_user_role),
    enrollment_service: EnrollmentService = Depends(get_enrollment_service),
):
    """
    Bulk enroll multiple registrations.
    Only ADMIN can access this endpoint.
    Allows partial success - some registrations may fail while others succeed.
    """
    if user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ADMIN can bulk enroll registrations",
        )
    
    try:
        result = await enrollment_service.bulk_enroll_registrations(
            request.registration_ids, current_user.id, current_user.role
        )
        return result
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

