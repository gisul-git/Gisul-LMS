from typing import Optional

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UpdateUserRequest

logger = get_logger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def get_by_id(self, user_id: str) -> User:
        user = await self._repo.find_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self._repo.find_by_email(email)

    async def update(self, user_id: str, data: UpdateUserRequest) -> User:
        user = await self.get_by_id(user_id)
        update_data = data.model_dump(exclude_none=True)
        if update_data:
            for field, value in update_data.items():
                setattr(user, field, value)
            await user.save()
        return user

    async def list_users(self, skip: int = 0, limit: int = 50) -> list[User]:
        return await self._repo.list_users(skip=skip, limit=limit)

    async def count(self) -> int:
        return await self._repo.count()
