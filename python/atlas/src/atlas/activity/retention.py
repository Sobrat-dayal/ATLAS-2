"""Maintenance retention cleanup routines for ATLAS User Activity."""

import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import UserActivityRepository
from .service import RETENTION_DAYS

logger = logging.getLogger(__name__)


async def run_activity_retention_cleanup(
    session: AsyncSession,
    retention_days: int = RETENTION_DAYS,
    batch_size: int = 500,
) -> int:
    """
    Operator / scheduled maintenance task: physically prunes records older than retention_days.
    Batches deletion to avoid table locking in PostgreSQL.
    """
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
    repo = UserActivityRepository(session)

    total_deleted = 0
    while True:
        deleted = await repo.cleanup_expired(retention_cutoff=cutoff, batch_size=batch_size)
        total_deleted += deleted
        await session.commit()
        if deleted < batch_size:
            break

    logger.info(
        "Activity retention cleanup complete: purged %d records older than %s",
        total_deleted,
        cutoff.isoformat(),
    )
    return total_deleted
