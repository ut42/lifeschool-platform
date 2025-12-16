from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from ..application.payment.dto import PaymentConfirmationResponse, PaymentInitiationResponse
from ..application.payment.services import PaymentService
from ..core.dependencies import get_current_user, get_exam_repository, get_registration_repository, get_user_repository
from ..domain.exam.repository import ExamRepository
from ..domain.registration.repository import RegistrationRepository
from ..domain.user.entity import User, UserRole
from ..domain.user.repository import UserRepository

router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(
    registration_repository: RegistrationRepository = Depends(get_registration_repository),
    exam_repository: ExamRepository = Depends(get_exam_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> PaymentService:
    """Dependency to get payment service."""
    from ..application.payment.services import PaymentService
    return PaymentService(registration_repository, exam_repository, user_repository)


@router.post("/registrations/{registration_id}/pay", response_model=PaymentInitiationResponse, status_code=status.HTTP_200_OK)
async def initiate_payment(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Initiate payment for a registration. Only USER role can initiate payment."""
    try:
        registration = await payment_service.initiate_payment(
            registration_id, current_user.id, current_user.role
        )
        
        # Generate mock payment_id
        from uuid import uuid4
        payment_id = uuid4()
        
        return PaymentInitiationResponse(
            registration_id=registration.id,
            status=registration.status,
            payment_id=payment_id,
            message="Payment initiated successfully. Please confirm payment.",
        )
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


@router.post("/{registration_id}/confirm", response_model=PaymentConfirmationResponse, status_code=status.HTTP_200_OK)
async def confirm_payment(
    registration_id: UUID,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service),
):
    """Confirm payment (mocked). Only USER role can confirm payment."""
    try:
        registration = await payment_service.confirm_payment(
            registration_id, current_user.id, current_user.role
        )
        
        # Generate mock payment_id (same as initiation)
        from uuid import uuid4
        payment_id = uuid4()
        
        from datetime import datetime, timezone
        return PaymentConfirmationResponse(
            registration_id=registration.id,
            status=registration.status,
            payment_id=payment_id,
            confirmed_at=datetime.now(timezone.utc),
            message="Payment confirmed successfully.",
        )
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

