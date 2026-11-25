from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. Values come from environment variables (see .env.example)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot"
    cors_origins: list[str] = []

    # Market data provider. Limits match the Tiingo Starter plan; change them here, not in code.
    tiingo_api_key: SecretStr | None = None
    tiingo_base_url: str = "https://api.tiingo.com"
    tiingo_max_requests_per_hour: int = 50
    tiingo_max_requests_per_day: int = 1000
    tiingo_max_symbols_per_month: int = 500
    tiingo_max_bytes_per_month: int = 1_000_000_000

    @field_validator("tiingo_api_key", mode="before")
    @classmethod
    def _blank_key_is_unset(cls, value: object) -> object:
        return None if value == "" else value


@lru_cache
def get_settings() -> Settings:
    return Settings()
