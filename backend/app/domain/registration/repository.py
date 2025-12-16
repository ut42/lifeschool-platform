from abc import ABC, abstractmethod
from typing import List, Optional, Set
from uuid import UUID

from .entity import ExamRegistration


class RegistrationRepository(ABC):
    """Repository interface for ExamRegistration entity."""
    
    @abstractmethod
    async def create(self, registration: ExamRegistration) -> ExamRegistration:
        """Create a new registration."""
        pass
    
    @abstractmethod
    async def get_by_id(self, registration_id: UUID) -> Optional[ExamRegistration]:
        """Get registration by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_and_exam(
        self,
        user_id: UUID,
        exam_id: UUID,
    ) -> Optional[ExamRegistration]:
        """Get registration by user_id and exam_id."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[ExamRegistration]:
        """Get all registrations for a user."""
        pass
    
    @abstractmethod
    async def get_by_exam_id(self, exam_id: UUID) -> List[ExamRegistration]:
        """Get all registrations for an exam."""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        registration_id: UUID,
        new_status: "RegistrationStatus",  # type: ignore
        expected_status: Optional["RegistrationStatus"] = None,  # type: ignore
        expected_statuses: Optional[Set["RegistrationStatus"]] = None,  # type: ignore
    ) -> ExamRegistration:
        """
        Update registration status atomically.
        
        Args:
            registration_id: ID of the registration
            new_status: The new status to set
            expected_status: If provided, only update if current status matches (single status)
            expected_statuses: If provided, only update if current status is in this set (multiple statuses)
        
        Returns:
            Updated registration
        
        Raises:
            RegistrationNotFoundError: If registration not found
            ValueError: If expected_status/expected_statuses doesn't match current status
        """
        pass

