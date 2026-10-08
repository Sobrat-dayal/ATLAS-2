from datetime import datetime, timezone
from typing import Optional

from atlas.market_data.freshness.enums import (
    MarketDataFreshnessAgeBasis,
    MarketDataSourceTimestampFallback,
    MarketDataFreshnessStatus,
    MarketDataFreshnessReason,
)
from atlas.market_data.freshness.models import (
    MarketDataFreshnessPolicy,
    MarketDataFreshnessState,
    MarketDataFreshnessEvaluation,
)
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.realtime.websocket.models import QuoteSubscriptionKey


class MarketDataFreshnessEvaluator:
    """
    Pure evaluator for Market Data Freshness.
    Performs no IO, network, or side effects.
    """

    @staticmethod
    def evaluate(
        series_key: QuoteSubscriptionKey,
        provider_key: str,
        policy: MarketDataFreshnessPolicy,
        now: datetime,
        quote_record: Optional[QuoteCacheRecord],
        target_enabled: bool = True,
        previous_state: Optional[MarketDataFreshnessState] = None,
    ) -> MarketDataFreshnessEvaluation:
        
        if not target_enabled:
            return MarketDataFreshnessEvaluator._create_unavailable(
                series_key, provider_key, policy, now, previous_state, MarketDataFreshnessReason.TARGET_DISABLED
            )

        if not quote_record:
            return MarketDataFreshnessEvaluator._create_unavailable(
                series_key, provider_key, policy, now, previous_state, MarketDataFreshnessReason.NO_QUOTE
            )

        # Base properties
        provider_delayed = getattr(quote_record.quote, "is_delayed", False) # or logic from quote timestamp source if delayed isn't explicit
        # We need to map provider delayed correctly. If quote has 'is_delayed' or 'session' we'd map it.
        # But looking at Quote, there is no `is_delayed` boolean.
        # Let's check what fields we have on Quote.
        # Quote has `timestamp_source`, `session`. Stage 33 mentions `delay_seconds`.
        # I'll use getattr safely in case it's added.
        provider_delayed = getattr(quote_record.quote, "is_delayed", False)
        provider_delay_seconds = getattr(quote_record.quote, "delay_seconds", None)

        source_ts = quote_record.source_timestamp
        receive_ts = quote_record.received_at

        # Determine basis and age
        basis_ts: datetime
        basis_used: MarketDataFreshnessAgeBasis
        reason_prefix: str
        
        if policy.age_basis == MarketDataFreshnessAgeBasis.RECEIVE_TIME_ONLY:
            basis_ts = receive_ts
            basis_used = MarketDataFreshnessAgeBasis.RECEIVE_TIME_ONLY
            reason_prefix = "RECEIVE_TIME"
        else:
            if source_ts is not None:
                basis_ts = source_ts
                basis_used = MarketDataFreshnessAgeBasis.SOURCE_TIME_PREFERRED
                reason_prefix = "SOURCE_TIME"
            else:
                if policy.source_timestamp_fallback == MarketDataSourceTimestampFallback.USE_RECEIVED_AT:
                    basis_ts = receive_ts
                    basis_used = MarketDataFreshnessAgeBasis.RECEIVE_TIME_ONLY
                    reason_prefix = "RECEIVE_TIME"
                else:
                    return MarketDataFreshnessEvaluator._create_unavailable(
                        series_key, provider_key, policy, now, previous_state, MarketDataFreshnessReason.SOURCE_TIMESTAMP_UNAVAILABLE,
                        provider_delayed=provider_delayed,
                        provider_delay_seconds=provider_delay_seconds,
                        quote_source_timestamp=source_ts,
                        quote_received_at=receive_ts,
                    )

        # Calculate age
        age_delta = now - basis_ts
        age_seconds = int(age_delta.total_seconds())

        # Future timestamp skew clamp
        is_future = age_seconds < 0
        if is_future:
            age_seconds = 0
            reason_prefix = "SOURCE_TIMESTAMP_IN_FUTURE"

        # Determine status
        status: MarketDataFreshnessStatus
        reason: MarketDataFreshnessReason
        next_eval_at: Optional[datetime] = None
        grace = 0.1 # 100ms grace for timer bounds

        if age_seconds <= policy.fresh_until_seconds:
            status = MarketDataFreshnessStatus.FRESH
            reason = MarketDataFreshnessReason.SOURCE_TIMESTAMP_IN_FUTURE if is_future else MarketDataFreshnessReason(f"{reason_prefix}_WITHIN_FRESH_THRESHOLD")
            
            # Next evaluation when it becomes AGING
            next_eval_at = basis_ts.timestamp() + policy.fresh_until_seconds + grace
        elif age_seconds <= policy.stale_after_seconds:
            status = MarketDataFreshnessStatus.AGING
            reason = MarketDataFreshnessReason(f"{reason_prefix}_BETWEEN_THRESHOLDS")
            
            # Next evaluation when it becomes STALE
            next_eval_at = basis_ts.timestamp() + policy.stale_after_seconds + grace
        else:
            status = MarketDataFreshnessStatus.STALE
            reason = MarketDataFreshnessReason(f"{reason_prefix}_EXCEEDS_STALE_THRESHOLD")
            # No next evaluation until quote update or policy change

        changed_at = now
        prev_status = None
        if previous_state:
            prev_status = previous_state.status
            if previous_state.status == status:
                changed_at = previous_state.status_changed_at

        state = MarketDataFreshnessState(
            series_key=series_key,
            provider_key=provider_key,
            status=status,
            reason=reason,
            effective_age_seconds=age_seconds,
            age_basis_used=basis_used,
            provider_delayed=provider_delayed,
            provider_delay_seconds=provider_delay_seconds,
            quote_source_timestamp=source_ts,
            quote_received_at=receive_ts,
            evaluated_at=now,
            status_changed_at=changed_at,
            previous_status=prev_status,
            fresh_until_seconds=policy.fresh_until_seconds,
            stale_after_seconds=policy.stale_after_seconds,
        )

        return MarketDataFreshnessEvaluation(
            state=state,
            next_evaluation_at=datetime.fromtimestamp(next_eval_at, timezone.utc) if next_eval_at else None
        )

    @staticmethod
    def _create_unavailable(
        series_key: QuoteSubscriptionKey,
        provider_key: str,
        policy: MarketDataFreshnessPolicy,
        now: datetime,
        previous_state: Optional[MarketDataFreshnessState],
        reason: MarketDataFreshnessReason,
        provider_delayed: bool = False,
        provider_delay_seconds: Optional[int] = None,
        quote_source_timestamp: Optional[datetime] = None,
        quote_received_at: Optional[datetime] = None,
    ) -> MarketDataFreshnessEvaluation:
        
        changed_at = now
        prev_status = None
        if previous_state:
            prev_status = previous_state.status
            if previous_state.status == MarketDataFreshnessStatus.UNAVAILABLE:
                changed_at = previous_state.status_changed_at

        state = MarketDataFreshnessState(
            series_key=series_key,
            provider_key=provider_key,
            status=MarketDataFreshnessStatus.UNAVAILABLE,
            reason=reason,
            effective_age_seconds=0,
            age_basis_used=policy.age_basis,
            provider_delayed=provider_delayed,
            provider_delay_seconds=provider_delay_seconds,
            quote_source_timestamp=quote_source_timestamp,
            quote_received_at=quote_received_at,
            evaluated_at=now,
            status_changed_at=changed_at,
            previous_status=prev_status,
            fresh_until_seconds=policy.fresh_until_seconds,
            stale_after_seconds=policy.stale_after_seconds,
        )

        return MarketDataFreshnessEvaluation(state=state, next_evaluation_at=None)
