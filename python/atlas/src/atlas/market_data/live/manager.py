import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Any
from uuid import UUID

from atlas.market_data.live.settings import LiveQuoteWorkerSettings
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.market_data.requests import LiveQuoteSubscriptionRequest
from atlas.providers.routing.resolver import ProviderResolver
from atlas.market_data.enums import MarketDataOperation
from atlas.market_data.protocols import LiveQuoteStreamProvider

logger = logging.getLogger(__name__)


class LiveQuoteSourceManager:
    """
    Manages connections and streams to Providers for Live Quotes.
    Groups targets, establishes streams, and passes incoming quotes to the StateStore.
    """

    def __init__(
        self,
        settings: LiveQuoteWorkerSettings,
        provider_resolver: ProviderResolver,
        store: LiveQuoteStateStore,
    ):
        self.settings = settings
        self.provider_resolver = provider_resolver
        self.store = store
        
        # State: provider_id -> task
        self._provider_tasks: Dict[str, List[asyncio.Task]] = {}
        # provider_id -> current targets
        self._provider_targets: Dict[str, Set[UUID]] = {}
        
        self._running = False

    async def reconcile_targets(self, provider_id: str, targets: Set[UUID]):
        """
        Reconciles the target list for a specific provider.
        If the target list has changed, restarts the streams for this provider.
        """
        current_targets = self._provider_targets.get(provider_id, set())
        if current_targets == targets:
            return  # No change

        logger.info(f"Reconciling targets for {provider_id}. Old count: {len(current_targets)}, New count: {len(targets)}")
        self._provider_targets[provider_id] = targets
        
        # Cancel existing streams
        await self._cancel_provider_streams(provider_id)
        
        if not targets:
            return
            
        # Start new streams based on chunks
        target_list = list(targets)
        chunks = [
            target_list[i : i + self.settings.targets_per_stream_chunk]
            for i in range(0, len(target_list), self.settings.targets_per_stream_chunk)
        ]
        
        # Limit max streams
        chunks = chunks[:self.settings.max_streams_per_provider]
        
        tasks = []
        for chunk in chunks:
            task = asyncio.create_task(self._stream_task(provider_id, chunk))
            tasks.append(task)
            
        self._provider_tasks[provider_id] = tasks

    async def _cancel_provider_streams(self, provider_id: str):
        tasks = self._provider_tasks.pop(provider_id, [])
        for task in tasks:
            task.cancel()
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _stream_task(self, provider_id: str, instrument_ids: List[UUID]):
        """
        Maintains a stream connection to a provider for a subset of instruments.
        """
        request = LiveQuoteSubscriptionRequest(instrument_ids=tuple(instrument_ids))
        
        # Fetch the configured provider
        provider = await self.provider_resolver.resolve(
            operation=MarketDataOperation.LIVE_QUOTE_STREAM,
            provider_override=provider_id
        )
        
        if not isinstance(provider, LiveQuoteStreamProvider):
            logger.error(f"Provider {provider_id} does not support LIVE_QUOTE_STREAM")
            return
            
        while True:
            try:
                logger.info(f"Starting stream for {provider_id} with {len(instrument_ids)} targets")
                async for quote in provider.stream_live_quotes(request):
                    received_at = datetime.now(timezone.utc)
                    await self.store.put_if_newer(quote, received_at)
                    
            except asyncio.CancelledError:
                logger.info(f"Stream task for {provider_id} cancelled.")
                break
            except Exception as e:
                logger.exception(f"Error in stream for {provider_id}. Reconnecting in {self.settings.reconnect_base_backoff_seconds}s...")
                await asyncio.sleep(self.settings.reconnect_base_backoff_seconds)

    async def shutdown(self):
        """
        Gracefully shuts down all active streams.
        """
        self._running = False
        for provider_id in list(self._provider_tasks.keys()):
            await self._cancel_provider_streams(provider_id)
        self._provider_targets.clear()
