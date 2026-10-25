"""Server-side event-driven Alert Evaluation Engine (Stage 80).

Evaluates incoming canonical Market Events against active alert rules:
- Validates event envelope and Quote payload
- Validates data freshness and delayed-data disclosure
- Enforces event ordering and rejects duplicates
- Performs decimal-safe condition evaluation
- Atomically commits triggers, updates evaluation states, and enqueues outbox records
- Guarantees idempotency via unique trigger deduplication keys
"""

import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.watchlists.alerts.conditions import evaluate_alert_condition
from atlas.watchlists.alerts.models import (
    WatchlistAlertNotificationOutbox,
    WatchlistAlertTrigger,
)
from atlas.watchlists.alerts.repository import WatchlistAlertRepository
from atlas.watchlists.alerts.schemas import (
    AlertEvaluationStatus,
    AlertRuleType,
    AlertState,
    ArmedSide,
    NotificationDeliveryStatus,
    QuoteMeasure,
    RecurrencePolicy,
    ReferenceMethodology,
)

logger = logging.getLogger(__name__)

# Max acceptable observation staleness for realtime movement alerts (in seconds)
MAX_STALENESS_SECONDS = 300


@dataclass(frozen=True)
class NormalizedObservation:
    """Canonical observation extracted from market data event."""

    instrument_id: UUID
    market_series_identity: str
    event_id: str
    observation_time: datetime.datetime
    received_at: datetime.datetime
    source: str
    venue: Optional[str]
    is_delayed: bool
    measures: Dict[QuoteMeasure, Decimal]
    reference_prices: Dict[ReferenceMethodology, Decimal]

    @property
    def references(self) -> Dict[ReferenceMethodology, Decimal]:
        return self.reference_prices


