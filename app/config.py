"""
Configuration module – loads and validates environment variables.

Uses pydantic-settings to ensure all required values are present
at startup rather than failing at call time.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings sourced from .env / environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Azure OpenAI ──────────────────────────────────────────
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_deployment: str = "gpt-4o"

    # ── App ───────────────────────────────────────────────────
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    log_level: str = "INFO"
    rate_limit_per_minute: int = 30

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated origins into a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Singleton-cached settings instance."""
    return Settings()  # type: ignore[call-arg]
