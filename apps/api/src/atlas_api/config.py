from enum import Enum
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    ATLAS API Configuration.
    Values are loaded from environment variables prefixed with ATLAS_.
    """

    env: Environment = Environment.DEVELOPMENT
    debug: bool = False
    log_level: str = "INFO"

    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    cors_origins: List[str] = ["http://127.0.0.1:3000", "http://localhost:3000"]

    app_name: str = "ATLAS API"
    app_version: str = "0.1.0"

    slow_request_ms: int = 1000

    # Database Settings
    database_url: str = "postgresql+asyncpg://atlas:atlas@127.0.0.1:5432/atlas"
    test_database_url: str = "postgresql+asyncpg://atlas:atlas@127.0.0.1:5432/atlas_test"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 1800
    database_health_timeout: int = 3

    # Supabase Authentication
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwt_secret: str = ""

    # Redis Settings
    redis_url: str = "redis://127.0.0.1:6379"

    model_config = SettingsConfigDict(
        env_prefix="ATLAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
