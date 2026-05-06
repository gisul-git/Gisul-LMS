from datetime import datetime, timedelta, timezone

from beanie import Document, Indexed
from pymongo import ASCENDING
from pymongo.operations import IndexModel
from pydantic import Field

from app.core.config import get_settings

settings = get_settings()


class EmailVerification(Document):
    user_id: Indexed(str)  # type: ignore[valid-type]
    token_hash: Indexed(str, unique=True)  # type: ignore[valid-type]
    is_used: bool = False
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(hours=settings.email_verification_expire_hours)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "email_verifications"
        indexes = [
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0),
        ]

    def is_expired(self) -> bool:
        expires = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        return datetime.now(timezone.utc) > expires

    def is_valid(self) -> bool:
        return not self.is_used and not self.is_expired()
