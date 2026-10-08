from datetime import datetime, timezone
from typing import Optional

from atlas.market_data.freshness.evaluator import MarketDataFreshnessEvaluator
from atlas.market_data.freshness.models import MarketDataFreshnessState
from atlas.market_data.freshness.resolver import MarketDataFreshnessPolicyResolver
from atlas.market_data.freshness.store import MarketDataFreshnessStateStore
from atlas.market_data.live.store import LiveQuoteStateStore
from atlas.realtime.websocket.models import QuoteSubscriptionKey


class MarketDataFreshnessQueryService:
    def __init__(
        self,
        state_store: MarketDataFreshnessStateStore,
        quote_store: LiveQuoteStateStore,
        policy_resolver: MarketDataFreshnessPolicyResolver,
    ):
        self.state_store = state_store
        self.quote_store = quote_store
        self.policy_resolver = policy_resolver

    async def get_freshness(
        self, series_key: QuoteSubscriptionKey, fallback_evaluation: bool = True
    ) -> Optional[MarketDataFreshnessState]:
        """
        Retrieves current freshness state from cache.
        Optionally performs a cheap internal evaluation if state is missing but Quote exists.
        """
        state = await self.state_store.get_state(series_key)
        if state:
            return state

        if fallback_evaluation:
            # Cheap internal evaluation if Quote exists
            quote_record = await self.quote_store.get_latest_quote(series_key.instrument_entity_id)
            if quote_record:
                # We need provider_key to resolve policy. Try to guess from quote or target.
                # However, quote doesn't have provider_key natively unless it's in venue_id?
                # Actually, quote has no strict provider_key field. It comes from ingestion.
                # Let's assume a default "unknown" provider_key for fallback evaluation
                provider_key = "unknown"
                policy = await self.policy_resolver.resolve(provider_key, target=None)
                now = datetime.now(timezone.utc)
                eval_res = MarketDataFreshnessEvaluator.evaluate(
                    series_key=series_key,
                    provider_key=provider_key,
                    policy=policy,
                    now=now,
                    quote_record=quote_record,
                    target_enabled=True,
                    previous_state=None,
                )
                return eval_res.state

        return None
