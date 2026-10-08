import argparse
import asyncio
import logging

from atlas.database import async_session_maker
from atlas.market_data.updates.scheduler import MarketDataUpdateScheduler
from atlas.market_data.updates.worker import MarketDataUpdateWorker
from atlas.market_data.updates.settings import MarketDataUpdateSettings
from atlas.market_data.ingestion.service import HistoricalMarketDataIngestionService
from atlas.infrastructure.clickhouse.market_data.repository import HistoricalMarketDataRepository
from atlas.infrastructure.clickhouse.client import get_clickhouse_client
from atlas.providers.bootstrap import build_provider_registry

logger = logging.getLogger(__name__)

async def _run_scheduler():
    logger.info("Starting Market Data Update Scheduler...")
    settings = MarketDataUpdateSettings()
    
    while True:
        try:
            async with async_session_maker() as session:
                scheduler = MarketDataUpdateScheduler(session, max_attempts=settings.max_attempts)
                jobs_created = await scheduler.schedule_due_targets()
                if jobs_created > 0:
                    logger.info(f"Scheduler created {jobs_created} jobs.")
        except Exception as e:
            logger.error(f"Scheduler failed: {e}", exc_info=True)
            
        await asyncio.sleep(settings.poll_interval_seconds)

async def _run_worker():
    settings = MarketDataUpdateSettings()
    logger.info(f"Starting Market Data Update Worker (id={settings.worker_id})...")
    
    provider_registry = build_provider_registry()
    ch_client = get_clickhouse_client()
    ch_repository = HistoricalMarketDataRepository(ch_client)
    
    # Instantiate provider
    openbb_provider = provider_registry.get("openbb").factory()
    
    while True:
        try:
            async with async_session_maker() as session:
                ingestion_service = HistoricalMarketDataIngestionService(
                    db_session=session,
                    ch_repository=ch_repository,
                    provider=openbb_provider
                )
                worker = MarketDataUpdateWorker(session, ingestion_service, settings)
                
                processed = await worker.execute_one_job()
                if not processed:
                    await asyncio.sleep(settings.poll_interval_seconds)
        except Exception as e:
            logger.error(f"Worker loop failed: {e}", exc_info=True)
            await asyncio.sleep(settings.poll_interval_seconds)

def cli():
    parser = argparse.ArgumentParser(description="Market Data Update Workers (Stage 40)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("scheduler", help="Run the market data update scheduler daemon.")
    subparsers.add_parser("worker", help="Run the market data update worker daemon.")
    
    args = parser.parse_args()
    
    if args.command == "scheduler":
        asyncio.run(_run_scheduler())
    elif args.command == "worker":
        asyncio.run(_run_worker())

if __name__ == "__main__":
    cli()
