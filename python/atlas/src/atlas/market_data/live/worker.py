import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Set, Optional, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from atlas.market_data.freshness.monitor import MarketDataFreshnessMonitor

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.market_data.live.manager import LiveQuoteSourceManager
from atlas.market_data.live.models import MarketDataLiveQuoteTarget
from atlas.market_data.live.settings import LiveQuoteWorkerSettings

logger = logging.getLogger(__name__)


class LiveQuoteWorker:
    """
    Coordinates the fetching of target leases and delegates to LiveQuoteSourceManager
    to establish and maintain streams.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        source_manager: LiveQuoteSourceManager,
        settings: LiveQuoteWorkerSettings,
        freshness_monitor: Optional["MarketDataFreshnessMonitor"] = None,
    ):
        self._db_session = db_session
        self._source_manager = source_manager
        self._settings = settings
        self._freshness_monitor = freshness_monitor
        
        self._running = False
        self._worker_task: asyncio.Task | None = None

    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._run_loop())
        if self._freshness_monitor:
            await self._freshness_monitor.start()

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        if self._freshness_monitor:
            await self._freshness_monitor.stop()
        await self._source_manager.shutdown()
        # Release leases on shutdown
        await self._release_leases()

    async def _run_loop(self):
        while self._running:
            try:
                await self._reconcile_leases()
                await asyncio.sleep(self._settings.heartbeat_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in LiveQuoteWorker run loop")
                await asyncio.sleep(self._settings.reconnect_base_backoff_seconds)

    async def _reconcile_leases(self):
        """
        Maintains current leases and attempts to acquire new ones.
        Updates the SourceManager with the latest list of targets per provider.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Heartbeat existing leases
        stmt = (
            update(MarketDataLiveQuoteTarget)
            .where(
                MarketDataLiveQuoteTarget.lease_owner == self._settings.worker_id,
                MarketDataLiveQuoteTarget.is_enabled == True
            )
            .values(last_heartbeat_at=now, lease_expires_at=now + timedelta(seconds=self._settings.lease_duration_seconds))
            .returning(MarketDataLiveQuoteTarget.provider_id, MarketDataLiveQuoteTarget.instrument_entity_id)
        )
        
        result = await self._db_session.execute(stmt)
        await self._db_session.commit()
        
        active_targets = result.all()
        current_count = len(active_targets)
        
        # 2. Acquire new leases if capacity allows
        capacity = self._settings.max_concurrent_targets - current_count
        if capacity > 0:
            # Find expired or unowned leases
            claim_stmt = (
                select(MarketDataLiveQuoteTarget.instrument_entity_id)
                .where(
                    MarketDataLiveQuoteTarget.is_enabled == True,
                    (MarketDataLiveQuoteTarget.lease_expires_at < now) | (MarketDataLiveQuoteTarget.lease_expires_at.is_(None))
                )
                .limit(capacity)
                .with_for_update(skip_locked=True)
            )
            
            to_claim = (await self._db_session.execute(claim_stmt)).scalars().all()
            
            if to_claim:
                claim_update_stmt = (
                    update(MarketDataLiveQuoteTarget)
                    .where(MarketDataLiveQuoteTarget.instrument_entity_id.in_(to_claim))
                    .values(
                        lease_owner=self._settings.worker_id,
                        last_heartbeat_at=now,
                        lease_expires_at=now + timedelta(seconds=self._settings.lease_duration_seconds)
                    )
                    .returning(MarketDataLiveQuoteTarget.provider_id, MarketDataLiveQuoteTarget.instrument_entity_id)
                )
                
                claim_result = await self._db_session.execute(claim_update_stmt)
                await self._db_session.commit()
                active_targets.extend(claim_result.all())

        # 3. Group targets by provider and reconcile
        targets_by_provider: Dict[str, Set[UUID]] = {}
        for row in active_targets:
            provider_id = row.provider_id
            instrument_id = row.instrument_entity_id
            if provider_id not in targets_by_provider:
                targets_by_provider[provider_id] = set()
            targets_by_provider[provider_id].add(instrument_id)

        # Reconcile all providers
        for provider_id, targets in targets_by_provider.items():
            await self._source_manager.reconcile_targets(provider_id, targets)
            
        # If any providers are completely empty now, reconcile them to empty set
        all_providers = set(targets_by_provider.keys())
        for existing_provider in list(self._source_manager._provider_targets.keys()):
            if existing_provider not in all_providers:
                await self._source_manager.reconcile_targets(existing_provider, set())

        if self._freshness_monitor:
            # We need to pass the actual full rows to the monitor
            # active_targets has provider_id and instrument_entity_id, but the monitor needs the full ORM object
            # Let's fetch them
            full_targets_stmt = select(MarketDataLiveQuoteTarget).where(
                MarketDataLiveQuoteTarget.lease_owner == self._settings.worker_id,
                MarketDataLiveQuoteTarget.is_enabled == True
            )
            full_targets = (await self._db_session.execute(full_targets_stmt)).scalars().all()
            self._freshness_monitor.set_active_targets(list(full_targets))

    async def _release_leases(self):
        """
        Releases all leases owned by this worker on shutdown.
        """
        stmt = (
            update(MarketDataLiveQuoteTarget)
            .where(MarketDataLiveQuoteTarget.lease_owner == self._settings.worker_id)
            .values(lease_owner=None, lease_expires_at=None, last_heartbeat_at=None)
        )
        await self._db_session.execute(stmt)
        await self._db_session.commit()
