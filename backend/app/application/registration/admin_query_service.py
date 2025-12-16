from typing import List
from uuid import UUID

from ...domain.exam.exceptions import ExamNotFoundError
from ...domain.exam.repository import ExamRepository
from ...domain.registration.repository import RegistrationRepository
from ...domain.user.entity import UserRole
from ...domain.user.repository import UserRepository
from .dto import RegistrationWithUserResponse, UserInfoDTO


class AdminRegistrationQueryService:
    """Query service for admin to view exam registrations."""
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
        exam_repository: ExamRepository,
        user_repository: UserRepository,
    ):
        self.registration_repository = registration_repository
        self.exam_repository = exam_repository
        self.user_repository = user_repository
    
    async def get_exam_registrations(
        self,
        exam_id: UUID,
        user_role: UserRole,
    ) -> List[RegistrationWithUserResponse]:
        """
        Get all registrations for an exam with user details.
        Only ADMIN can access this endpoint.
        """
        # Business Rule 1: Only ADMIN can access
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can view exam registrations")
        
        # Business Rule 2: Exam must exist
        exam = await self.exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        
        # Get all registrations for this exam
        registrations = await self.registration_repository.get_by_exam_id(exam_id)
        
        # Join with user data at application layer
        result = []
        for registration in registrations:
            user = await self.user_repository.get_by_id(registration.user_id)
            if user:
                result.append(
                    RegistrationWithUserResponse(
                        registration_id=registration.id,
                        user=UserInfoDTO(
                            id=user.id,
                            name=user.name,
                            email=user.email,
                            mobile=user.mobile,
                        ),
                        status=registration.status,
                        registered_at=registration.created_at,
                    )
                )
        
        return result

