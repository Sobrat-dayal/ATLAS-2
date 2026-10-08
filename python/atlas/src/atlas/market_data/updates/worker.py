import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.market_data.ingestion.service import HistoricalMarketDataIngestionService
from atlas.market_data.requests import HistoricalBarsRequest
from atlas.market_data.enums import BarInterval, PriceAdjustment
from atlas.market_data.updates.models import MarketDataUpdateJobAttempt
from atlas.market_data.updates.repository import MarketDataUpdateRepository
from atlas.market_data.updates.settings import MarketDataUpdateSettings
from atlas.market_data.updates.enums import UpdateAttemptStatus

logger = logging.getLogger(__name__)

class MarketDataUpdateWorker:
    def __init__(
        self,
        db_session: AsyncSession,
        ingestion_service: HistoricalMarketDataIngestionService,
        settings: MarketDataUpdateSettings,
    ):
        self._db_session = db_session
        self._repository = MarketDataUpdateRepository(db_session)
        self._ingestion_service = ingestion_service
        self._settings = settings

    async def execute_one_job(self) -> bool:
        """
        Attempts to claim and execute one job.
        Returns True if a job was found and processed, False otherwise.
        """
        lease_duration = timedelta(seconds=self._settings.lease_duration_seconds)
        job = await self._repository.claim_job(self._settings.worker_id, lease_duration)
        if not job:
            await self._db_session.rollback()
            return False

        job.attempt_count += 1
        
        attempt = MarketDataUpdateJobAttempt(
            job_id=job.id,
            attempt_number=job.attempt_count,
            worker_id=self._settings.worker_id,
            started_at=datetime.now(timezone.utc),
            status=UpdateAttemptStatus.RUNNING,
        )
        await self._repository.record_attempt(attempt)
        await self._db_session.commit()

        # Execute
        target = await self._repository.get_target_by_id(job.target_id)
        if not target:
            await self._fail_job(job.id, attempt.id, "TARGET_NOT_FOUND", "Target not found", job.attempt_count >= job.max_attempts)
            return True

        request = HistoricalBarsRequest(
            instrument_id=target.instrument_id,
            interval=BarInterval(target.interval),
            start=job.range_start_at,
            end=job.range_end_at,
            adjustment=PriceAdjustment(target.adjustment)
        )

        try:
            # We assume ingestion_service handles the underlying provider fetch and ClickHouse write.
            # Stage 39 service creates a run, we capture the run ID.
            run_id = await self._ingestion_service.ingest_bars(request)
            
            # If successful
            await self._repository.complete_job_success(job.id, attempt.id, run_id)
            
            # Update target coverage
            target = await self._repository.get_target_by_id(job.target_id)
            if target:
                if not target.last_successful_coverage_end_at or job.range_end_at > target.last_successful_coverage_end_at:
                    target.last_successful_coverage_end_at = job.range_end_at
                target.last_success_at = datetime.now(timezone.utc)
                target.consecutive_failures = 0
                await self._repository.update_target(target)
                
            await self._db_session.commit()
            
        except Exception as e:
            logger.error(f"Worker {self._settings.worker_id} failed job {job.id}: {e}", exc_info=True)
            
            # Fail job
            target = await self._repository.get_target_by_id(job.target_id)
            if target:
                target.last_failure_at = datetime.now(timezone.utc)
                target.last_failure_code = type(e).__name__
                target.consecutive_failures += 1
                await self._repository.update_target(target)
                
            will_retry = job.attempt_count < job.max_attempts
            available_at = None
            if will_retry:
                # Exponential backoff
                delay = self._settings.retry_backoff_base_seconds * (2 ** (job.attempt_count - 1))
                available_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                
            await self._fail_job(job.id, attempt.id, type(e).__name__, str(e), not will_retry, available_at)
        
        return True

    async def _fail_job(self, job_id: uuid.UUID, attempt_id: uuid.UUID, error_code: str, error_message: str, final: bool, available_at=None):
        await self._repository.complete_job_failure(
            job_id, attempt_id, error_code, error_message, not final, available_at
        )
        await self._db_session.commit()
