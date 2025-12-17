from typing import List
from uuid import UUID
import csv
import io

from ...domain.registration.repository import RegistrationRepository
from ...domain.exam.repository import ExamRepository
from ...domain.user.repository import UserRepository
from ...domain.registration.entity import RegistrationStatus
from ...domain.exam.exceptions import ExamNotFoundError
from .dto import CSVRegistrationRow


class ExportService:
    """Service for exporting registrations to CSV."""
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
        exam_repository: ExamRepository,
        user_repository: UserRepository,
    ):
        self.registration_repository = registration_repository
        self.exam_repository = exam_repository
        self.user_repository = user_repository
    
    def _derive_enrollment_status(self, status: RegistrationStatus) -> str:
        """Derive enrollment status from registration status."""
        if status == RegistrationStatus.ENROLLED:
            return "ENROLLED"
        return "NOT_ENROLLED"
    
    def _derive_payment_status(self, status: RegistrationStatus) -> str:
        """Derive payment status from registration status."""
        if status in [RegistrationStatus.PAID, RegistrationStatus.ENROLLED]:
            return "PAID"
        elif status == RegistrationStatus.PAYMENT_PENDING:
            return "PENDING"
        return "NOT_PAID"
    
    async def export_exam_registrations_to_csv(
        self,
        exam_id: UUID,
    ) -> str:
        """
        Export all registrations for an exam to CSV format.
        
        Args:
            exam_id: ID of the exam to export registrations for
        
        Returns:
            CSV content as string
        
        Raises:
            ExamNotFoundError: If exam not found
        """
        # Verify exam exists
        exam = await self.exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundError(f"Exam with id {exam_id} not found")
        
        # Get all registrations for the exam
        registrations = await self.registration_repository.get_by_exam_id(exam_id)
        
        # Build CSV rows
        csv_rows: List[CSVRegistrationRow] = []
        for registration in registrations:
            # Get user details
            user = await self.user_repository.get_by_id(registration.user_id)
            if not user:
                continue  # Skip if user not found
            
            # Derive statuses
            enrollment_status = self._derive_enrollment_status(registration.status)
            payment_status = self._derive_payment_status(registration.status)
            
            # Determine paid_at and enrolled_at
            paid_at = None
            enrolled_at = None
            
            if registration.status in [RegistrationStatus.PAID, RegistrationStatus.ENROLLED]:
                # For simplicity, use created_at as paid_at if status is PAID or ENROLLED
                # In a real system, you'd track payment timestamps separately
                paid_at = registration.created_at
            
            if registration.status == RegistrationStatus.ENROLLED:
                # For simplicity, use created_at as enrolled_at
                # In a real system, you'd track enrollment timestamps separately
                enrolled_at = registration.created_at
            
            csv_row = CSVRegistrationRow(
                registration_id=registration.id,
                user_id=user.id,
                user_name=user.name,
                email=user.email,
                mobile=user.mobile,
                registration_status=registration.status.value,
                enrollment_status=enrollment_status,
                payment_status=payment_status,
                paid_at=paid_at,
                enrolled_at=enrolled_at,
                registered_at=registration.created_at,
            )
            csv_rows.append(csv_row)
        
        # Generate CSV content
        return self._generate_csv(csv_rows)
    
    def _generate_csv(self, rows: List[CSVRegistrationRow]) -> str:
        """Generate CSV content from rows."""
        output = io.StringIO()
        
        # Define column order
        fieldnames = [
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
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in rows:
            writer.writerow({
                "registration_id": str(row.registration_id),
                "user_id": str(row.user_id),
                "user_name": row.user_name,
                "email": row.email,
                "mobile": row.mobile or "",
                "registration_status": row.registration_status,
                "enrollment_status": row.enrollment_status,
                "payment_status": row.payment_status,
                "paid_at": row.paid_at.isoformat() if row.paid_at else "",
                "enrolled_at": row.enrolled_at.isoformat() if row.enrolled_at else "",
                "registered_at": row.registered_at.isoformat(),
            })
        
        return output.getvalue()

