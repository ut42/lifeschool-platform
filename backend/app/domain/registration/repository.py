from abc import ABC, abstractmethod
from typing import List, Optional
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

