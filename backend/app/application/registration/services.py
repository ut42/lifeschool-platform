from typing import List
from uuid import UUID

from ...domain.exam.entity import ExamStatus
from ...domain.exam.exceptions import ExamNotFoundError
from ...domain.exam.repository import ExamRepository
from ...domain.registration.entity import ExamRegistration, RegistrationStatus
from ...domain.registration.exceptions import DuplicateRegistrationError
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import User
from ...domain.user.exceptions import UserNotFoundError
from ...domain.user.repository import UserRepository
from .dto import RegistrationResponse


class RegistrationService:
    """Application service for registration operations."""
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
        exam_repository: ExamRepository,
        user_repository: UserRepository,
    ):
        self.registration_repository = registration_repository
        self.exam_repository = exam_repository
        self.user_repository = user_repository
    
    async def register_for_exam(
        self,
        user_id: UUID,
        exam_id: UUID,
    ) -> ExamRegistration:
        """Register a user for an exam. Enforces all business rules."""
        # Business Rule 1: User must have mobile (profile complete)
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        if not user.is_profile_complete:
            raise ValueError("User profile must be complete (mobile number required) to register for exams")
        
        # Business Rule 2: Exam must exist
        exam = await self.exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        
        # Business Rule 3: Cannot register for DRAFT exam
        if exam.status != ExamStatus.ACTIVE:
            raise ValueError("Cannot register for DRAFT exam. Only ACTIVE exams can be registered for.")
        
        # Business Rule 4: Cannot register twice for same exam
        existing_registration = await self.registration_repository.get_by_user_and_exam(
            user_id, exam_id
        )
        if existing_registration:
            raise DuplicateRegistrationError(
                f"User {user_id} is already registered for exam {exam_id}"
            )
        
        # Create registration
        registration = ExamRegistration(
            user_id=user_id,
            exam_id=exam_id,
            status=RegistrationStatus.REGISTERED,
        )
        
        return await self.registration_repository.create(registration)
    
    async def get_user_registrations(self, user_id: UUID) -> List[ExamRegistration]:
        """Get all registrations for a user."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        return await self.registration_repository.get_by_user_id(user_id)
    
    @staticmethod
    def to_dto(registration: ExamRegistration) -> RegistrationResponse:
        """Convert domain entity to DTO."""
        return RegistrationResponse(
            id=registration.id,
            user_id=registration.user_id,
            exam_id=registration.exam_id,
            status=registration.status,
            created_at=registration.created_at,
        )

