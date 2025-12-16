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
async def test_admin_can_bulk_enroll_multiple_paid_registrations():
    """Test that ADMIN can bulk enroll multiple PAID registrations."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular users
    user1 = User(email="user1@example.com", name="User 1", mobile="1234567890")
    user2 = User(email="user2@example.com", name="User 2", mobile="1234567891")
    user3 = User(email="user3@example.com", name="User 3", mobile="1234567892")
    await user_repo.create(user1)
    await user_repo.create(user2)
    await user_repo.create(user3)
    
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
    
    # Create PAID registrations
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg2 = ExamRegistration(
        user_id=user2.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg3 = ExamRegistration(
        user_id=user3.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    await reg_repo.create(reg1)
    await reg_repo.create(reg2)
    await reg_repo.create(reg3)
    
    # Bulk enroll
    registration_ids = [reg1.id, reg2.id, reg3.id]
    result = await service.bulk_enroll_registrations(registration_ids, admin.id, admin.role)
    
    assert len(result.success) == 3
    assert len(result.failed) == 0
    assert reg1.id in result.success
    assert reg2.id in result.success
    assert reg3.id in result.success
    
    # Verify all were enrolled
    updated_reg1 = await reg_repo.get_by_id(reg1.id)
    updated_reg2 = await reg_repo.get_by_id(reg2.id)
    updated_reg3 = await reg_repo.get_by_id(reg3.id)
    assert updated_reg1.status == RegistrationStatus.ENROLLED
    assert updated_reg2.status == RegistrationStatus.ENROLLED
    assert updated_reg3.status == RegistrationStatus.ENROLLED


@pytest.mark.asyncio
async def test_bulk_enrollment_allows_partial_success():
    """Test that bulk enrollment allows partial success."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular users
    user1 = User(email="user1@example.com", name="User 1", mobile="1234567890")
    user2 = User(email="user2@example.com", name="User 2", mobile="1234567891")
    await user_repo.create(user1)
    await user_repo.create(user2)
    
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
    
    # Create one PAID and one ENROLLED registration
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg2 = ExamRegistration(
        user_id=user2.id,
        exam_id=exam.id,
        status=RegistrationStatus.ENROLLED,  # Already enrolled
    )
    await reg_repo.create(reg1)
    await reg_repo.create(reg2)
    
    # Bulk enroll
    registration_ids = [reg1.id, reg2.id]
    result = await service.bulk_enroll_registrations(registration_ids, admin.id, admin.role)
    
    assert len(result.success) == 1
    assert len(result.failed) == 1
    assert reg1.id in result.success
    assert reg2.id not in result.success
    
    # Check failed reason
    failed_item = result.failed[0]
    assert failed_item.registration_id == reg2.id
    assert "already ENROLLED" in failed_item.reason


@pytest.mark.asyncio
async def test_bulk_enrollment_handles_nonexistent_registrations():
    """Test that bulk enrollment handles non-existent registrations gracefully."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular user
    user1 = User(email="user1@example.com", name="User 1", mobile="1234567890")
    await user_repo.create(user1)
    
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
    
    # Create one PAID registration
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    await reg_repo.create(reg1)
    
    # Bulk enroll with one valid and one fake ID
    fake_id = uuid4()
    registration_ids = [reg1.id, fake_id]
    result = await service.bulk_enroll_registrations(registration_ids, admin.id, admin.role)
    
    assert len(result.success) == 1
    assert len(result.failed) == 1
    assert reg1.id in result.success
    
    # Check failed reason
    failed_item = result.failed[0]
    assert failed_item.registration_id == fake_id
    assert "not found" in failed_item.reason.lower()


@pytest.mark.asyncio
async def test_bulk_enrollment_skips_already_enrolled_safely():
    """Test that bulk enrollment safely skips already ENROLLED registrations."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = EnrollmentService(reg_repo)
    
    # Create admin user
    admin = User(email="admin@example.com", name="Admin", role=UserRole.ADMIN)
    await user_repo.create(admin)
    
    # Create regular users
    user1 = User(email="user1@example.com", name="User 1", mobile="1234567890")
    user2 = User(email="user2@example.com", name="User 2", mobile="1234567891")
    await user_repo.create(user1)
    await user_repo.create(user2)
    
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
    
    # Create one PAID and one ENROLLED registration
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg2 = ExamRegistration(
        user_id=user2.id,
        exam_id=exam.id,
        status=RegistrationStatus.ENROLLED,
    )
    await reg_repo.create(reg1)
    await reg_repo.create(reg2)
    
    # Bulk enroll - should succeed for reg1, skip reg2
    registration_ids = [reg1.id, reg2.id]
    result = await service.bulk_enroll_registrations(registration_ids, admin.id, admin.role)
    
    assert len(result.success) == 1
    assert len(result.failed) == 1
    assert reg1.id in result.success
    
    # Verify reg1 was enrolled, reg2 remains ENROLLED
    updated_reg1 = await reg_repo.get_by_id(reg1.id)
    updated_reg2 = await reg_repo.get_by_id(reg2.id)
    assert updated_reg1.status == RegistrationStatus.ENROLLED
    assert updated_reg2.status == RegistrationStatus.ENROLLED


@pytest.mark.asyncio
async def test_non_admin_cannot_bulk_enroll():
    """Test that non-admin cannot bulk enroll registrations."""
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
    reg1 = ExamRegistration(
        user_id=user.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    await reg_repo.create(reg1)
    
    # Try to bulk enroll as regular user - should fail
    with pytest.raises(PermissionError, match="Only ADMIN"):
        await service.bulk_enroll_registrations([reg1.id], user.id, user.role)

