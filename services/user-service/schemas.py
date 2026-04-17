from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from models import UserRole


class UserProfileCreate(BaseModel):
    auth_user_id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    tc_no: Optional[str] = None
    date_of_birth: Optional[str] = None
    role: UserRole = UserRole.user


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    tc_no: Optional[str] = None
    date_of_birth: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: UUID
    auth_user_id: UUID
    email: str
    full_name: str
    phone: Optional[str]
    tc_no: Optional[str]
    date_of_birth: Optional[str]
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
