import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from app.application.exam.services import ExamService
from app.domain.exam.entity import Exam, ExamStatus
from app.domain.exam.exceptions import ExamNotFoundError
from app.domain.exam.repository import ExamRepository
from app.domain.user.entity import UserRole


class InMemoryExamRepository(ExamRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._exams = {}
    
    async def create(self, exam: Exam) -> Exam:
        self._exams[str(exam.id)] = exam
        return exam
    
    async def get_by_id(self, exam_id) -> Exam:
        return self._exams.get(str(exam_id))
    
    async def get_all(self) -> list[Exam]:
        return list(self._exams.values())
    
    async def get_active(self) -> list[Exam]:
        return [exam for exam in self._exams.values() if exam.status == ExamStatus.ACTIVE]


@pytest.mark.asyncio
async def test_user_cannot_access_draft_exam():
    """Test that user cannot access DRAFT exam."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    draft_exam = Exam(
        title="Draft Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.DRAFT,
    )
    await repository.create(draft_exam)
    
    with pytest.raises(PermissionError, match="USER cannot access DRAFT exams"):
        await service.get_exam_by_id(draft_exam.id, UserRole.USER)


@pytest.mark.asyncio
async def test_user_can_access_active_exam():
    """Test that user can access ACTIVE exam."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    active_exam = Exam(
        title="Active Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await repository.create(active_exam)
    
    exam = await service.get_exam_by_id(active_exam.id, UserRole.USER)
    
    assert exam is not None
    assert exam.id == active_exam.id
    assert exam.status == ExamStatus.ACTIVE


@pytest.mark.asyncio
async def test_admin_can_access_any_exam():
    """Test that admin can access any exam (draft or active)."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    # Test draft exam
    draft_exam = Exam(
        title="Draft Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.DRAFT,
    )
    await repository.create(draft_exam)
    
    exam = await service.get_exam_by_id(draft_exam.id, UserRole.ADMIN)
    assert exam is not None
    assert exam.id == draft_exam.id
    assert exam.status == ExamStatus.DRAFT
    
    # Test active exam
    active_exam = Exam(
        title="Active Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await repository.create(active_exam)
    
    exam = await service.get_exam_by_id(active_exam.id, UserRole.ADMIN)
    assert exam is not None
    assert exam.id == active_exam.id
    assert exam.status == ExamStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_nonexistent_exam_raises_error():
    """Test that getting nonexistent exam raises error."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    from uuid import uuid4
    
    with pytest.raises(ExamNotFoundError):
        await service.get_exam_by_id(uuid4(), UserRole.ADMIN)


