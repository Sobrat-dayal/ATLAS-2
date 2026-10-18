import asyncio
import logging
from typing import Callable, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from atlas.providers.health.models import ProviderHealthCheckTrigger, ProviderHealthTargetType
from atlas.providers.health.registry import ProviderHealthRegistry
from atlas.providers.health.service import ProviderHealthService

logger = logging.getLogger(__name__)


class ProviderHealthMonitor:
    def __init__(
        self,
        health_registry: ProviderHealthRegistry,
        session_factory: Callable[[], AsyncSession],
        service_factory: Callable[[AsyncSession], ProviderHealthService],
        enabled: bool = False,
        interval_seconds: int = 300,
        concurrency: int = 4,
    ):
        self.health_registry = health_registry
        self.session_factory = session_factory
        self.service_factory = service_factory
        self.enabled = enabled
        self.interval_seconds = max(60, interval_seconds)  # Minimum 60s
        self.concurrency = concurrency
        self._task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

    def start(self):
        if not self.enabled:
            logger.info("ProviderHealthMonitor is disabled.")
            return
        if self._task is None:
            self._shutdown_event.clear()
            self._task = asyncio.create_task(self._run())
            logger.info("ProviderHealthMonitor started.")

    async def stop(self):
        if self._task is not None:
            self._shutdown_event.set()
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("ProviderHealthMonitor stopped.")

    async def _run(self):
        # Startup check after a short delay
        await asyncio.sleep(5)

        while not self._shutdown_event.is_set():
            try:
                definitions = self.health_registry.list_definitions()
                # Only monitor integration targets that are schedulable
                schedulable_keys = [
                    d.provider_key
                    for d in definitions
                    if d.schedulable and ProviderHealthTargetType.INTEGRATION in d.supported_targets
                ]

                # Bounded concurrency
                sem = asyncio.Semaphore(self.concurrency)

                async def _check(provider_key: str):
                    async with sem:
                        try:
                            import inspect
                            from contextlib import asynccontextmanager
                            raw_ctx = self.session_factory()
                            if inspect.isasyncgen(raw_ctx):
                                @asynccontextmanager
                                async def _gen_wrap():
                                    async for item in raw_ctx:
                                        yield item
                                ctx = _gen_wrap()
                            else:
                                ctx = raw_ctx
                            async with ctx as session:
                                service = self.service_factory(session)
                                await service.execute_check(
                                    provider_key=provider_key,
                                    target_type=ProviderHealthTargetType.INTEGRATION,
                                    trigger=ProviderHealthCheckTrigger.SCHEDULED,
                                )
                        except Exception as e:
                            logger.error(
                                f"ProviderHealthMonitor error checking {provider_key}: {e}",
                                exc_info=True,
                            )

                tasks = [_check(key) for key in schedulable_keys]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                logger.error(f"ProviderHealthMonitor loop error: {e}", exc_info=True)

            # Wait for next interval or shutdown
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                pass  # Normal interval elapsed
