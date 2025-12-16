from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entity import Exam


class ExamRepository(ABC):
    """Repository interface for Exam entity."""
    
    @abstractmethod
    async def create(self, exam: Exam) -> Exam:
        """Create a new exam."""
        pass
    
    @abstractmethod
    async def get_by_id(self, exam_id: UUID) -> Optional[Exam]:
        """Get exam by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Exam]:
        """Get all exams."""
        pass
    
    @abstractmethod
    async def get_active(self) -> List[Exam]:
        """Get all active exams."""
        pass
    
    @abstractmethod
    async def update(self, exam: Exam) -> Exam:
        """Update an existing exam."""
        pass

