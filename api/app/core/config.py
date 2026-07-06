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
    log_level: str = "INFO"

    # Supabase / Auth — the JWKS URL is derived from supabase_url (deps.py).
    supabase_url: str = ""
    supabase_jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_audience: str = "authenticated"

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

    # AI
    openai_api_key: str = ""
    llm_model_chat: str = "gpt-4o-mini"
    llm_model_plan: str = "gpt-4o"
    # When on, the coach chat can call tools to pull deterministic facts.
    coach_tools_enabled: bool = True

    # Queue / Email / Payments
    redis_url: str = "redis://localhost:6379"
    resend_api_key: str = ""
    email_from: str = "Endurance Coach <coach@endurancecoach.app>"
    paddle_api_key: str = ""
    paddle_webhook_secret: str = ""
    paddle_client_token: str = ""
    paddle_price_id: str = ""
    paddle_price_id_annual: str = ""
    paddle_environment: str = "sandbox"

    # Monitoring (S9) — Sentry is a no-op until a DSN is provided.
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # Security
    encryption_key: str = ""
    # Per-user sliding-window rate limits (in-process; see core/ratelimit.py)
    rate_limit_enabled: bool = True
    rate_limit_chat_per_min: int = 20
    rate_limit_garmin_per_5min: int = 5
    rate_limit_plans_per_hour: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
