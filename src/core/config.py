from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str

    # Database
    database_url: str

    # Redis / Celery
    redis_url: str

    # Auth
    secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24

    # App
    env: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"

    # Media
    media_dir: str = "./media"

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_long(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_test(self) -> bool:
        return self.env == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
