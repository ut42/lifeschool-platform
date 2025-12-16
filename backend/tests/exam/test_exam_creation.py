import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from app.application.exam.dto import ExamCreateRequest
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
async def test_non_admin_cannot_create_exam():
    """Test that non-admin cannot create exam."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    request = ExamCreateRequest(
        title="Test Exam",
        start_date=start_date,
        end_date=end_date,
        fee=Decimal("500.00"),
    )
    
    with pytest.raises(PermissionError, match="Only ADMIN can create exams"):
        await service.create_exam(request, UserRole.USER)


@pytest.mark.asyncio
async def test_admin_can_create_exam():
    """Test that admin can create exam."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    request = ExamCreateRequest(
        title="Test Exam",
        description="Test Description",
        start_date=start_date,
        end_date=end_date,
        fee=Decimal("500.00"),
        status=ExamStatus.DRAFT,
    )
    
    exam = await service.create_exam(request, UserRole.ADMIN)
    
    assert exam is not None
    assert exam.title == "Test Exam"
    assert exam.description == "Test Description"
    assert exam.fee == Decimal("500.00")
    assert exam.status == ExamStatus.DRAFT


@pytest.mark.asyncio
async def test_start_date_must_be_before_end_date():
    """Test that start_date must be before end_date."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date - timedelta(hours=1)  # End before start
    
    request = ExamCreateRequest(
        title="Test Exam",
        start_date=start_date,
        end_date=end_date,
        fee=Decimal("500.00"),
    )
    
    with pytest.raises(ValueError, match="start_date must be before end_date"):
        await service.create_exam(request, UserRole.ADMIN)


@pytest.mark.asyncio
async def test_fee_must_be_greater_than_or_equal_to_zero():
    """Test that fee must be >= 0."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    # Test with negative fee in domain entity
    with pytest.raises(ValueError, match="fee must be >= 0"):
        Exam(
            title="Test Exam",
            start_date=start_date,
            end_date=end_date,
            fee=Decimal("-100.00"),
        )


@pytest.mark.asyncio
async def test_exam_creation_with_zero_fee():
    """Test that exam can be created with zero fee."""
    repository = InMemoryExamRepository()
    service = ExamService(repository)
    
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    request = ExamCreateRequest(
        title="Free Exam",
        start_date=start_date,
        end_date=end_date,
        fee=Decimal("0.00"),
    )
    
    exam = await service.create_exam(request, UserRole.ADMIN)
    
    assert exam.fee == Decimal("0.00")