class AlertEvaluationEngine:
    """Core server-side evaluation worker engine."""

    def __init__(
        self,
        session: AsyncSession,
        repository: Optional[WatchlistAlertRepository] = None,
    ) -> None:
        self.session = session
        self.repository = repository or WatchlistAlertRepository(session)

    def extract_observation(
        self,
        event_envelope: Dict[str, Any],
    ) -> Optional[NormalizedObservation]:
        """Extracts and normalizes market observation data from a LiveEventEnvelope dictionary."""
        try:
            event_id = str(event_envelope.get("event_id", uuid4()))
            inst_id_raw = event_envelope.get("instrument_entity_id")
            if not inst_id_raw:
                return None
            instrument_id = UUID(str(inst_id_raw))
            provider_key = str(event_envelope.get("provider_key", "canonical_quotes"))
            emitted_at_raw = event_envelope.get("emitted_at")
            if isinstance(emitted_at_raw, datetime.datetime):
                emitted_at = emitted_at_raw
            elif isinstance(emitted_at_raw, str):
                emitted_at = datetime.datetime.fromisoformat(emitted_at_raw)
            else:
                emitted_at = datetime.datetime.now(datetime.timezone.utc)

            payload = event_envelope.get("payload", {})
            quote_data = payload.get("quote", {})
            if not quote_data and isinstance(payload, dict) and "last_price" in payload:
                quote_data = payload

            # Determine observation time
            src_time_raw = (
                payload.get("source_timestamp")
                or quote_data.get("as_of")
                or emitted_at
            )
            if isinstance(src_time_raw, datetime.datetime):
                observation_time = src_time_raw
            elif isinstance(src_time_raw, str):
                observation_time = datetime.datetime.fromisoformat(src_time_raw)
            else:
                observation_time = emitted_at

            # Ensure UTC timezone
            if observation_time.tzinfo is None:
                observation_time = observation_time.replace(tzinfo=datetime.timezone.utc)

            venue = quote_data.get("venue_id") or quote_data.get("venue")
            is_delayed = bool(payload.get("is_delayed", False) or quote_data.get("is_delayed", False))

            measures: Dict[QuoteMeasure, Decimal] = {}

            # Parse standard measures
            def _parse_dec(val: Any) -> Optional[Decimal]:
                if val is None:
                    return None
                try:
                    return Decimal(str(val))
                except Exception:
                    return None

            # Last price
            last = _parse_dec(quote_data.get("last_price") or quote_data.get("price"))
            if last is not None:
                measures[QuoteMeasure.LAST] = last

            # Bid / Ask / Mid
            bid = _parse_dec(quote_data.get("bid_price") or quote_data.get("bid"))
            ask = _parse_dec(quote_data.get("ask_price") or quote_data.get("ask"))
            if bid is not None:
                measures[QuoteMeasure.BID] = bid
            if ask is not None:
                measures[QuoteMeasure.ASK] = ask
            if bid is not None and ask is not None:
                measures[QuoteMeasure.MID] = (bid + ask) / Decimal("2")
            elif last is not None:
                # Indicative fallback for mid if last only
                measures[QuoteMeasure.MID] = last

            # Session OHLC
            s_open = _parse_dec(quote_data.get("session_open") or quote_data.get("open"))
            s_high = _parse_dec(quote_data.get("session_high") or quote_data.get("high"))
            s_low = _parse_dec(quote_data.get("session_low") or quote_data.get("low"))
            s_close = _parse_dec(quote_data.get("previous_close") or quote_data.get("close"))

            if s_open is not None:
                measures[QuoteMeasure.OPEN] = s_open
            if s_high is not None:
                measures[QuoteMeasure.HIGH] = s_high
            if s_low is not None:
                measures[QuoteMeasure.LOW] = s_low
            if s_close is not None:
                measures[QuoteMeasure.CLOSE] = s_close

            # NAV & Yield
            nav = _parse_dec(quote_data.get("nav"))
            if nav is not None:
                measures[QuoteMeasure.NAV] = nav

            yld = _parse_dec(quote_data.get("yield") or quote_data.get("yield_pct"))
            if yld is not None:
                measures[QuoteMeasure.YIELD] = yld

            # Reference prices for % change
            references: Dict[ReferenceMethodology, Decimal] = {}
            if s_close is not None and s_close > Decimal("0"):
                references[ReferenceMethodology.SESSION_PREVIOUS_CLOSE] = s_close

            rolling_24h = _parse_dec(quote_data.get("rolling_24h_price") or payload.get("rolling_24h_price"))
            if rolling_24h is not None and rolling_24h > Decimal("0"):
                references[ReferenceMethodology.ROLLING_24H] = rolling_24h

            prev_nav = _parse_dec(quote_data.get("previous_nav") or payload.get("previous_nav"))
            if prev_nav is not None and prev_nav > Decimal("0"):
                references[ReferenceMethodology.PREVIOUS_NAV] = prev_nav

            series_id = str(quote_data.get("series_id") or quote_data.get("symbol") or str(instrument_id))

            return NormalizedObservation(
                instrument_id=instrument_id,
                market_series_identity=series_id,
                event_id=event_id,
                observation_time=observation_time,
                received_at=emitted_at,
                source=provider_key,
                venue=str(venue) if venue else None,
                is_delayed=is_delayed,
                measures=measures,
                reference_prices=references,
            )
        except Exception as e:
            logger.warning("Failed to extract observation from market event envelope: %s", e)
            return None

    async def evaluate_event(
        self,
        event_envelope: Dict[str, Any],
        now: Optional[datetime.datetime] = None,
    ) -> List[UUID]:
        """Evaluates an incoming market event against all matching active alert rules.
        Returns the list of triggered alert IDs.
        """
        if now is None:
            now = datetime.datetime.now(datetime.timezone.utc)

        obs = self.extract_observation(event_envelope)
        if obs is None:
            return []

        # 1. Freshness validation (Requirement 48 & 191)
        age_seconds = (now - obs.observation_time).total_seconds()
        if age_seconds > MAX_STALENESS_SECONDS and not obs.is_delayed:
            logger.info(
                "Stale observation rejected for instrument %s: age=%ss > max=%ss",
                obs.instrument_id,
                age_seconds,
                MAX_STALENESS_SECONDS,
            )
            return []

        triggered_alert_ids: List[UUID] = []

        # 2. Evaluate for each available quote measure
        for measure, value in obs.measures.items():
            # Query active rules indexed by series and measure (Requirement 72)
            rules = await self.repository.get_active_rules_for_series(
                market_series_identity=obs.market_series_identity,
                quote_measure=measure.value,
            )
            if not rules:
                continue

            for rule in rules:
                if not rule.enabled:
                    continue
                eval_state = rule.evaluation_state
                if eval_state is None:
                    continue

                # Event ordering & out-of-order protection (Requirement 84 & 190)
                if (
                    eval_state.last_qualified_observation_time is not None
                    and obs.observation_time < eval_state.last_qualified_observation_time
                ):
                    # Out of order event: reject older event
                    continue

                # Expiration check
                if rule.expires_at is not None and now >= rule.expires_at:
                    rule.enabled = False
                    rule.state = AlertState.EXPIRED.value
                    eval_state.evaluation_status = AlertEvaluationStatus.EXPIRED.value
                    continue

                # Resolve reference price if required
                ref_price: Optional[Decimal] = None
                if rule.reference_methodology:
                    try:
                        ref_enum = ReferenceMethodology(rule.reference_methodology)
                        ref_price = obs.references.get(ref_enum)
                    except Exception:
                        ref_price = None

                prior_side = (
                    ArmedSide(eval_state.armed_side) if eval_state.armed_side else None
                )

                # Pure financial evaluation
                result = evaluate_alert_condition(
                    rule_type=AlertRuleType(rule.rule_type),
                    threshold=Decimal(str(rule.threshold_decimal)),
                    recurrence_policy=RecurrencePolicy(rule.recurrence_policy),
                    current_value=value,
                    reference_price=ref_price,
                    baseline_established=eval_state.baseline_established,
                    prior_armed_side=prior_side,
                    now=now,
                    cooldown_until=eval_state.cooldown_until,
                )

                # Update evaluation state
                eval_state.baseline_established = result.new_baseline_established
                eval_state.armed_side = result.new_armed_side.value
                eval_state.last_qualified_value = float(result.observation_value)
                eval_state.last_qualified_observation_time = obs.observation_time
                eval_state.last_qualified_observation_identity = obs.event_id
                eval_state.updated_at = now

                if not result.triggered:
                    if eval_state.cooldown_until and now < eval_state.cooldown_until:
                        eval_state.evaluation_status = AlertEvaluationStatus.COOLDOWN.value
                    else:
                        eval_state.evaluation_status = AlertEvaluationStatus.ARMED.value
                    continue

                # Alert Triggered!
                # Generate unique trigger deduplication key (Requirement 94)
                dedup_key = (
                    f"trig:{rule.id}:{rule.revision}:{obs.event_id}:{obs.observation_time.isoformat()}"
                )

                trigger = WatchlistAlertTrigger(
                    alert_id=rule.id,
                    rule_revision=rule.revision,
                    owner_user_id=rule.owner_user_id,
                    watchlist_id=rule.watchlist_id,
                    watchlist_item_id=rule.watchlist_item_id,
                    instrument_entity_id=rule.instrument_entity_id,
                    market_series_identity=rule.market_series_identity,
                    symbol=rule.symbol,
                    event_identity=obs.event_id,
                    observation_value=float(result.observation_value),
                    threshold_value=float(result.threshold_value),
                    quote_measure=rule.quote_measure,
                    rule_type=rule.rule_type,
                    source=obs.source,
                    venue=obs.venue,
                    observation_time=obs.observation_time,
                    evaluated_at=now,
                    trigger_dedup_key=dedup_key,
                    notification_status=NotificationDeliveryStatus.PENDING.value,
                )

                # Notification outbox payload
                outbox_payload = {
                    "alert_id": str(rule.id),
                    "watchlist_id": str(rule.watchlist_id),
                    "watchlist_item_id": str(rule.watchlist_item_id),
                    "instrument_entity_id": str(rule.instrument_entity_id),
                    "symbol": rule.symbol,
                    "condition": rule.rule_type,
                    "measure": rule.quote_measure,
                    "threshold": str(result.threshold_value),
                    "threshold_unit": rule.threshold_unit,
                    "observed_value": str(result.observation_value),
                    "observation_time": obs.observation_time.isoformat(),
                    "evaluated_at": now.isoformat(),
                    "source": obs.source,
                    "venue": obs.venue,
                    "is_delayed": obs.is_delayed,
                }

                outbox = WatchlistAlertNotificationOutbox(
                    trigger_id=trigger.id,
                    owner_user_id=rule.owner_user_id,
                    alert_id=rule.id,
                    status=NotificationDeliveryStatus.PENDING.value,
                    payload=outbox_payload,
                    next_attempt_at=now,
                )

                # Update trigger state & cooldown
                eval_state.last_trigger_at = now
                if rule.recurrence_policy == RecurrencePolicy.ONE_SHOT.value:
                    rule.enabled = False
                    rule.state = AlertState.DISABLED.value
                    eval_state.evaluation_status = AlertEvaluationStatus.COMPLETED.value
                else:
                    if rule.cooldown_seconds > 0:
                        eval_state.cooldown_until = now + datetime.timedelta(
                            seconds=rule.cooldown_seconds
                        )
                        eval_state.evaluation_status = AlertEvaluationStatus.COOLDOWN.value
                    else:
                        eval_state.evaluation_status = AlertEvaluationStatus.TRIGGERED.value

                # Atomic commit transaction (Requirement 101)
                try:
                    await self.repository.commit_trigger_transaction(rule, trigger, outbox)
                    await self.session.commit()
                    triggered_alert_ids.append(rule.id)
                    logger.info(
                        "Alert %s triggered for %s at %s (%s %s)",
                        rule.id,
                        rule.symbol,
                        result.observation_value,
                        rule.quote_measure,
                        rule.threshold_unit,
                    )
                except IntegrityError:
                    # Multi-worker idempotency: duplicate event already processed by another worker
                    await self.session.rollback()
                    logger.info("Duplicate alert trigger rejected by dedup constraint: %s", dedup_key)

        return triggered_alert_ids
