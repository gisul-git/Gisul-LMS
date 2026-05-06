from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "lms_db"

    # JWT — provide keys either inline or via file path (inline takes priority)
    jwt_private_key_content: Optional[str] = None   # paste PEM content directly
    jwt_public_key_content: Optional[str] = None    # paste PEM content directly
    jwt_private_key_path: Optional[str] = None      # fallback: path to .pem file
    jwt_public_key_path: Optional[str] = None       # fallback: path to .pem file
    jwt_algorithm: str = "RS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # SendGrid
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@yourdomain.com"
    sendgrid_from_name: str = "LMS Platform"

    # App
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Account lockout
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # Email verification
    email_verification_expire_hours: int = 24

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def jwt_private_key(self) -> str:
        if self.jwt_private_key_content:
            # Inline value: replace literal \n with real newlines
            return self.jwt_private_key_content.replace("\\n", "\n")
        if self.jwt_private_key_path:
            from pathlib import Path
            return Path(self.jwt_private_key_path).read_text()
        raise ValueError(
            "JWT private key not configured. Set JWT_PRIVATE_KEY_CONTENT or JWT_PRIVATE_KEY_PATH."
        )

    @property
    def jwt_public_key(self) -> str:
        if self.jwt_public_key_content:
            return self.jwt_public_key_content.replace("\\n", "\n")
        if self.jwt_public_key_path:
            from pathlib import Path
            return Path(self.jwt_public_key_path).read_text()
        raise ValueError(
            "JWT public key not configured. Set JWT_PUBLIC_KEY_CONTENT or JWT_PUBLIC_KEY_PATH."
        )

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
