from datetime import datetime, timedelta, timezone
from typing import Optional

from beanie.operators import Set

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import create_refresh_token, hash_token
from app.models.refresh_token import RefreshToken

logger = get_logger(__name__)
settings = get_settings()


class TokenService:
    async def create_refresh_token(
        self,
        user_id: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> str:
        """Create, persist, and return the raw refresh token."""
        raw, hashed = create_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        token = RefreshToken(
            user_id=user_id,
            token_hash=hashed,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await token.insert()
        logger.info("refresh_token_created", user_id=user_id)
        return raw

    async def rotate_refresh_token(
        self,
        raw_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Validate old token, revoke it, issue new one.
        Returns (new_raw_token, user_id).
        Raises on invalid/expired/revoked token.
        """
        from app.core.exceptions import InvalidTokenException

        token_hash = hash_token(raw_token)
        stored = await RefreshToken.find_one(RefreshToken.token_hash == token_hash)

        if not stored or not stored.is_valid():
            # Possible token reuse attack — revoke all tokens for this user
            if stored:
                await self._revoke_all_for_user(stored.user_id)
                logger.warning(
                    "refresh_token_reuse_detected", user_id=stored.user_id
                )
            raise InvalidTokenException("Refresh token is invalid or expired")

        # Revoke old token
        new_raw, new_hash = create_refresh_token()
        await stored.update(
            Set({
                RefreshToken.is_revoked: True,
                RefreshToken.replaced_by: new_hash,
            })
        )

        # Issue new token
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        new_token = RefreshToken(
            user_id=stored.user_id,
            token_hash=new_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        await new_token.insert()
        logger.info("refresh_token_rotated", user_id=stored.user_id)
        return new_raw, stored.user_id

    async def revoke_token(self, raw_token: str) -> None:
        token_hash = hash_token(raw_token)
        stored = await RefreshToken.find_one(RefreshToken.token_hash == token_hash)
        if stored:
            await stored.update(Set({RefreshToken.is_revoked: True}))
            logger.info("refresh_token_revoked", user_id=stored.user_id)

    async def revoke_all_for_user(self, user_id: str) -> None:
        await self._revoke_all_for_user(user_id)

    async def _revoke_all_for_user(self, user_id: str) -> None:
        result = await RefreshToken.find(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,  # noqa: E712
        ).update(Set({RefreshToken.is_revoked: True}))
        logger.info("all_refresh_tokens_revoked", user_id=user_id)
