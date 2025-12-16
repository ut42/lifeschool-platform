from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User:
    """Domain entity representing a user."""
    
    def __init__(
        self,
        email: str,
        name: str,
        id: Optional[UUID] = None,
        mobile: Optional[str] = None,
        role: UserRole = UserRole.USER,
        created_at: Optional[datetime] = None,
    ):
        if not email or not email.strip():
            raise ValueError("Email is required")
        if not name or not name.strip():
            raise ValueError("Name is required")
        
        self.id = id or uuid4()
        self.email = email.strip().lower()
        self.name = name.strip()
        self.mobile = mobile
        self.role = role
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def update_mobile(self, mobile: str) -> None:
        """Update mobile number with validation."""
        if not mobile or not mobile.strip():
            raise ValueError("Mobile number is required")
        
        mobile_clean = mobile.strip().replace(" ", "").replace("-", "")
        
        if not mobile_clean.isdigit():
            raise ValueError("Mobile number must contain only digits")
        
        if len(mobile_clean) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        
        self.mobile = mobile_clean
    
    @property
    def is_profile_complete(self) -> bool:
        """Check if user profile is complete (has mobile number)."""
        return self.mobile is not None and len(self.mobile) == 10
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __repr__(self):
        return f"<User id={self.id} email={self.email} name={self.name}>"

