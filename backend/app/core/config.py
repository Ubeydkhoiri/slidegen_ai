from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. All values come from env vars or a local `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://slidegen:slidegen@localhost:5432/slidegen"

    # LLM: any OpenAI-compatible endpoint. Model ids are never hardcoded.
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    # Auth
    session_secret: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None

    # Encrypts stored OAuth refresh tokens
    token_encryption_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
