import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_settings
from .database import db_manager
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

    # Stage 31: Provider Health Monitor
    from atlas.providers.bootstrap import build_provider_registry, build_provider_health_registry
    from atlas.providers.health.monitor import ProviderHealthMonitor
    from atlas.providers.health.service import ProviderHealthService
    from atlas.providers.health.repository import ProviderHealthRepository
    from atlas.providers.configuration.service import ProviderConfigurationService
    from atlas.providers.configuration.secrets import SupabaseVaultSecretStore

    provider_registry = build_provider_registry()
    health_registry = build_provider_health_registry(provider_registry)

    def service_factory(session):
        secret_store = SupabaseVaultSecretStore(session)
        config_service = ProviderConfigurationService(session, secret_store)
        repo = ProviderHealthRepository(session)
        return ProviderHealthService(health_registry, provider_registry, repo, config_service)

    monitor = ProviderHealthMonitor(
        health_registry=health_registry,
        session_factory=db_manager.session,
        service_factory=service_factory,
        enabled=True,
        interval_seconds=300
    )
    app.state.health_monitor = monitor
    monitor.start()

    yield

    logger.info("Shutting down ATLAS API foundation...")
    app.state.ready = False

    if hasattr(app.state, "health_monitor"):
        await app.state.health_monitor.stop()

    # Dispose database engine
    await db_manager.dispose()
