from typing import List, Optional, Set
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument

from ...domain.registration.entity import ExamRegistration, RegistrationStatus
from ...domain.registration.exceptions import DuplicateRegistrationError, RegistrationNotFoundError
from ...domain.registration.repository import RegistrationRepository
from .mapper import RegistrationMapper


class MongoDBRegistrationRepository(RegistrationRepository):
    """MongoDB implementation of RegistrationRepository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.exam_registrations
    
    async def create(self, registration: ExamRegistration) -> ExamRegistration:
        """Create a new registration."""
        document = RegistrationMapper.to_document(registration)
        
        try:
            await self.collection.insert_one(document)
            return registration
        except DuplicateKeyError:
            # Translate MongoDB duplicate key error to domain exception
            raise DuplicateRegistrationError(
                f"User {registration.user_id} is already registered for exam {registration.exam_id}"
            )
    
    async def get_by_id(self, registration_id: UUID) -> Optional[ExamRegistration]:
        """Get registration by ID."""
        document = await self.collection.find_one({"id": str(registration_id)})
        
        if not document:
            return None
        
        return RegistrationMapper.to_entity(document)
    
    async def get_by_user_and_exam(
        self,
        user_id: UUID,
        exam_id: UUID,
    ) -> Optional[ExamRegistration]:
        """Get registration by user_id and exam_id."""
        document = await self.collection.find_one({
            "user_id": str(user_id),
            "exam_id": str(exam_id),
        })
        
        if not document:
            return None
        
        return RegistrationMapper.to_entity(document)
    
    async def get_by_user_id(self, user_id: UUID) -> List[ExamRegistration]:
        """Get all registrations for a user."""
        cursor = self.collection.find({"user_id": str(user_id)})
        documents = await cursor.to_list(length=None)
        return [RegistrationMapper.to_entity(doc) for doc in documents]
    
    async def get_by_exam_id(self, exam_id: UUID) -> List[ExamRegistration]:
        """Get all registrations for an exam."""
        cursor = self.collection.find({"exam_id": str(exam_id)})
        documents = await cursor.to_list(length=None)
        return [RegistrationMapper.to_entity(doc) for doc in documents]
    
    async def update_status(
        self,
        registration_id: UUID,
        new_status: RegistrationStatus,
        expected_status: Optional[RegistrationStatus] = None,
        expected_statuses: Optional[Set[RegistrationStatus]] = None,
    ) -> ExamRegistration:
        """
        Update registration status atomically.
        Uses MongoDB findOneAndUpdate for atomicity.
        
        Args:
            registration_id: ID of the registration
            new_status: The new status to set
            expected_status: If provided, only update if current status matches (single status)
            expected_statuses: If provided, only update if current status is in this set (multiple statuses)
        """
        # Build update query
        update_query = {"$set": {"status": new_status.value}}
        
        # Build filter with expected status check
        filter_query = {"id": str(registration_id)}
        if expected_status:
            filter_query["status"] = expected_status.value
        elif expected_statuses:
            filter_query["status"] = {"$in": [s.value for s in expected_statuses]}
        
        # Atomic update
        result = await self.collection.find_one_and_update(
            filter_query,
            update_query,
            return_document=ReturnDocument.AFTER,  # Return updated document
        )
        
        if not result:
            # Check if registration exists but with wrong status
            existing = await self.collection.find_one({"id": str(registration_id)})
            if existing:
                current_status = existing.get('status')
                if expected_status:
                    raise ValueError(
                        f"Cannot transition from {current_status} to {new_status.value}. "
                        f"Expected {expected_status.value}"
                    )
                elif expected_statuses:
                    raise ValueError(
                        f"Cannot transition from {current_status} to {new_status.value}. "
                        f"Expected one of: {', '.join(s.value for s in expected_statuses)}"
                    )
                else:
                    raise ValueError(
                        f"Cannot transition from {current_status} to {new_status.value}"
                    )
            raise RegistrationNotFoundError(f"Registration with id {registration_id} not found")
        
        return RegistrationMapper.to_entity(result)

