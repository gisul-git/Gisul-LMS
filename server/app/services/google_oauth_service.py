import secrets
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_SCOPES = "openid email profile"


class GoogleOAuthService:
    def build_authorization_url(self, state: str) -> str:
        """Build the Google OAuth consent screen URL."""
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_SCOPES,
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_profile(
        self, code: str
    ) -> Optional[dict]:
        """
        Exchange authorization code for tokens, then fetch user profile.
        Returns dict with: google_id, email, full_name
        Returns None on any failure.
        """
        try:
            tokens = await self._exchange_code(code)
            if not tokens:
                return None
            return await self._fetch_userinfo(tokens["access_token"])
        except Exception as exc:
            logger.error("google_oauth_exchange_failed", error=str(exc))
            return None

    async def _exchange_code(self, code: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            if resp.status_code != 200:
                logger.error("google_token_exchange_failed", status=resp.status_code)
                return None
            return resp.json()

    async def _fetch_userinfo(self, access_token: str) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            if resp.status_code != 200:
                logger.error("google_userinfo_failed", status=resp.status_code)
                return None
            data = resp.json()
            return {
                "google_id": data.get("sub"),
                "email": data.get("email", "").lower(),
                "full_name": data.get("name", ""),
                "email_verified": data.get("email_verified", False),
            }
