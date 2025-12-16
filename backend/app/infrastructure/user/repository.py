from typing import Optional
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ...domain.user.entity import User
from ...domain.user.exceptions import UserAlreadyExistsError, UserNotFoundError
from ...domain.user.repository import UserRepository
from .mapper import UserMapper


class MongoDBUserRepository(UserRepository):
    """MongoDB implementation of UserRepository."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        document = UserMapper.to_document(user)
        
        try:
            await self.collection.insert_one(document)
            return user
        except DuplicateKeyError:
            raise UserAlreadyExistsError(f"User with email {user.email} already exists")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        document = await self.collection.find_one({"id": str(user_id)})
        
        if not document:
            return None
        
        return UserMapper.to_entity(document)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        document = await self.collection.find_one({"email": email.lower()})
        
        if not document:
            return None
        
        return UserMapper.to_entity(document)
    
    async def update(self, user: User) -> User:
        """Update an existing user."""
        document = UserMapper.to_document(user)
        
        # Remove _id from update document (MongoDB doesn't allow updating _id)
        update_doc = {k: v for k, v in document.items() if k != "_id"}
        
        result = await self.collection.update_one(
            {"id": str(user.id)},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise UserNotFoundError(f"User with id {user.id} not found")
        
        return user

