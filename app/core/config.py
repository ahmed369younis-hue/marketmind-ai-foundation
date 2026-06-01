"""Minimal application settings for MarketMind AI."""

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    """Environment-backed application settings."""

    app_env: str = "development"
    app_name: str = "MarketMind AI"
    log_level: str = "INFO"


def get_settings() -> Settings:
    """Return settings from environment variables with safe defaults."""

    return Settings(
        app_env=getenv("APP_ENV", Settings.app_env),
        app_name=getenv("APP_NAME", Settings.app_name),
        log_level=getenv("LOG_LEVEL", Settings.log_level),
    )
