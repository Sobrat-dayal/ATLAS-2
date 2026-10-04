import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from .engine import create_engine, redact_database_url
from .session import create_session_factory
from .errors import DatabaseConfigurationError

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        self.is_initialized = False

    def initialize(
        self,
        url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        application_name: str = "atlas",
    ) -> None:
        if self.is_initialized:
            logger.warning("DatabaseManager is already initialized.")
            return

        redacted_url = redact_database_url(url)
        logger.info(f"Initializing database manager with URL: {redacted_url}")

        try:
            self.engine = create_engine(
                url=url,
                echo=echo,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                application_name=application_name,
            )
            self.session_factory = create_session_factory(self.engine)
            self.is_initialized = True
            logger.info("Database engine initialized successfully.")
        except Exception as e:
            logger.error("Failed to initialize database engine.", exc_info=True)
            raise DatabaseConfigurationError("Failed to initialize database engine.") from e

    async def dispose(self) -> None:
        """Disposes the engine pool."""
        if not self.is_initialized or self.engine is None:
            return
        
        logger.info("Disposing database engine...")
        await self.engine.dispose()
        self.is_initialized = False
        logger.info("Database engine disposed.")

    async def check_connectivity(self, timeout: float = 3.0) -> bool:
        """Checks if the database is reachable by executing SELECT 1."""
        if not self.is_initialized or self.engine is None:
            return False
            
        try:
            async with self.engine.connect() as conn:
                # Use a timeout context if needed, but for now we just try a lightweight query
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.warning(f"Database connectivity check failed: {e}")
            return False

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency provider for an async database session."""
        if not self.is_initialized or self.session_factory is None:
            raise DatabaseConfigurationError("DatabaseManager is not initialized.")

        async with self.session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
