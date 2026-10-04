from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from .config import Settings, get_settings
from .database import db_manager


def get_app_settings() -> Settings:
    return get_settings()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.session():
        yield session
