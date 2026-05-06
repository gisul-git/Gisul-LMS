import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Request, Response
from fastapi.responses import RedirectResponse

from app.api.v1.dependencies import get_auth_service
from app.core.config import get_settings
from app.core.constants import ACCESS_TOKEN_COOKIE, REFRESH_TOKEN_COOKIE
from app.core.exceptions import OAuthLoginForbiddenException
from app.core.logging import get_logger
from app.services.auth_service import AuthService
from app.services.google_oauth_service import GoogleOAuthService

router = APIRouter(prefix="/auth", tags=["OAuth"])
settings = get_settings()
logger = get_logger(__name__)

OAUTH_STATE_COOKIE = "oauth_state"


def _get_google_service() -> GoogleOAuthService:
    return GoogleOAuthService()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
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


@router.get("/google")
async def google_login(
    google_service: Annotated[GoogleOAuthService, Depends(_get_google_service)],
) -> RedirectResponse:
    """Redirect user to Google OAuth consent screen."""
    state = secrets.token_urlsafe(32)
    url = google_service.build_authorization_url(state=state)

    response = RedirectResponse(url=url)
    # Store state in short-lived cookie for CSRF validation
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        max_age=600,  # 10 minutes
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    oauth_state: Annotated[str | None, Cookie(alias=OAUTH_STATE_COOKIE)] = None,
    auth_service: AuthService = Depends(get_auth_service),
    google_service: GoogleOAuthService = Depends(_get_google_service),
) -> RedirectResponse:
    """Handle Google OAuth callback."""
    frontend_url = settings.frontend_url
    error_redirect = f"{frontend_url}/login?error=login_failed"

    # Google returned an error
    if error:
        logger.warning("google_oauth_error_returned", error=error)
        return RedirectResponse(url=error_redirect)

    # Validate CSRF state
    if not state or not oauth_state or state != oauth_state:
        logger.warning("google_oauth_state_mismatch")
        return RedirectResponse(url=error_redirect)

    if not code:
        return RedirectResponse(url=error_redirect)

    # Exchange code for user profile
    profile = await google_service.exchange_code_for_profile(code)
    if not profile or not profile.get("email"):
        return RedirectResponse(url=error_redirect)

    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None

    try:
        access_token, refresh_token, user = await auth_service.google_oauth_login(
            google_id=profile["google_id"],
            email=profile["email"],
            full_name=profile["full_name"],
            email_verified=profile.get("email_verified", False),
            user_agent=user_agent,
            ip_address=ip_address,
        )
    except OAuthLoginForbiddenException:
        return RedirectResponse(url=error_redirect)
    except Exception as exc:
        logger.error("google_oauth_login_error", error=str(exc))
        return RedirectResponse(url=error_redirect)

    # Success — set cookies and redirect to student dashboard
    success_redirect = f"{frontend_url}/student-dashboard"
    response = RedirectResponse(url=success_redirect)
    _set_auth_cookies(response, access_token, refresh_token)

    # Clear the state cookie
    response.delete_cookie(OAUTH_STATE_COOKIE)

    return response
