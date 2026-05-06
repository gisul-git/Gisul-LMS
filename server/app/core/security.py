import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.constants import TokenType
from app.core.exceptions import InvalidTokenException, TokenExpiredException
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Argon2 password hashing context
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,   # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=4,
)


# ─── Password ─────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── Tokens ───────────────────────────────────────────────────────────────────

def create_access_token(subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": TokenType.ACCESS,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_urlsafe(16),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_private_key, algorithm=settings.jwt_algorithm)


def create_refresh_token() -> tuple[str, str]:
    """Return (raw_token, hashed_token). Store only the hash."""
    raw = secrets.token_urlsafe(64)
    hashed = hash_token(raw)
    return raw, hashed


def hash_token(token: str) -> str:
    """SHA-256 hash a token for safe storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_public_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != TokenType.ACCESS:
            raise InvalidTokenException("Invalid token type")
        return payload
    except JWTError as exc:
        msg = str(exc)
        if "expired" in msg.lower():
            raise TokenExpiredException()
        raise InvalidTokenException() from exc


def generate_verification_token() -> tuple[str, str]:
    """Return (raw_token, hashed_token) for email verification."""
    raw = secrets.token_urlsafe(32)
    hashed = hash_token(raw)
    return raw, hashed
