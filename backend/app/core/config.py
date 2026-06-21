from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"

    # Database
    database_url: str = "postgresql+asyncpg://trustscanner:password@db:5432/trustscanner"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Security
    secret_key: str = "change-me-in-production"

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]

    # Scan limits
    scan_timeout_seconds: int = 8
    scan_max_redirects: int = 5
    scan_max_response_size_mb: int = 2

    # Rate limits
    rate_limit_guest_per_hour: int = 3
    rate_limit_free_user_per_day: int = 10

    # Reputation
    reputation_provider: str = "mock"
    google_safe_browsing_api_key: str = ""
    virustotal_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
