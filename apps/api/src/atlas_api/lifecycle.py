import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logging import setup_logging
from .config import get_settings
from .database import db_manager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifespan.
    Handles startup and shutdown events for the modular monolith.
    """
    setup_logging()
    logger.info("Starting ATLAS API foundation...")
    
    # Initialize database
    settings = get_settings()
    db_manager.initialize(
        url=settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        application_name=settings.app_name,
    )
    
    # Stage 11: Application state setup
    # Future stages will initialize DB pools, Redis, etc. here.
    app.state.ready = True
    app.state.db = db_manager
    
    yield
    
    logger.info("Shutting down ATLAS API foundation...")
    app.state.ready = False
    
    # Dispose database engine
    await db_manager.dispose()
