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

    model_config = SettingsConfigDict(
        env_prefix="ATLAS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
