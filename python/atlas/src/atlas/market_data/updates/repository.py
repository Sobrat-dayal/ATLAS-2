import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Sequence

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from atlas.market_data.updates.models import MarketDataUpdateTarget, MarketDataUpdateJob, MarketDataUpdateJobAttempt
from atlas.market_data.updates.enums import UpdateJobStatus, UpdateAttemptStatus

class MarketDataUpdateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_due_targets(self) -> Sequence[MarketDataUpdateTarget]:
        now = datetime.now(timezone.utc)
        stmt = select(MarketDataUpdateTarget).where(
            and_(
                MarketDataUpdateTarget.enabled == True,
                MarketDataUpdateTarget.next_run_at <= now
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_job(self, job: MarketDataUpdateJob) -> MarketDataUpdateJob:
        self.session.add(job)
        await self.session.flush()
        return job

    async def update_target(self, target: MarketDataUpdateTarget) -> MarketDataUpdateTarget:
        await self.session.flush()
        return target

    async def get_target_by_id(self, target_id: uuid.UUID) -> Optional[MarketDataUpdateTarget]:
        return await self.session.get(MarketDataUpdateTarget, target_id)

    async def get_active_job_for_target(self, target_id: uuid.UUID) -> Optional[MarketDataUpdateJob]:
        stmt = select(MarketDataUpdateJob).where(
            and_(
                MarketDataUpdateJob.target_id == target_id,
                MarketDataUpdateJob.status.in_([
                    UpdateJobStatus.QUEUED,
                    UpdateJobStatus.RUNNING,
                    UpdateJobStatus.RETRY_WAIT
                ])
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def claim_job(self, worker_id: str, lease_duration: timedelta) -> Optional[MarketDataUpdateJob]:
        now = datetime.now(timezone.utc)
        
        # We need to find a job that is QUEUED, or RETRY_WAIT and available_at <= now,
        # or RUNNING and lease_expires_at < now (stale lease)
        
        stmt = select(MarketDataUpdateJob).where(
            or_(
                and_(
                    MarketDataUpdateJob.status == UpdateJobStatus.QUEUED,
                    MarketDataUpdateJob.scheduled_for <= now,
                    MarketDataUpdateJob.available_at <= now
                ),
                and_(
                    MarketDataUpdateJob.status == UpdateJobStatus.RETRY_WAIT,
                    MarketDataUpdateJob.available_at <= now
                ),
                and_(
                    MarketDataUpdateJob.status == UpdateJobStatus.RUNNING,
                    MarketDataUpdateJob.lease_expires_at != None,
                    MarketDataUpdateJob.lease_expires_at < now
                )
            )
        ).with_for_update(skip_locked=True).limit(1)

        result = await self.session.execute(stmt)
        job = result.scalar_one_or_none()

        if job:
            job.status = UpdateJobStatus.RUNNING
            job.lease_owner = worker_id
            job.lease_expires_at = now + lease_duration
            job.heartbeat_at = now
            if not job.started_at:
                job.started_at = now
            await self.session.flush()
            return job

        return None

    async def renew_lease(self, job_id: uuid.UUID, worker_id: str, lease_duration: timedelta) -> bool:
        now = datetime.now(timezone.utc)
        stmt = update(MarketDataUpdateJob).where(
            and_(
                MarketDataUpdateJob.id == job_id,
                MarketDataUpdateJob.lease_owner == worker_id,
                MarketDataUpdateJob.status == UpdateJobStatus.RUNNING
            )
        ).values(
            lease_expires_at=now + lease_duration,
            heartbeat_at=now,
            updated_at=now
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def record_attempt(self, attempt: MarketDataUpdateJobAttempt) -> MarketDataUpdateJobAttempt:
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def complete_job_success(self, job_id: uuid.UUID, attempt_id: uuid.UUID, ingestion_run_id: uuid.UUID) -> None:
        now = datetime.now(timezone.utc)
        job = await self.session.get(MarketDataUpdateJob, job_id)
        if job:
            job.status = UpdateJobStatus.SUCCEEDED
            job.finished_at = now
            job.final_ingestion_run_id = ingestion_run_id
            job.lease_owner = None
            job.lease_expires_at = None

        attempt = await self.session.get(MarketDataUpdateJobAttempt, attempt_id)
        if attempt:
            attempt.status = UpdateAttemptStatus.SUCCEEDED
            attempt.finished_at = now
            attempt.ingestion_run_id = ingestion_run_id
        
        await self.session.flush()

    async def complete_job_failure(
        self, 
        job_id: uuid.UUID, 
        attempt_id: uuid.UUID, 
        error_code: str, 
        error_message: str,
        retry: bool,
        available_at: Optional[datetime] = None
    ) -> None:
        now = datetime.now(timezone.utc)
        job = await self.session.get(MarketDataUpdateJob, job_id)
        if job:
            if retry:
                job.status = UpdateJobStatus.RETRY_WAIT
                if available_at:
                    job.available_at = available_at
            else:
                job.status = UpdateJobStatus.FAILED
                job.finished_at = now
                job.final_error_code = error_code
                job.final_error_message = error_message
            
            job.lease_owner = None
            job.lease_expires_at = None

        attempt = await self.session.get(MarketDataUpdateJobAttempt, attempt_id)
        if attempt:
            attempt.status = UpdateAttemptStatus.FAILED
            attempt.finished_at = now
            attempt.error_code = error_code
            attempt.error_message = error_message

        await self.session.flush()
