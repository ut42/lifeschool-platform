import pytest
from datetime import datetime, timezone, timedelta

from app.application.registration.services import RegistrationService
from app.domain.exam.entity import Exam, ExamStatus
from app.domain.exam.repository import ExamRepository
from app.domain.registration.entity import ExamRegistration
from app.domain.registration.repository import RegistrationRepository
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository


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
    
    async def update(self, exam: Exam) -> Exam:
        self._exams[str(exam.id)] = exam
        return exam


class InMemoryUserRepository(UserRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._users = {}
    
    async def create(self, user: User) -> User:
        self._users[str(user.id)] = user
        return user
    
    async def get_by_id(self, user_id) -> User:
        return self._users.get(str(user_id))
    
    async def get_by_email(self, email: str) -> User:
        for user in self._users.values():
            if user.email == email.lower():
                return user
        return None
    
    async def update(self, user: User) -> User:
        self._users[str(user.id)] = user
        return user


class InMemoryRegistrationRepository(RegistrationRepository):
    """In-memory implementation for testing."""
    
    def __init__(self):
        self._registrations = {}
        self._by_user_exam = {}
    
    async def create(self, registration: ExamRegistration) -> ExamRegistration:
        key = (str(registration.user_id), str(registration.exam_id))
        if key in self._by_user_exam:
            from app.domain.registration.exceptions import DuplicateRegistrationError
            raise DuplicateRegistrationError("Duplicate")
        self._registrations[str(registration.id)] = registration
        self._by_user_exam[key] = registration
        return registration
    
    async def get_by_id(self, registration_id) -> ExamRegistration:
        return self._registrations.get(str(registration_id))
    
    async def get_by_user_and_exam(self, user_id, exam_id) -> ExamRegistration:
        key = (str(user_id), str(exam_id))
        return self._by_user_exam.get(key)
    
    async def get_by_user_id(self, user_id) -> list[ExamRegistration]:
        return [
            reg for reg in self._registrations.values()
            if str(reg.user_id) == str(user_id)
        ]


@pytest.mark.asyncio
async def test_user_can_see_their_registrations():
    """Test that user can see their registrations."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = RegistrationService(reg_repo, exam_repo, user_repo)
    
    # Create user with mobile
    user = User(email="test@example.com", name="Test User", mobile="1234567890")
    await user_repo.create(user)
    
    # Create two active exams
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    
    exam1 = Exam(
        title="Exam 1",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await exam_repo.create(exam1)
    
    exam2 = Exam(
        title="Exam 2",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await exam_repo.create(exam2)
    
    # Register for both exams
    reg1 = await service.register_for_exam(user.id, exam1.id)
    reg2 = await service.register_for_exam(user.id, exam2.id)
    
    # Get user registrations
    registrations = await service.get_user_registrations(user.id)
    
    assert len(registrations) == 2
    exam_ids = {reg.exam_id for reg in registrations}
    assert exam1.id in exam_ids
    assert exam2.id in exam_ids


@pytest.mark.asyncio
async def test_user_sees_only_their_own_registrations():
    """Test that user sees only their own registrations."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = RegistrationService(reg_repo, exam_repo, user_repo)
    
    # Create two users with mobile
    user1 = User(email="user1@example.com", name="User 1", mobile="1234567890")
    user2 = User(email="user2@example.com", name="User 2", mobile="9876543210")
    await user_repo.create(user1)
    await user_repo.create(user2)
    
    # Create active exam
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    exam = Exam(
        title="Active Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await exam_repo.create(exam)
    
    # User1 registers
    await service.register_for_exam(user1.id, exam.id)
    
    # User2 registers
    await service.register_for_exam(user2.id, exam.id)
    
    # User1 should see only their registration
    user1_regs = await service.get_user_registrations(user1.id)
    assert len(user1_regs) == 1
    assert user1_regs[0].user_id == user1.id
    
    # User2 should see only their registration
    user2_regs = await service.get_user_registrations(user2.id)
    assert len(user2_regs) == 1
    assert user2_regs[0].user_id == user2.id

