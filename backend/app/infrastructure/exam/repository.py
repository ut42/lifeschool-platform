from typing import List, Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase

from ...domain.exam.entity import Exam, ExamStatus
from ...domain.exam.exceptions import ExamNotFoundError
from ...domain.exam.repository import ExamRepository
from .mapper import ExamMapper


class MongoDBExamRepository(ExamRepository):
    """MongoDB implementation of ExamRepository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.exams
    
    async def create(self, exam: Exam) -> Exam:
        """Create a new exam."""
        document = ExamMapper.to_document(exam)
        await self.collection.insert_one(document)
        return exam
    
    async def get_by_id(self, exam_id: UUID) -> Optional[Exam]:
        """Get exam by ID."""
        document = await self.collection.find_one({"id": str(exam_id)})
        
        if not document:
            return None
        
        return ExamMapper.to_entity(document)
    
    async def get_all(self) -> List[Exam]:
        """Get all exams."""
        cursor = self.collection.find({})
        documents = await cursor.to_list(length=None)
        return [ExamMapper.to_entity(doc) for doc in documents]
    
    async def get_active(self) -> List[Exam]:
        """Get all active exams."""
        cursor = self.collection.find({"status": ExamStatus.ACTIVE.value})
        documents = await cursor.to_list(length=None)
        return [ExamMapper.to_entity(doc) for doc in documents]
    
    async def update(self, exam: Exam) -> Exam:
        """Update an existing exam."""
        document = ExamMapper.to_document(exam)
        
        # Remove _id from update document (MongoDB doesn't allow updating _id)
        update_doc = {k: v for k, v in document.items() if k != "_id"}
        
        result = await self.collection.update_one(
            {"id": str(exam.id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise ExamNotFoundError(f"Exam with id {exam.id} not found")
        
        return exam

