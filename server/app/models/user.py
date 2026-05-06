from datetime import datetime, timezone
from typing import Optional

from beanie import Document, Indexed
from pydantic import EmailStr, Field

from app.core.constants import AuthProvider, UserRole, VerificationStatus


class User(Document):
    email: Indexed(EmailStr, unique=True)  # type: ignore[valid-type]
    hashed_password: Optional[str] = None  # None for OAuth-only accounts
    full_name: str
    auth_provider: AuthProvider = AuthProvider.LOCAL
    google_id: Optional[str] = None
    role: UserRole = UserRole.STUDENT
    is_active: bool = True
    email_verified: bool = False
    verification_status: VerificationStatus = VerificationStatus.PENDING

    # Account lockout
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None

    class Settings:
        name = "users"
        indexes = [
            "email",
            "role",
            "google_id",
        ]

    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        locked = self.locked_until.replace(tzinfo=timezone.utc) if self.locked_until.tzinfo is None else self.locked_until
        return datetime.now(timezone.utc) < locked

    def to_safe_dict(self) -> dict:
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
