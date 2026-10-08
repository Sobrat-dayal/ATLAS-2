import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional
from uuid import UUID

from atlas.market_data.freshness.evaluator import MarketDataFreshnessEvaluator
from atlas.market_data.freshness.resolver import MarketDataFreshnessPolicyResolver
from atlas.market_data.freshness.settings import MarketDataFreshnessSettings
from atlas.market_data.freshness.store import MarketDataFreshnessStateStore
from atlas.market_data.live.models import MarketDataLiveQuoteTarget
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.realtime.enums import LiveEventType
from atlas.realtime.models import LiveEventEnvelope, MarketDataFreshnessUpdatedPayload
from atlas.realtime.pipeline import LiveEventPipeline
from atlas.realtime.websocket.models import QuoteSubscriptionKey


logger = logging.getLogger(__name__)


class MarketDataFreshnessMonitor:
    """
    Background monitor that continuously evaluates freshness state for owned targets.
    """

    def __init__(
        self,
        settings: MarketDataFreshnessSettings,
        state_store: MarketDataFreshnessStateStore,
        quote_store: LiveQuoteStateStore,
        policy_resolver: MarketDataFreshnessPolicyResolver,
        pipeline: LiveEventPipeline,
    ):
        self.settings = settings
        self.state_store = state_store
        self.quote_store = quote_store
        self.policy_resolver = policy_resolver
        self.pipeline = pipeline
        
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._active_targets: List[MarketDataLiveQuoteTarget] = []

    def set_active_targets(self, targets: List[MarketDataLiveQuoteTarget]):
        """Called periodically by the worker to update its leased targets."""
        self._active_targets = targets

    async def start(self):
        if not self.settings.enabled:
            return
        self._running = True
        self._monitor_task = asyncio.create_task(self._run_loop())

    async def stop(self):
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _run_loop(self):
        while self._running:
            try:
                start_time = datetime.now(timezone.utc)
                await self._evaluate_all()
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                
                # Sleep enough to prevent tight loop, maybe 1 second minus elapsed
                sleep_time = max(0.1, 1.0 - elapsed)
                await asyncio.sleep(sleep_time)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in FreshnessMonitor run loop")
                await asyncio.sleep(5.0)

    async def _evaluate_all(self):
        now = datetime.now(timezone.utc)
        
        for target in self._active_targets:
            if not self._running:
                break
                
            try:
                series_key = QuoteSubscriptionKey(
                    instrument_entity_id=target.instrument_entity_id,
                    variant=target.variant
                )
                
                # Retrieve current state to check if evaluation is due
                state = await self.state_store.get_state(series_key)
                if state:
                    # Is it time to re-evaluate?
                    # The transition to STALE happens at basis + stale_after_seconds.
                    # Instead of precise timer logic, we check the effective age.
                    # Or we just re-evaluate always since it's cheap? Let's re-evaluate.
                    pass

                policy = await self.policy_resolver.resolve(target.provider_id, target=target)
                quote_record = await self.quote_store.get_latest_quote(target.instrument_entity_id)
                
                eval_res = MarketDataFreshnessEvaluator.evaluate(
                    series_key=series_key,
                    provider_key=target.provider_id,
                    policy=policy,
                    now=now,
                    quote_record=quote_record,
                    target_enabled=target.is_enabled,
                    previous_state=state,
                )
                
                new_state = eval_res.state
                
                # Determine if state changed
                changed = False
                if not state:
                    changed = True
                elif state.status != new_state.status or state.reason != new_state.reason:
                    changed = True
                    
                if changed:
                    # Update state store
                    saved = await self.state_store.put_if_newer(new_state)
                    
                    # Emit event if enabled and saved
                    if saved and self.settings.transition_event_enabled:
                        await self._emit_transition_event(new_state, now)
                        
            except Exception as e:
                logger.error(f"Error evaluating freshness for target {target.instrument_entity_id}: {e}")

    async def _emit_transition_event(self, state, now: datetime):
        payload = MarketDataFreshnessUpdatedPayload(
            series_key=state.series_key.model_dump(mode="json"),
            provider_key=state.provider_key,
            status=state.status,
            reason=state.reason,
            effective_age_seconds=state.effective_age_seconds,
            previous_status=state.previous_status,
        )

        event = LiveEventEnvelope(
            event_type=LiveEventType.MARKET_QUOTE_FRESHNESS_UPDATED,
            emitted_at=now,
            instrument_entity_id=state.series_key.instrument_entity_id,
            provider_key=state.provider_key,
            payload=payload.model_dump(mode="json")
        )
        
        event_json = event.model_dump_json()
        
        # Publish to stream
        if self.pipeline.settings.enabled:
            stream_key = self.pipeline.settings.stream_key_prefix
            await self.pipeline.redis.xadd(
                stream_key,
                {"data": event_json},
                maxlen=self.pipeline.settings.stream_max_length,
                approximate=True
            )
