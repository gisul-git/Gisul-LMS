from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global _client
    from app.models.user import User
    from app.models.refresh_token import RefreshToken
    from app.models.email_verification import EmailVerification
    from app.models.password_reset import PasswordReset

    _client = AsyncIOMotorClient(settings.mongo_uri)
    await init_beanie(
        database=_client[settings.mongo_db_name],
        document_models=[User, RefreshToken, EmailVerification, PasswordReset],
    )
    logger.info("database_connected", db=settings.mongo_db_name)


async def disconnect_db() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("database_disconnected")


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("Database not initialised")
    return _client
