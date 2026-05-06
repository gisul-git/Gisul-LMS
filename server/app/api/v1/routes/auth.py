from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response, status

from app.api.v1.dependencies import (
    get_auth_service,
    get_current_user,
)
from app.core.config import get_settings
from app.core.constants import ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserPublic,
    VerifyEmailRequest,
)
from app.schemas.common import SuccessResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set HttpOnly secure cookies for tokens."""
    cookie_kwargs = {
        "httponly": True,
        "secure": settings.is_production,
        "samesite": "lax",
    }
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        **cookie_kwargs,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        **cookie_kwargs,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE)
    response.delete_cookie(REFRESH_TOKEN_COOKIE)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[UserPublic]:
    """Student self-registration. Sends verification email."""
    user = await auth_service.register_student(data)
    return SuccessResponse(
        message="Registration successful. Please check your email to verify your account.",
        data=UserPublic(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            email_verified=user.email_verified,
        ),
    )


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    """Verify email using token from email link."""
    await auth_service.verify_email(data.token)
    return SuccessResponse(message="Email verified successfully. You can now log in.")


@router.post("/login")
async def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    """Login with email and password. Returns tokens via HttpOnly cookies."""
    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    access_token, refresh_token, user = await auth_service.login(
        email=data.email,
        password=data.password,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    _set_auth_cookies(response, access_token, refresh_token)

    return LoginResponse(
        message="Login successful",
        user=UserPublic(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            email_verified=user.email_verified,
        ),
    )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_TOKEN_COOKIE)] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse[None]:
    """Refresh access token using refresh token from cookie."""
    from app.core.exceptions import UnauthorizedException

    if not refresh_token:
        raise UnauthorizedException("Refresh token missing")

    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    access_token, new_refresh, user = await auth_service.refresh_tokens(
        refresh_token, user_agent=user_agent, ip_address=ip_address
    )

    _set_auth_cookies(response, access_token, new_refresh)
    return SuccessResponse(message="Tokens refreshed successfully")


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_TOKEN_COOKIE)] = None,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> SuccessResponse[None]:
    """Logout and revoke refresh token."""
    await auth_service.logout(refresh_token, str(current_user.id))
    _clear_auth_cookies(response)
    return SuccessResponse(message="Logged out successfully")


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    """Request password reset. Always returns success to prevent email enumeration."""
    await auth_service.forgot_password(data.email)
    return SuccessResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> SuccessResponse[None]:
    """Reset password using token from email."""
    await auth_service.reset_password(data.token, data.new_password)
    return SuccessResponse(message="Password reset successfully. You can now log in.")


@router.get("/me")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> SuccessResponse[UserPublic]:
    """Get current authenticated user."""
    return SuccessResponse(
        message="User retrieved",
        data=UserPublic(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role,
            email_verified=current_user.email_verified,
        ),
    )
