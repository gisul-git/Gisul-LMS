import re
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.core.constants import PASSWORD_REGEX


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name must be between 2 and 100 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "Password must be at least 8 characters and contain uppercase, "
                "lowercase, number, and special character"
            )
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """Used when refresh token is sent in body (fallback). Prefer cookie."""
    refresh_token: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.match(PASSWORD_REGEX, v):
            raise ValueError(
                "Password must be at least 8 characters and contain uppercase, "
                "lowercase, number, and special character"
            )
        return v


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    # access_token intentionally omitted from body — set via HttpOnly cookie


class LoginResponse(BaseModel):
    message: str
    user: "UserPublic"
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    email_verified: bool
