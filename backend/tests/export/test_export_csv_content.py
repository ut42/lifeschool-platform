import pytest
import csv
import io
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.application.export.service import ExportService
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
            from app.domain.registration.exceptions import RegistrationNotFoundError
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
async def test_csv_contains_correct_columns():
    """Test that CSV contains all required columns in correct order."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = ExportService(reg_repo, exam_repo, user_repo)
    
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
    
    # Export CSV
    csv_content = await service.export_exam_registrations_to_csv(exam.id)
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    
    # Check columns
    expected_columns = [
        "registration_id",
        "user_id",
        "user_name",
        "email",
        "mobile",
        "registration_status",
        "enrollment_status",
        "payment_status",
        "paid_at",
        "enrolled_at",
        "registered_at",
    ]
    
    assert list(reader.fieldnames) == expected_columns


@pytest.mark.asyncio
async def test_csv_contains_all_registrations():
    """Test that CSV contains all registrations for the exam."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = ExportService(reg_repo, exam_repo, user_repo)
    
    # Create users
    user1 = User(email="user1@test.com", name="User One", mobile="1234567890")
    user2 = User(email="user2@test.com", name="User Two", mobile="1234567891")
    user3 = User(email="user3@test.com", name="User Three", mobile="1234567892")
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
    
    # Create registrations
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.REGISTERED,
    )
    reg2 = ExamRegistration(
        user_id=user2.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg3 = ExamRegistration(
        user_id=user3.id,
        exam_id=exam.id,
        status=RegistrationStatus.ENROLLED,
    )
    await reg_repo.create(reg1)
    await reg_repo.create(reg2)
    await reg_repo.create(reg3)
    
    # Export CSV
    csv_content = await service.export_exam_registrations_to_csv(exam.id)
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    
    # Should have 3 registrations
    assert len(rows) == 3
    
    # Check that all registration IDs are present
    registration_ids = {str(reg1.id), str(reg2.id), str(reg3.id)}
    csv_registration_ids = {row["registration_id"] for row in rows}
    assert csv_registration_ids == registration_ids


@pytest.mark.asyncio
async def test_csv_contains_correct_user_data():
    """Test that CSV contains correct user data."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = ExportService(reg_repo, exam_repo, user_repo)
    
    # Create user
    user1 = User(email="user1@test.com", name="User One", mobile="1234567890")
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
    
    # Create registration
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.REGISTERED,
    )
    await reg_repo.create(reg1)
    
    # Export CSV
    csv_content = await service.export_exam_registrations_to_csv(exam.id)
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    
    # Check first registration
    row1 = rows[0]
    assert row1["user_id"] == str(user1.id)
    assert row1["user_name"] == user1.name
    assert row1["email"] == user1.email
    assert row1["mobile"] == user1.mobile


@pytest.mark.asyncio
async def test_csv_contains_correct_statuses():
    """Test that CSV contains correct status information."""
    exam_repo = InMemoryExamRepository()
    user_repo = InMemoryUserRepository()
    reg_repo = InMemoryRegistrationRepository()
    service = ExportService(reg_repo, exam_repo, user_repo)
    
    # Create users
    user1 = User(email="user1@test.com", name="User One", mobile="1234567890")
    user2 = User(email="user2@test.com", name="User Two", mobile="1234567891")
    user3 = User(email="user3@test.com", name="User Three", mobile="1234567892")
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
    
    # Create registrations with different statuses
    reg1 = ExamRegistration(
        user_id=user1.id,
        exam_id=exam.id,
        status=RegistrationStatus.REGISTERED,
    )
    reg2 = ExamRegistration(
        user_id=user2.id,
        exam_id=exam.id,
        status=RegistrationStatus.PAID,
    )
    reg3 = ExamRegistration(
        user_id=user3.id,
        exam_id=exam.id,
        status=RegistrationStatus.ENROLLED,
    )
    await reg_repo.create(reg1)
    await reg_repo.create(reg2)
    await reg_repo.create(reg3)
    
    # Export CSV
    csv_content = await service.export_exam_registrations_to_csv(exam.id)
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(csv_content))
    rows = list(reader)
    
    # Check REGISTERED status
    row1 = next(row for row in rows if row["registration_id"] == str(reg1.id))
    assert row1["registration_status"] == "REGISTERED"
    assert row1["enrollment_status"] == "NOT_ENROLLED"
    assert row1["payment_status"] == "NOT_PAID"
    
    # Check PAID status
    row2 = next(row for row in rows if row["registration_id"] == str(reg2.id))
    assert row2["registration_status"] == "PAID"
    assert row2["enrollment_status"] == "NOT_ENROLLED"
    assert row2["payment_status"] == "PAID"
    
    # Check ENROLLED status
    row3 = next(row for row in rows if row["registration_id"] == str(reg3.id))
    assert row3["registration_status"] == "ENROLLED"
    assert row3["enrollment_status"] == "ENROLLED"
    assert row3["payment_status"] == "PAID"
