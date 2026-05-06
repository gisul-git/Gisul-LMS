from typing import Annotated

from fastapi import Cookie, Depends, Request

from app.core.constants import ACCESS_TOKEN_COOKIE, UserRole
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.services.token_service import TokenService
from app.services.user_service import UserService


# ─── Repository / Service DI ──────────────────────────────────────────────────

def get_user_repository() -> UserRepository:
    return UserRepository()


def get_token_service() -> TokenService:
    return TokenService()


def get_email_service() -> EmailService:
    return EmailService()


def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
    email_service: Annotated[EmailService, Depends(get_email_service)],
) -> AuthService:
    return AuthService(user_repo, token_service, email_service)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repo)


# ─── Auth Guards ──────────────────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    access_token: Annotated[str | None, Cookie(alias=ACCESS_TOKEN_COOKIE)] = None,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Extract and validate the access token from HttpOnly cookie."""
    if not access_token:
        # Also check Authorization header for API clients
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header[7:]

    if not access_token:
        raise UnauthorizedException()

    payload = decode_access_token(access_token)
    user_id: str = payload.get("sub", "")

    user = await user_repo.find_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User account is inactive or not found")

    return user


async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.email_verified:
        from app.core.exceptions import EmailNotVerifiedException
        raise EmailNotVerifiedException()
    return current_user


# ─── Role Guards ──────────────────────────────────────────────────────────────

def require_role(*roles: UserRole):
    async def guard(
        current_user: Annotated[User, Depends(get_current_verified_user)],
    ) -> User:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Access restricted to: {', '.join(r.value for r in roles)}"
            )
        return current_user
    return guard


require_student = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN))
require_instructor = Depends(require_role(UserRole.INSTRUCTOR, UserRole.ADMIN))
require_admin = Depends(require_role(UserRole.ADMIN))
