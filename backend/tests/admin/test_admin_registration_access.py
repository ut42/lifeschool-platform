import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta

from app.application.registration.admin_query_service import AdminRegistrationQueryService
from app.domain.exam.entity import Exam, ExamStatus
from app.domain.exam.repository import ExamRepository
from app.domain.registration.entity import ExamRegistration, RegistrationStatus
from app.domain.registration.repository import RegistrationRepository
from app.domain.user.entity import User, UserRole
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
        if str(exam.id) not in self._exams:
            from app.domain.exam.exceptions import ExamNotFoundError
            raise ExamNotFoundError(f"Exam with id {exam.id} not found")
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
        self._by_exam = {}
    
    async def create(self, registration: ExamRegistration) -> ExamRegistration:
        key = (str(registration.user_id), str(registration.exam_id))
        if key in self._by_user_exam:
            from app.domain.registration.exceptions import DuplicateRegistrationError
            raise DuplicateRegistrationError("Duplicate")
        self._registrations[str(registration.id)] = registration
        self._by_user_exam[key] = registration
        
        # Index by exam_id
        exam_id_str = str(registration.exam_id)
        if exam_id_str not in self._by_exam:
            self._by_exam[exam_id_str] = []
        self._by_exam[exam_id_str].append(registration)
        
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
    
    async def get_by_exam_id(self, exam_id) -> list[ExamRegistration]:
        """Get all registrations for an exam."""
        exam_id_str = str(exam_id)
        return self._by_exam.get(exam_id_str, [])
    
    async def update_status(
        self,
        registration_id,
        new_status: RegistrationStatus,
        expected_status: RegistrationStatus = None,
    ) -> ExamRegistration:
        reg = self._registrations.get(str(registration_id))
        if not reg:
            from app.domain.registration.exceptions import RegistrationNotFoundError
            raise RegistrationNotFoundError(f"Registration {registration_id} not found")
        if expected_status and reg.status != expected_status:
            raise ValueError(
                f"Cannot transition from {reg.status} to {new_status}. Expected {expected_status}"
            )
        reg.status = new_status
        return reg


@pytest.mark.asyncio
async def test_non_admin_cannot_access_registrations():
    """Test that non-admin (USER) cannot access admin registration endpoint."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = AdminRegistrationQueryService(reg_repo, exam_repo, user_repo)
    
    # Create exam
    start_date = datetime.now(timezone.utc) + timedelta(days=30)
    end_date = start_date + timedelta(hours=3)
    exam = Exam(
        title="Test Exam",
        start_date=start_date,
        end_date=end_date,
        status=ExamStatus.ACTIVE,
    )
    await exam_repo.create(exam)
    
    # Try to access as USER role
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.get_exam_registrations(exam.id, UserRole.USER)


@pytest.mark.asyncio
async def test_admin_cannot_view_registrations_for_nonexistent_exam():
    """Test that admin cannot view registrations for non-existent exam."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = AdminRegistrationQueryService(reg_repo, exam_repo, user_repo)
    
    from uuid import uuid4
    
    with pytest.raises(Exception, match="not found"):
        await service.get_exam_registrations(uuid4(), UserRole.ADMIN)

