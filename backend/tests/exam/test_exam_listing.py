import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from app.application.exam.services import ExamService
from app.domain.exam.entity import Exam, ExamStatus
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
async def test_admin_sees_all_exams():
    """Test that admin sees all exams (draft + active)."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    # Create draft exam
    draft_exam = Exam(
        title="Draft Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.DRAFT,
    )
    await repository.create(draft_exam)
    
    # Create active exam
    active_exam = Exam(
        title="Active Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await repository.create(active_exam)
    
    exams = await service.list_exams(UserRole.ADMIN)
    
    assert len(exams) == 2
    exam_titles = [exam.title for exam in exams]
    assert "Draft Exam" in exam_titles
    assert "Active Exam" in exam_titles


@pytest.mark.asyncio
async def test_user_sees_only_active_exams():
    """Test that user sees only active exams."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    # Create draft exam
    draft_exam = Exam(
        title="Draft Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.DRAFT,
    )
    await repository.create(draft_exam)
    
    # Create active exam
    active_exam = Exam(
        title="Active Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await repository.create(active_exam)
    
    exams = await service.list_exams(UserRole.USER)
    
    assert len(exams) == 1
    assert exams[0].title == "Active Exam"
    assert exams[0].status == ExamStatus.ACTIVE


