import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifespan.
    Handles startup and shutdown events for the modular monolith.
    """
    setup_logging()
    logger.info("Starting ATLAS API foundation...")
    
    # Stage 11: Application state setup
    # Future stages will initialize DB pools, Redis, etc. here.
    app.state.ready = True
    
    yield
    
    logger.info("Shutting down ATLAS API foundation...")
    app.state.ready = False
    # Cleanup logic here
