from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .errors import DatabaseConfigurationError


def redact_database_url(url: str) -> str:
    """Redacts the password from a database connection string for logging."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if parsed.password:
            # Reconstruct the URL without the password
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            parsed = parsed._replace(netloc=netloc)
        return urlunparse(parsed)
    except Exception:
        return "postgresql+asyncpg://***:***@***"


def normalize_database_url(url: str) -> str:
    """
    Normalizes generic database URLs to use the asyncpg driver.
    Changes postgresql:// or postgres:// to postgresql+asyncpg://
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine(
    url: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_timeout: int = 30,
    pool_recycle: int = 1800,
    application_name: str = "atlas",
) -> AsyncEngine:
    """
    Creates an asynchronous SQLAlchemy engine.
    """
    if not url:
        raise DatabaseConfigurationError("Database URL is required.")

    normalized_url = normalize_database_url(url)

    # Configure connection arguments
    connect_args = {}
    if application_name:
        connect_args["server_settings"] = {"application_name": application_name, "timezone": "UTC"}

    return create_async_engine(
        normalized_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
