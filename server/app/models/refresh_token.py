from datetime import datetime, timezone
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class RefreshToken(Document):
    user_id: Indexed(str)  # type: ignore[valid-type]
    token_hash: Indexed(str, unique=True)  # type: ignore[valid-type]  # SHA-256 of raw token
    is_revoked: bool = False
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replaced_by: Optional[str] = None  # hash of the new token (rotation audit trail)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

    class Settings:
        name = "refresh_tokens"
        indexes = [
            "user_id",
            "token_hash",
            [("expires_at", 1)],  # TTL handled in application layer; index for queries
        ]

    def is_expired(self) -> bool:
        expires = self.expires_at.replace(tzinfo=timezone.utc) if self.expires_at.tzinfo is None else self.expires_at
        return datetime.now(timezone.utc) > expires

    def is_valid(self) -> bool:
        return not self.is_revoked and not self.is_expired()
