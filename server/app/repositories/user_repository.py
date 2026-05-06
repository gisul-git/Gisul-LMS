from datetime import datetime, timezone
from typing import Optional

from beanie.operators import Set

from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    async def find_by_email(self, email: str) -> Optional[User]:
        return await User.find_one(User.email == email.lower())

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return await User.get(user_id)

    async def create(self, user: User) -> User:
        user.email = user.email.lower()
        await user.insert()
        logger.info("user_created", user_id=str(user.id), role=user.role)
        return user

    async def update_last_login(self, user: User) -> None:
        await user.update(Set({User.last_login_at: datetime.now(timezone.utc)}))

    async def increment_failed_attempts(self, user: User) -> None:
        await user.update(
            Set({User.failed_login_attempts: user.failed_login_attempts + 1})
        )

    async def lock_account(self, user: User, until: datetime) -> None:
        await user.update(Set({User.locked_until: until}))
        logger.warning("account_locked", user_id=str(user.id), until=until.isoformat())

    async def reset_failed_attempts(self, user: User) -> None:
        await user.update(
            Set({
                User.failed_login_attempts: 0,
                User.locked_until: None,
            })
        )

    async def mark_email_verified(self, user: User) -> None:
        from app.core.constants import VerificationStatus
        await user.update(
            Set({
                User.email_verified: True,
                User.verification_status: VerificationStatus.VERIFIED,
                User.updated_at: datetime.now(timezone.utc),
            })
        )

    async def update_password(self, user: User, hashed_password: str) -> None:
        await user.update(
            Set({
                User.hashed_password: hashed_password,
                User.updated_at: datetime.now(timezone.utc),
            })
        )

    async def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        return await User.find_all().skip(skip).limit(limit).to_list()

    async def list_by_role(self, role: str, skip: int = 0, limit: int = 200) -> list[User]:
        return await User.find(User.role == role).skip(skip).limit(limit).to_list()

    async def count(self) -> int:
        return await User.count()
