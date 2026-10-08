import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.market_data.updates.models import MarketDataUpdateTarget, MarketDataUpdateJob
from atlas.market_data.updates.repository import MarketDataUpdateRepository
from atlas.market_data.updates.enums import UpdateJobStatus

logger = logging.getLogger(__name__)

class MarketDataUpdateScheduler:
    """
    Schedules MarketDataUpdateJob rows based on MarketDataUpdateTarget rows.
    Follows "pull" logic.
    """

    def __init__(self, db_session: AsyncSession, max_attempts: int = 3):
        self._db_session = db_session
        self._repository = MarketDataUpdateRepository(db_session)
        self._max_attempts = max_attempts

    async def schedule_due_targets(self) -> int:
        """
        Finds all due targets, creates jobs for them, and advances their next_run_at.
        Returns the number of jobs created.
        """
        targets = await self._repository.get_due_targets()
        jobs_created = 0
        now = datetime.now(timezone.utc)

        for target in targets:
            try:
                # Check if there's already an active job for this target
                active_job = await self._repository.get_active_job_for_target(target.id)
                if active_job:
                    logger.debug(f"Target {target.id} already has active job {active_job.id}")
                    # Push next_run_at forward so we don't spam
                    target.next_run_at = now + timedelta(seconds=target.cadence_seconds)
                    await self._repository.update_target(target)
                    continue

                # Determine range_start_at
                if target.last_successful_coverage_end_at:
                    range_start_at = target.last_successful_coverage_end_at - timedelta(seconds=target.revision_lookback_seconds)
                else:
                    range_start_at = target.initial_start_at

                range_end_at = now

                if range_start_at >= range_end_at:
                    logger.warning(f"Target {target.id} has start >= end. Skipping.")
                    target.next_run_at = now + timedelta(seconds=target.cadence_seconds)
                    await self._repository.update_target(target)
                    continue

                # Create job
                job = MarketDataUpdateJob(
                    target_id=target.id,
                    scheduled_for=now,
                    range_start_at=range_start_at,
                    range_end_at=range_end_at,
                    provider_override=target.provider_override,
                    status=UpdateJobStatus.QUEUED,
                    available_at=now,
                    max_attempts=self._max_attempts,
                )

                await self._repository.create_job(job)
                jobs_created += 1

                # Advance target next_run_at
                target.next_run_at = now + timedelta(seconds=target.cadence_seconds)
                await self._repository.update_target(target)

            except Exception as e:
                logger.error(f"Error scheduling target {target.id}: {e}", exc_info=True)

        await self._db_session.commit()
        return jobs_created
