from typing import List
from uuid import UUID

from ...domain.exam.entity import Exam, ExamStatus
from ...domain.exam.exceptions import ExamNotFoundError
from ...domain.exam.repository import ExamRepository
from ...domain.user.entity import UserRole
from .dto import ExamCreateRequest, ExamResponse, ExamUpdateRequest


class ExamService:
    """Application service for exam operations."""
    
    def __init__(self, exam_repository: ExamRepository):
        self.exam_repository = exam_repository
    
    async def create_exam(
        self,
        request: ExamCreateRequest,
        user_role: UserRole,
    ) -> Exam:
        """Create a new exam. Only ADMIN can create exams."""
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can create exams")
        
        exam = Exam(
            title=request.title,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            fee=request.fee,
            status=request.status,
        )
        
        return await self.exam_repository.create(exam)
    
    async def get_exam_by_id(
        self,
        exam_id: UUID,
        user_role: UserRole,
    ) -> Exam:
        """Get exam by ID. USER cannot access DRAFT exams."""
        exam = await self.exam_repository.get_by_id(exam_id)
        
        if not exam:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        
        # Authorization: USER cannot access DRAFT exams
        if user_role == UserRole.USER and exam.status == ExamStatus.DRAFT:
            raise PermissionError("USER cannot access DRAFT exams")
        
        return exam
    
    async def list_exams(self, user_role: UserRole) -> List[Exam]:
        """List exams. ADMIN sees all, USER sees only ACTIVE."""
        if user_role == UserRole.ADMIN:
            return await self.exam_repository.get_all()
        else:
            return await self.exam_repository.get_active()
    
    async def update_exam(
        self,
        exam_id: UUID,
        request: ExamUpdateRequest,
        user_role: UserRole,
    ) -> Exam:
        """Update an exam. Only ADMIN can update exams."""
        if user_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can update exams")
        
        exam = await self.exam_repository.get_by_id(exam_id)
        
        if not exam:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        
        # Update fields if provided
        if request.title is not None:
            exam.title = request.title.strip()
        
        if request.description is not None:
            exam.description = request.description.strip() if request.description else None
        
        if request.start_date is not None:
            exam.start_date = request.start_date
        
        if request.end_date is not None:
            exam.end_date = request.end_date
        
        if request.fee is not None:
            if request.fee < 0:
                raise ValueError("fee must be >= 0")
            exam.fee = request.fee
        
        if request.status is not None:
            exam.status = request.status
        
        # Validate dates if both are being updated
        if request.start_date is not None or request.end_date is not None:
            if exam.start_date >= exam.end_date:
                raise ValueError("start_date must be before end_date")
        
        return await self.exam_repository.update(exam)
    
    @staticmethod
    def to_dto(exam: Exam) -> ExamResponse:
        """Convert domain entity to DTO."""
        return ExamResponse(
            id=exam.id,
            title=exam.title,
            description=exam.description,
            start_date=exam.start_date,
            end_date=exam.end_date,
            fee=exam.fee,
            status=exam.status,
            created_at=exam.created_at,
        )

