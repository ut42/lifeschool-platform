from uuid import UUID, uuid4

from ...domain.exam.entity import ExamStatus
from ...domain.exam.exceptions import ExamNotFoundError
from ...domain.exam.repository import ExamRepository
from ...domain.registration.entity import RegistrationStatus
from ...domain.registration.exceptions import RegistrationNotFoundError
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import UserRole
from ...domain.user.repository import UserRepository


class PaymentService:
    """Application service for payment operations."""
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
        exam_repository: ExamRepository,
        user_repository: UserRepository,
    ):
        self.registration_repository = registration_repository
        self.exam_repository = exam_repository
        self.user_repository = user_repository
    
    async def initiate_payment(
        self,
        registration_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> "ExamRegistration":
        """
        Initiate payment for a registration.
        Transitions: REGISTERED → PAYMENT_PENDING
        
        Business Rules:
        - Only USER role can initiate payment
        - Registration must be in REGISTERED status
        - Exam must be ACTIVE (not DRAFT)
        """
        if user_role != UserRole.USER:
            raise PermissionError("Only USER role can initiate payment")
        
        # Get registration
        registration = await self.registration_repository.get_by_id(registration_id)
        if not registration:
            raise RegistrationNotFoundError(f"Registration with id {registration_id} not found")
        
        # Verify ownership
        if registration.user_id != user_id:
            raise PermissionError("Cannot initiate payment for another user's registration")
        
        # Business Rule 1: Cannot initiate payment unless status = REGISTERED
        if registration.status != RegistrationStatus.REGISTERED:
            raise ValueError(
                f"Cannot initiate payment. Registration status must be REGISTERED, but is {registration.status.value}"
            )
        
        # Business Rule 3: Cannot pay for DRAFT exam
        exam = await self.exam_repository.get_by_id(registration.exam_id)
        if not exam:
            raise ExamNotFoundError(f"Exam with id {registration.exam_id} not found")
        
        if exam.status == ExamStatus.DRAFT:
            raise ValueError("Cannot initiate payment for DRAFT exam")
        
        # Atomic update: REGISTERED → PAYMENT_PENDING
        updated_registration = await self.registration_repository.update_status(
            registration_id=registration_id,
            new_status=RegistrationStatus.PAYMENT_PENDING,
            expected_status=RegistrationStatus.REGISTERED,
        )
        
        return updated_registration
    
    async def confirm_payment(
        self,
        registration_id: UUID,
        user_id: UUID,
        user_role: UserRole,
    ) -> "ExamRegistration":
        """
        Confirm payment (mocked).
        Transitions: PAYMENT_PENDING → PAID
        
        Business Rules:
        - Only USER role can confirm payment
        - Registration must be in PAYMENT_PENDING status
        - Cannot confirm payment twice
        """
        if user_role != UserRole.USER:
            raise PermissionError("Only USER role can confirm payment")
        
        # Get registration
        registration = await self.registration_repository.get_by_id(registration_id)
        if not registration:
            raise RegistrationNotFoundError(f"Registration with id {registration_id} not found")
        
        # Verify ownership
        if registration.user_id != user_id:
            raise PermissionError("Cannot confirm payment for another user's registration")
        
        # Business Rule 2: Cannot confirm payment unless status = PAYMENT_PENDING
        if registration.status != RegistrationStatus.PAYMENT_PENDING:
            raise ValueError(
                f"Cannot confirm payment. Registration status must be PAYMENT_PENDING, but is {registration.status.value}"
            )
        
        # Business Rule 4: Cannot confirm payment twice (enforced by atomic update)
        # Atomic update: PAYMENT_PENDING → PAID
        updated_registration = await self.registration_repository.update_status(
            registration_id=registration_id,
            new_status=RegistrationStatus.PAID,
            expected_status=RegistrationStatus.PAYMENT_PENDING,
        )
        
        return updated_registration

