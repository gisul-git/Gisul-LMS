from datetime import datetime, timedelta, timezone
from typing import Optional

from beanie.operators import Set

from app.core.config import get_settings
from app.core.constants import UserRole
from app.core.exceptions import (
    AccountLockedException,
    EmailNotVerifiedException,
    InvalidCredentialsException,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    generate_verification_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest
from app.services.email_service import EmailService
from app.services.token_service import TokenService

logger = get_logger(__name__)
settings = get_settings()


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_service: TokenService,
        email_service: EmailService,
    ) -> None:
        self._user_repo = user_repo
        self._token_service = token_service
        self._email_service = email_service

    # ─── Registration ─────────────────────────────────────────────────────────

    async def register_student(self, data: RegisterRequest) -> User:
        """Only students can self-register."""
        # Check uniqueness — generic error to avoid email enumeration
        existing = await self._user_repo.find_by_email(data.email)
        if existing:
            # Silently succeed to prevent email enumeration
            logger.info("register_duplicate_email", email=data.email)
            return existing  # caller should not reveal this

        user = User(
            email=data.email.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=UserRole.STUDENT,
            email_verified=False,
        )
        await self._user_repo.create(user)

        # Send verification email
        raw_token, token_hash = generate_verification_token()
        verification = EmailVerification(
            user_id=str(user.id),
            token_hash=token_hash,
        )
        await verification.insert()

        await self._email_service.send_verification_email(
            to_email=user.email,
            full_name=user.full_name,
            token=raw_token,
        )
        logger.info("student_registered", user_id=str(user.id))
        return user

    # ─── Email Verification ───────────────────────────────────────────────────

    async def verify_email(self, raw_token: str) -> User:
        from app.core.exceptions import InvalidTokenException

        token_hash = hash_token(raw_token)
        record = await EmailVerification.find_one(
            EmailVerification.token_hash == token_hash
        )

        if not record or not record.is_valid():
            raise InvalidTokenException("Verification link is invalid or has expired")

        user = await self._user_repo.find_by_id(record.user_id)
        if not user:
            raise InvalidTokenException("User not found")

        # Mark token as used (one-time use)
        await record.update(Set({EmailVerification.is_used: True}))
        await self._user_repo.mark_email_verified(user)

        logger.info("email_verified", user_id=str(user.id))
        return user

    # ─── Login ────────────────────────────────────────────────────────────────

    async def login(
        self,
        email: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[str, str, User]:
        """
        Returns (access_token, raw_refresh_token, user).
        Raises on any auth failure with generic messages.
        """
        user = await self._user_repo.find_by_email(email.lower())

        # Generic error — never reveal whether email exists
        if not user:
            raise InvalidCredentialsException()

        # Check lockout before password verification
        if user.is_locked():
            raise AccountLockedException(
                f"Account locked. Try again after {settings.lockout_duration_minutes} minutes."
            )

        if not verify_password(password, user.hashed_password):
            await self._handle_failed_attempt(user)
            raise InvalidCredentialsException()

        if not user.email_verified:
            raise EmailNotVerifiedException()

        if not user.is_active:
            raise InvalidCredentialsException()

        # Successful login — reset counters
        await self._user_repo.reset_failed_attempts(user)
        await self._user_repo.update_last_login(user)

        access_token = create_access_token(subject=str(user.id), role=user.role)
        refresh_token = await self._token_service.create_refresh_token(
            user_id=str(user.id),
            user_agent=user_agent,
            ip_address=ip_address,
        )

        logger.info("user_logged_in", user_id=str(user.id), role=user.role)
        return access_token, refresh_token, user

    async def _handle_failed_attempt(self, user: User) -> None:
        new_count = user.failed_login_attempts + 1
        await self._user_repo.increment_failed_attempts(user)

        if new_count >= settings.max_login_attempts:
            locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=settings.lockout_duration_minutes
            )
            await self._user_repo.lock_account(user, locked_until)
            logger.warning(
                "account_locked_after_attempts",
                user_id=str(user.id),
                attempts=new_count,
            )

    # ─── Refresh ──────────────────────────────────────────────────────────────

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[str, str, User]:
        new_raw, user_id = await self._token_service.rotate_refresh_token(
            raw_refresh_token, user_agent=user_agent, ip_address=ip_address
        )
        user = await self._user_repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise InvalidCredentialsException()

        access_token = create_access_token(subject=user_id, role=user.role)
        return access_token, new_raw, user

    # ─── Logout ───────────────────────────────────────────────────────────────

    async def logout(self, raw_refresh_token: Optional[str], user_id: str) -> None:
        if raw_refresh_token:
            await self._token_service.revoke_token(raw_refresh_token)
        logger.info("user_logged_out", user_id=user_id)

    # ─── Forgot / Reset Password ──────────────────────────────────────────────

    async def forgot_password(self, email: str) -> None:
        """Always returns success to prevent email enumeration."""
        user = await self._user_repo.find_by_email(email.lower())
        if not user:
            return  # Silent — don't reveal email existence

        raw_token, token_hash = generate_verification_token()
        reset = PasswordReset(user_id=str(user.id), token_hash=token_hash)
        await reset.insert()

        await self._email_service.send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name,
            token=raw_token,
        )
        logger.info("password_reset_requested", user_id=str(user.id))

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        from app.core.exceptions import InvalidTokenException

        token_hash = hash_token(raw_token)
        record = await PasswordReset.find_one(PasswordReset.token_hash == token_hash)

        if not record or not record.is_valid():
            raise InvalidTokenException("Reset link is invalid or has expired")

        user = await self._user_repo.find_by_id(record.user_id)
        if not user:
            raise InvalidTokenException("User not found")

        await record.update(Set({PasswordReset.is_used: True}))
        await self._user_repo.update_password(user, hash_password(new_password))

        # Revoke all refresh tokens on password change
        await self._token_service.revoke_all_for_user(str(user.id))
        logger.info("password_reset_completed", user_id=str(user.id))
