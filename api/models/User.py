from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


# 1. Google OAuth soecific data (received from Google token/profile API)
class GoogleUserCreate(BaseModel):
    email: EmailStr
    nickname: str
    first_name: str
    last_name: str
    avatar: Optional[str] = None  # Google avatar URL
    google_id: str
    verified_email: bool = False


# 2. Used to validate new users before saving them to the database
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None


# 3. Used for responses back to the client (sanitized, includes DB identifiers)
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = (
            True  # this allows seamless conversion from ORM models to Pydantic models
        )
