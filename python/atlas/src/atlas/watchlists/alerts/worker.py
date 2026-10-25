"""Server-side background worker for continuous Watchlist Alert evaluation and dispatch (Stage 80)."""

import asyncio
import datetime
import logging
from typing import Dict, List, Optional, Set
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.watchlists.alerts.evaluation import AlertEvaluationEngine
from atlas.watchlists.alerts.notification_dispatch import AlertNotificationDispatcher
from atlas.watchlists.alerts.repository import WatchlistAlertRepository
from atlas.watchlists.alerts.schemas import AlertHealthStatusResponse

logger = logging.getLogger(__name__)


class WatchlistAlertWorker:
    """Supervised server-side background worker for continuous financial alert evaluation."""

    def __init__(
        self,
        session_factory,
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self.session_factory = session_factory
        self.poll_interval_seconds = poll_interval_seconds
        self._is_running = False
        self._task: Optional[asyncio.Task] = None
        self._last_heartbeat: Optional[datetime.datetime] = None
        self._active_rules_cache: Dict[str, Set[UUID]] = {}
        self._rule_count: int = 0
        self._eval_count: int = 0
        self._trigger_count: int = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def start(self) -> None:
        """Starts the background worker task."""
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._worker_loop())
        logger.info("WatchlistAlertWorker started.")

    async def stop(self) -> None:
        """Gracefully terminates the background worker."""
        self._is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("WatchlistAlertWorker stopped.")

    async def refresh_active_rules_index(self, session: AsyncSession) -> None:
        """Indexes active rules in memory to avoid scanning the entire database per tick (Requirement 74 & 140)."""
        repo = WatchlistAlertRepository(session)
        rules = await repo.get_all_active_rules()
        new_index: Dict[str, Set[UUID]] = {}
        count = 0
        for r in rules:
            key = f"{r.market_series_identity}:{r.quote_measure}"
            if key not in new_index:
                new_index[key] = set()
            new_index[key].add(r.id)
            count += 1
        self._active_rules_cache = new_index
        self._rule_count = count

    async def evaluate_event(self, event_envelope: dict) -> List[UUID]:
        """Evaluates a market quote event using a scoped database session."""
        async with self.session_factory() as session:
            engine = AlertEvaluationEngine(session)
            triggered = await engine.evaluate_event(event_envelope)
            self._eval_count += 1
            if triggered:
                self._trigger_count += len(triggered)
            return triggered

    async def dispatch_notifications(self) -> int:
        """Runs a batch outbox notification dispatch cycle."""
        async with self.session_factory() as session:
            dispatcher = AlertNotificationDispatcher(session)
            return await dispatcher.dispatch_pending(limit=50)

    async def get_health_status(self) -> AlertHealthStatusResponse:
        """Returns the current operational health of the evaluation system."""
        now = datetime.datetime.now(datetime.timezone.utc)
        is_healthy = self._is_running
        if self._last_heartbeat:
            age = (now - self._last_heartbeat).total_seconds()
            if age > 30:
                is_healthy = False

        status_str = "HEALTHY" if is_healthy else ("DEGRADED" if self._is_running else "UNAVAILABLE")

        return AlertHealthStatusResponse(
            status=status_str,
            worker_running=self._is_running,
            last_heartbeat=self._last_heartbeat,
            active_rules_in_memory=self._rule_count,
            evaluation_queue_lag_ms=0,
            connected_to_market_events=self._is_running,
            entitlement_status="AUTHORIZED",
        )

    async def _worker_loop(self) -> None:
        """Main evaluation and notification dispatch loop."""
        index_refresh_interval = 30  # seconds
        last_index_refresh = 0.0

        while self._is_running:
            now = datetime.datetime.now(datetime.timezone.utc)
            self._last_heartbeat = now
            loop_start = asyncio.get_event_loop().time()

            try:
                # 1. Periodically refresh active rule index
                if loop_start - last_index_refresh >= index_refresh_interval:
                    async with self.session_factory() as session:
                        await self.refresh_active_rules_index(session)
                    last_index_refresh = loop_start

                # 2. Dispatch pending outbox notifications
                await self.dispatch_notifications()

            except Exception as e:
                logger.error("Error in WatchlistAlertWorker loop: %s", e, exc_info=True)

            await asyncio.sleep(self.poll_interval_seconds)
