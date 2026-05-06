from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.constants import UserRole


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class AdminCreateUserRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole
