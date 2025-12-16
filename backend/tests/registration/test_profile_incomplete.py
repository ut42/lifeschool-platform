import pytest
from datetime import datetime, timezone, timedelta

from app.application.registration.services import RegistrationService
from app.domain.exam.entity import Exam, ExamStatus
from app.domain.exam.repository import ExamRepository
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
    
    async def create(self, registration):
        from app.domain.registration.entity import ExamRegistration
        key = (str(registration.user_id), str(registration.exam_id))
        if key in self._by_user_exam:
            from app.domain.registration.exceptions import DuplicateRegistrationError
            raise DuplicateRegistrationError("Duplicate")
        self._registrations[str(registration.id)] = registration
        self._by_user_exam[key] = registration
        return registration
    
    async def get_by_id(self, registration_id):
        return self._registrations.get(str(registration_id))
    
    async def get_by_user_and_exam(self, user_id, exam_id):
        key = (str(user_id), str(exam_id))
        return self._by_user_exam.get(key)
    
    async def get_by_user_id(self, user_id):
        return [
            reg for reg in self._registrations.values()
            if str(reg.user_id) == str(user_id)
        ]
    
    async def get_by_exam_id(self, exam_id):
        return [
            reg for reg in self._registrations.values()
            if str(reg.exam_id) == str(exam_id)
        ]


@pytest.mark.asyncio
async def test_user_must_complete_profile_before_registering():
    """Test that user must complete profile (have mobile) before registering."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = RegistrationService(reg_repo, exam_repo, user_repo)
    
    # Create user without mobile
    user = User(email="test@example.com", name="Test User", mobile=None)
    await user_repo.create(user)
    
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
    
    # Try to register - should fail
    with pytest.raises(ValueError, match="profile must be complete"):
        await service.register_for_exam(user.id, exam.id)
    
    # Update user with mobile
    user.update_mobile("1234567890")
    await user_repo.update(user)
    
    # Now registration should succeed
    registration = await service.register_for_exam(user.id, exam.id)
    assert registration is not None

