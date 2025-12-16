from datetime import datetime, timezone
from typing import List
from uuid import UUID

from ...domain.registration.repository import RegistrationRepository
from ...domain.registration.entity import RegistrationStatus
from ...domain.registration.exceptions import RegistrationNotFoundError
from ...domain.user.entity import UserRole
from .dto import EnrollmentResponse, BulkEnrollmentResponse, FailedEnrollmentItem


class EnrollmentService:
    """Service for handling enrollment operations."""
    
    # Valid statuses that can be enrolled
    ENROLLABLE_STATUSES = {
        RegistrationStatus.PAID,
        RegistrationStatus.REGISTERED,
        RegistrationStatus.PAYMENT_PENDING,
    }
    
    def __init__(
        self,
        registration_repository: RegistrationRepository,
    ):
        self.registration_repository = registration_repository
    
    async def enroll_registration(
        self,
        registration_id: UUID,
        admin_id: UUID,
        admin_role: UserRole,
    ) -> dict:
        """
        Enroll a single registration.
        Transitions status from PAID/REGISTERED/PAYMENT_PENDING to ENROLLED.
        
        Args:
            registration_id: ID of the registration to enroll
            admin_id: ID of the admin performing the enrollment
            admin_role: Role of the user performing the enrollment
        
        Returns:
            Dictionary with enrollment details
        
        Raises:
            PermissionError: If user is not ADMIN
            RegistrationNotFoundError: If registration not found
            ValueError: If registration is already ENROLLED or in invalid status
        """
        if admin_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can enroll registrations")
        
        registration = await self.registration_repository.get_by_id(registration_id)
        if not registration:
            raise RegistrationNotFoundError(f"Registration {registration_id} not found")
        
        # Check if already enrolled
        if registration.status == RegistrationStatus.ENROLLED:
            raise ValueError(
                f"Registration {registration_id} is already ENROLLED"
            )
        
        # Check if status is enrollable
        if registration.status not in self.ENROLLABLE_STATUSES:
            raise ValueError(
                f"Cannot enroll registration in {registration.status.value} status. "
                f"Must be one of: {', '.join(s.value for s in self.ENROLLABLE_STATUSES)}"
            )
        
        # Perform atomic status update
        # We allow enrollment from any of the enrollable statuses
        updated_registration = await self.registration_repository.update_status(
            registration_id,
            RegistrationStatus.ENROLLED,
            expected_statuses=self.ENROLLABLE_STATUSES,
        )
        
        return {
            "registration_id": updated_registration.id,
            "status": updated_registration.status,
            "enrolled_at": datetime.now(timezone.utc),
        }
    
    async def bulk_enroll_registrations(
        self,
        registration_ids: List[UUID],
        admin_id: UUID,
        admin_role: UserRole,
    ) -> BulkEnrollmentResponse:
        """
        Bulk enroll multiple registrations.
        Allows partial success - some registrations may fail while others succeed.
        
        Args:
            registration_ids: List of registration IDs to enroll
            admin_id: ID of the admin performing the enrollment
            admin_role: Role of the user performing the enrollment
        
        Returns:
            BulkEnrollmentResponse with success and failed lists
        
        Raises:
            PermissionError: If user is not ADMIN
        """
        if admin_role != UserRole.ADMIN:
            raise PermissionError("Only ADMIN can bulk enroll registrations")
        
        success_ids: List[UUID] = []
        failed_items: List[FailedEnrollmentItem] = []
        
        for registration_id in registration_ids:
            try:
                # Try to enroll this registration
                await self.enroll_registration(registration_id, admin_id, admin_role)
                success_ids.append(registration_id)
            except RegistrationNotFoundError as e:
                failed_items.append(
                    FailedEnrollmentItem(
                        registration_id=registration_id,
                        reason=f"Registration not found: {str(e)}"
                    )
                )
            except ValueError as e:
                # Already enrolled or invalid status
                failed_items.append(
                    FailedEnrollmentItem(
                        registration_id=registration_id,
                        reason=str(e)
                    )
                )
            except Exception as e:
                # Catch any other unexpected errors
                failed_items.append(
                    FailedEnrollmentItem(
                        registration_id=registration_id,
                        reason=f"Unexpected error: {str(e)}"
                    )
                )
        
        return BulkEnrollmentResponse(
            success=success_ids,
            failed=failed_items,
        )

