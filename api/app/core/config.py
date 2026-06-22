"""Application settings loaded from environment / .env."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration. All secrets come from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # Supabase / Auth
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_jwks_url: str = ""
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "authenticated"

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

    # AI
    anthropic_api_key: str = ""
    llm_model_chat: str = "claude-sonnet-4-6"
    llm_model_plan: str = "claude-opus-4-8"

    # Queue / Email / Payments
    redis_url: str = "redis://localhost:6379"
    resend_api_key: str = ""
    email_from: str = "Endurance Coach <coach@endurancecoach.app>"
    paddle_api_key: str = ""
    paddle_webhook_secret: str = ""
    paddle_client_token: str = ""
    paddle_price_id: str = ""
    paddle_environment: str = "sandbox"

    # Security
    encryption_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
