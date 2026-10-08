import argparse
import asyncio
import logging
from redis.asyncio import Redis

from atlas_api.config import get_settings as get_api_settings
from atlas.database import async_session_maker
from atlas.market_data.live.manager import LiveQuoteSourceManager
from atlas.market_data.live.settings import LiveQuoteWorkerSettings
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.market_data.live.worker import LiveQuoteWorker
from atlas.providers.routing.resolver import ProviderResolver
from atlas.providers.configuration.repository import ProviderConfigurationRepository
from atlas.providers.configuration.manager import ProviderConfigurationManager
from atlas.providers.health.manager import ProviderHealthManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_worker():
    settings = LiveQuoteWorkerSettings()
    api_settings = get_api_settings()

    logger.info(f"Starting Live Quote Worker: {settings.worker_id}")

    # Set up Redis
    # Assuming redis URL is in api settings, or we default to a local valkey
    redis_url = getattr(api_settings, "redis_url", "redis://localhost:6379/0")
    redis_client = Redis.from_url(redis_url, decode_responses=False)
    
    # Store
    store = LiveQuoteStateStore(redis_client)

    # Database
    async with async_session_maker() as session:
        # We need a Resolver. For this CLI, we will construct a basic one.
        # Ideally, we should inject this from a broader capability layer container.
        config_repo = ProviderConfigurationRepository(session)
        config_manager = ProviderConfigurationManager(config_repo)
        health_manager = ProviderHealthManager(session)
        
        resolver = ProviderResolver(
            config_manager=config_manager,
            health_manager=health_manager
        )
        
        manager = LiveQuoteSourceManager(
            settings=settings,
            provider_resolver=resolver,
            store=store
        )
        
        worker = LiveQuoteWorker(
            db_session=session,
            source_manager=manager,
            settings=settings
        )
        
        await worker.start()
        
        # Keep alive
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("Shutting down worker...")
        finally:
            await worker.stop()
            await redis_client.aclose()


def main():
    parser = argparse.ArgumentParser(description="Run the Live Quote Worker")
    parser.parse_args()
    
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Exiting...")


if __name__ == "__main__":
    main()
