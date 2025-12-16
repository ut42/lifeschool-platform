import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.application.enrollment.services import EnrollmentService
from app.domain.exam.entity import Exam, ExamStatus
from app.domain.exam.repository import ExamRepository
from app.domain.registration.entity import ExamRegistration, RegistrationStatus
from app.domain.registration.repository import RegistrationRepository
from app.domain.user.entity import User, UserRole
from app.domain.user.repository import UserRepository
from app.domain.registration.exceptions import RegistrationNotFoundError


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
        exam_id_str = str(exam_id)
        return self._by_exam.get(exam_id_str, [])
    
    async def update_status(
        self,
        registration_id,
        new_status: RegistrationStatus,
        expected_status: RegistrationStatus = None,
        expected_statuses: set = None,
    ) -> ExamRegistration:
        """Update registration status atomically."""
        reg = self._registrations.get(str(registration_id))
        if not reg:
            raise RegistrationNotFoundError(f"Registration {registration_id} not found")
        
        if expected_status and reg.status != expected_status:
            raise ValueError(
                f"Cannot transition from {reg.status} to {new_status}. Expected {expected_status}"
            )
        
        if expected_statuses and reg.status not in expected_statuses:
            raise ValueError(
                f"Cannot transition from {reg.status} to {new_status}. "
                f"Expected one of: {', '.join(s.value for s in expected_statuses)}"
            )
        
        reg.status = new_status
        return reg


@pytest.mark.asyncio
async def test_admin_can_enroll_paid_registration():
    """Test that ADMIN can enroll a PAID registration."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular user
    user = User(email="user@example.com", name="User", mobile="1234567890")
    await user_repo.create(user)
    
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
    
    # Create PAID registration
    registration = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    await reg_repo.create(registration)
    
    # Enroll registration
    result = await service.enroll_registration(registration.id, admin.id, admin.role)
    
    assert result["registration_id"] == registration.id
    assert result["status"] == RegistrationStatus.ENROLLED
    
    # Verify status was updated
    updated_reg = await reg_repo.get_by_id(registration.id)
    assert updated_reg.status == RegistrationStatus.ENROLLED


@pytest.mark.asyncio
async def test_admin_can_enroll_registered_registration():
    """Test that ADMIN can enroll a REGISTERED registration."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular user
    user = User(email="user@example.com", name="User", mobile="1234567890")
    await user_repo.create(user)
    
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
    
    # Create REGISTERED registration
    registration = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.REGISTERED,
    )
    await reg_repo.create(registration)
    
    # Enroll registration
    result = await service.enroll_registration(registration.id, admin.id, admin.role)
    
    assert result["registration_id"] == registration.id
    assert result["status"] == RegistrationStatus.ENROLLED


@pytest.mark.asyncio
async def test_admin_can_enroll_payment_pending_registration():
    """Test that ADMIN can enroll a PAYMENT_PENDING registration."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular user
    user = User(email="user@example.com", name="User", mobile="1234567890")
    await user_repo.create(user)
    
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
    
    # Create PAYMENT_PENDING registration
    registration = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAYMENT_PENDING,
    )
    await reg_repo.create(registration)
    
    # Enroll registration
    result = await service.enroll_registration(registration.id, admin.id, admin.role)
    
    assert result["registration_id"] == registration.id
    assert result["status"] == RegistrationStatus.ENROLLED


@pytest.mark.asyncio
async def test_non_admin_cannot_enroll():
    """Test that non-admin cannot enroll registrations."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create regular user (not admin)
    user = User(email="user@example.com", name="User", mobile="1234567890")
    await user_repo.create(user)
    
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
    
    # Create PAID registration
    registration = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    await reg_repo.create(registration)
    
    # Try to enroll as regular user - should fail
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.enroll_registration(registration.id, user.id, user.role)


@pytest.mark.asyncio
async def test_cannot_enroll_nonexistent_registration():
    """Test that cannot enroll a non-existent registration."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Try to enroll non-existent registration - should fail
    fake_id = uuid4()
    with pytest.raises(RegistrationNotFoundError):
        await service.enroll_registration(fake_id, admin.id, admin.role)


@pytest.mark.asyncio
async def test_cannot_enroll_already_enrolled_registration():
    """Test that cannot enroll an already ENROLLED registration."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular user
    user = User(email="user@example.com", name="User", mobile="1234567890")
    await user_repo.create(user)
    
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
    
    # Create ENROLLED registration
    registration = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.ENROLLED,
    )
    await reg_repo.create(registration)
    
    # Try to enroll again - should fail
    with pytest.raises(ValueError, match="already ENROLLED"):
        await service.enroll_registration(registration.id, admin.id, admin.role)

