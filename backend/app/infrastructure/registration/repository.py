from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ...domain.registration.entity import ExamRegistration
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

