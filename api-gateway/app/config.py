from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    gateway_port: int = 8080
    allowed_origins: str = "http://localhost:3000"
    rate_limit_requests: int = 100
    environment: str = "development"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()
