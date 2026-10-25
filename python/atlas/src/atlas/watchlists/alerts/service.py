"""Service layer for Watchlist Alert lifecycle management and validation (Stage 80)."""

import logging
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.entities.models import Entity
from atlas.instruments.models import FinancialInstrument
from atlas.watchlists.alerts.capabilities import (
    MAX_ACTIVE_ALERTS_PER_USER,
    MAX_ALERTS_PER_INSTRUMENT,
    validate_measure_for_asset_class,
)
from atlas.watchlists.alerts.errors import (
    AlertLimitExceededError,
    AlertNotFoundError,
    IncompatibleQuoteMeasureError,
    IncompatibleReferenceMethodError,
    WatchlistItemNotFoundError,
)
from atlas.watchlists.alerts.models import (
    WatchlistAlertEvaluationState,
    WatchlistAlertRule,
)
from atlas.watchlists.alerts.repository import WatchlistAlertRepository
from atlas.watchlists.alerts.schemas import (
    AlertEvaluationStatus,
    AlertHistoryResponse,
    AlertListResponse,
    AlertRuleResponse,
    AlertRuleType,
    AlertState,
    AlertTriggerResponse,
    ComparisonOperator,
    CreateAlertRequest,
    UpdateAlertRequest,
)
from atlas.watchlists.models import Watchlist, WatchlistItem

logger = logging.getLogger(__name__)


class WatchlistAlertService:
    """Manages the lifecycle, quotas, and validation of user-defined Watchlist Alerts."""

    def __init__(
        self,
        session: AsyncSession,
        repository: Optional[WatchlistAlertRepository] = None,
    ) -> None:
        self.session = session
        self.repository = repository or WatchlistAlertRepository(session)

    async def create_alert(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
        request: CreateAlertRequest,
    ) -> AlertRuleResponse:
        """Creates a new validated, persistent alert rule with quota and entitlement enforcement."""
        # 1. Verify parent watchlist ownership
        wl_stmt = select(Watchlist).where(
            Watchlist.id == watchlist_id,
            Watchlist.owner_user_id == owner_user_id,
        )
        watchlist = (await self.session.execute(wl_stmt)).scalar_one_or_none()
        if watchlist is None:
            raise WatchlistItemNotFoundError(f"Watchlist {watchlist_id} not found or not owned by user.")

        # 2. Verify watchlist item belongs to watchlist
        item_stmt = select(WatchlistItem).where(
            WatchlistItem.id == request.watchlist_item_id,
            WatchlistItem.watchlist_id == watchlist_id,
        )
        item = (await self.session.execute(item_stmt)).scalar_one_or_none()
        if item is None:
            raise WatchlistItemNotFoundError(f"Watchlist item {request.watchlist_item_id} not found in watchlist.")

        # 3. Resolve canonical financial instrument and symbol
        inst_stmt = select(FinancialInstrument).where(
            FinancialInstrument.entity_id == item.instrument_entity_id
        )
        instrument = (await self.session.execute(inst_stmt)).scalar_one_or_none()
        if instrument is None:
            raise WatchlistItemNotFoundError(f"Canonical instrument {item.instrument_entity_id} not found.")

        # Resolve symbol from Entity if instrument doesn't have it directly
        symbol = getattr(instrument, "symbol", None)
        if not symbol:
            ent_stmt = select(Entity.display_name).where(Entity.entity_id == item.instrument_entity_id)
            symbol = (await self.session.execute(ent_stmt)).scalar_one_or_none() or "UNKNOWN"

        asset_class = getattr(instrument, "asset_class", "equity") or "equity"

        # 4. Financial qualification: validate measure for asset class
        if not validate_measure_for_asset_class(request.quote_measure, asset_class):
            raise IncompatibleQuoteMeasureError(
                f"Quote measure '{request.quote_measure.value}' is incompatible with asset class '{asset_class}'."
            )

        # 5. Percentage change reference methodology validation
        if request.rule_type in (
            AlertRuleType.PERCENTAGE_CHANGE_ABOVE,
            AlertRuleType.PERCENTAGE_CHANGE_BELOW,
        ):
            if not request.reference_methodology:
                raise IncompatibleReferenceMethodError(
                    "reference_methodology is required for percentage-change alerts."
                )

        # 6. Enforce Quotas (Requirement 138)
        active_user_alerts = await self.repository.count_active_for_user(owner_user_id)
        if active_user_alerts >= MAX_ACTIVE_ALERTS_PER_USER:
            raise AlertLimitExceededError(
                f"Active alert quota of {MAX_ACTIVE_ALERTS_PER_USER} reached for user."
            )

        active_inst_alerts = await self.repository.count_active_for_instrument(
            owner_user_id, item.instrument_entity_id
        )
        if active_inst_alerts >= MAX_ALERTS_PER_INSTRUMENT:
            raise AlertLimitExceededError(
                f"Alert quota of {MAX_ALERTS_PER_INSTRUMENT} reached for instrument {symbol}."
            )

        # Determine default comparison operator
        comparator_map = {
            AlertRuleType.PRICE_ABOVE: ComparisonOperator.GREATER_THAN,
            AlertRuleType.PRICE_BELOW: ComparisonOperator.LESS_THAN,
            AlertRuleType.CROSSING_ABOVE: ComparisonOperator.CROSS_ABOVE,
            AlertRuleType.CROSSING_BELOW: ComparisonOperator.CROSS_BELOW,
            AlertRuleType.PERCENTAGE_CHANGE_ABOVE: ComparisonOperator.CROSS_ABOVE,
            AlertRuleType.PERCENTAGE_CHANGE_BELOW: ComparisonOperator.CROSS_BELOW,
        }
        operator = comparator_map.get(request.rule_type, ComparisonOperator.GREATER_THAN)

        # 7. Construct Alert Rule
        rule = WatchlistAlertRule(
            owner_user_id=owner_user_id,
            watchlist_id=watchlist_id,
            watchlist_item_id=request.watchlist_item_id,
            instrument_entity_id=item.instrument_entity_id,
            market_series_identity=item.market_series_id or symbol,
            symbol=symbol,
            rule_type=request.rule_type.value,
            rule_version=1,
            quote_measure=request.quote_measure.value,
            comparison_operator=operator.value,
            threshold_decimal=float(request.threshold),
            threshold_unit=request.threshold_unit,
            reference_methodology=(
                request.reference_methodology.value if request.reference_methodology else None
            ),
            recurrence_policy=request.recurrence_policy.value,
            cooldown_seconds=request.cooldown_seconds,
            expires_at=request.expires_at,
            enabled=True,
            state=AlertState.ENABLED.value,
            revision=1,
        )

        initial_eval_state = WatchlistAlertEvaluationState(
            rule_revision=1,
            evaluation_status=AlertEvaluationStatus.WAITING_FOR_BASELINE.value,
            baseline_established=False,
        )

        persisted = await self.repository.create_alert(rule, initial_eval_state)
        await self.session.commit()
        return self._to_rule_response(persisted)

    async def get_alert(self, alert_id: UUID, owner_user_id: UUID) -> AlertRuleResponse:
        """Retrieves a single alert rule with current evaluation state."""
        rule = await self.repository.get_by_id(alert_id, owner_user_id=owner_user_id)
        if rule is None or rule.state == AlertState.DELETED.value:
            raise AlertNotFoundError(f"Alert {alert_id} not found.")
        return self._to_rule_response(rule)

    async def list_watchlist_alerts(
        self, watchlist_id: UUID, owner_user_id: UUID
    ) -> List[AlertRuleResponse]:
        """Lists all alerts for a specific watchlist."""
        rules = await self.repository.list_by_watchlist(watchlist_id, owner_user_id)
        return [self._to_rule_response(r) for r in rules]

    async def list_user_alerts(
        self,
        owner_user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> AlertListResponse:
        """Paginated list of all alerts belonging to user across all watchlists."""
        rules, total, active, paused = await self.repository.list_user_alerts(
            owner_user_id=owner_user_id, limit=limit, offset=offset
        )
        return AlertListResponse(
            items=[self._to_rule_response(r) for r in rules],
            total_count=total,
            active_count=active,
            paused_count=paused,
        )

    async def update_alert(
        self,
        alert_id: UUID,
        owner_user_id: UUID,
        request: UpdateAlertRequest,
    ) -> AlertRuleResponse:
        """Updates an alert rule with optimistic concurrency control."""
        updated = await self.repository.update_alert(
            alert_id=alert_id,
            owner_user_id=owner_user_id,
            expected_revision=request.expected_revision,
            threshold=request.threshold,
            cooldown_seconds=request.cooldown_seconds,
            recurrence_policy=(
                request.recurrence_policy.value if request.recurrence_policy else None
            ),
            expires_at=request.expires_at,
        )
        await self.session.commit()
        return self._to_rule_response(updated)

    async def pause_alert(self, alert_id: UUID, owner_user_id: UUID) -> AlertRuleResponse:
        """Pauses alert evaluation."""
        paused = await self.repository.pause_alert(alert_id, owner_user_id)
        await self.session.commit()
        return self._to_rule_response(paused)

    async def resume_alert(self, alert_id: UUID, owner_user_id: UUID) -> AlertRuleResponse:
        """Resumes alert evaluation and safely resets baseline to prevent false crossings."""
        resumed = await self.repository.resume_alert(alert_id, owner_user_id)
        await self.session.commit()
        return self._to_rule_response(resumed)

    async def delete_alert(self, alert_id: UUID, owner_user_id: UUID) -> bool:
        """Soft-deletes an alert rule."""
        success = await self.repository.delete_alert(alert_id, owner_user_id)
        if not success:
            raise AlertNotFoundError(f"Alert {alert_id} not found.")
        await self.session.commit()
        return True

    async def get_trigger_history(
        self,
        owner_user_id: UUID,
        alert_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AlertHistoryResponse:
        """Returns paginated immutable alert trigger history."""
        triggers, total = await self.repository.get_trigger_history(
            owner_user_id=owner_user_id,
            alert_id=alert_id,
            limit=limit,
            offset=offset,
        )
        items = [
            AlertTriggerResponse(
                id=t.id,
                alert_id=t.alert_id,
                rule_revision=t.rule_revision,
                owner_user_id=t.owner_user_id,
                watchlist_id=t.watchlist_id,
                watchlist_item_id=t.watchlist_item_id,
                instrument_entity_id=t.instrument_entity_id,
                market_series_identity=t.market_series_identity,
                symbol=t.symbol,
                event_identity=t.event_identity,
                observation_value=Decimal(str(t.observation_value)),
                threshold_value=Decimal(str(t.threshold_value)),
                quote_measure=t.quote_measure,
                rule_type=t.rule_type,
                source=t.source,
                venue=t.venue,
                observation_time=t.observation_time,
                evaluated_at=t.evaluated_at,
                trigger_dedup_key=t.trigger_dedup_key,
                notification_status=t.notification_status,
                notification_id=t.notification_id,
                notification_error=t.notification_error,
                created_at=t.created_at,
            )
            for t in triggers
        ]
        next_cursor = str(offset + limit) if offset + limit < total else None
        return AlertHistoryResponse(
            items=items,
            total_count=total,
            next_cursor=next_cursor,
        )

    def _to_rule_response(self, rule: WatchlistAlertRule) -> AlertRuleResponse:
        """Maps SQLAlchemy WatchlistAlertRule model to Pydantic AlertRuleResponse."""
        eval_resp = None
        if rule.evaluation_state is not None:
            s = rule.evaluation_state
            eval_resp = {
                "rule_revision": s.rule_revision,
                "evaluation_status": s.evaluation_status,
                "armed_side": s.armed_side,
                "last_qualified_value": (
                    Decimal(str(s.last_qualified_value))
                    if s.last_qualified_value is not None
                    else None
                ),
                "last_qualified_observation_time": s.last_qualified_observation_time,
                "last_trigger_at": s.last_trigger_at,
                "cooldown_until": s.cooldown_until,
                "baseline_established": s.baseline_established,
                "updated_at": s.updated_at,
            }

        last_trigger = None
        if rule.triggers:
            t = rule.triggers[0]
            last_trigger = {
                "id": t.id,
                "alert_id": t.alert_id,
                "rule_revision": t.rule_revision,
                "owner_user_id": t.owner_user_id,
                "watchlist_id": t.watchlist_id,
                "watchlist_item_id": t.watchlist_item_id,
                "instrument_entity_id": t.instrument_entity_id,
                "market_series_identity": t.market_series_identity,
                "symbol": t.symbol,
                "event_identity": t.event_identity,
                "observation_value": Decimal(str(t.observation_value)),
                "threshold_value": Decimal(str(t.threshold_value)),
                "quote_measure": t.quote_measure,
                "rule_type": t.rule_type,
                "source": t.source,
                "venue": t.venue,
                "observation_time": t.observation_time,
                "evaluated_at": t.evaluated_at,
                "trigger_dedup_key": t.trigger_dedup_key,
                "notification_status": t.notification_status,
                "notification_id": t.notification_id,
                "notification_error": t.notification_error,
                "created_at": t.created_at,
            }

        return AlertRuleResponse(
            id=rule.id,
            owner_user_id=rule.owner_user_id,
            watchlist_id=rule.watchlist_id,
            watchlist_item_id=rule.watchlist_item_id,
            instrument_entity_id=rule.instrument_entity_id,
            market_series_identity=rule.market_series_identity,
            symbol=rule.symbol,
            rule_type=rule.rule_type,
            rule_version=rule.rule_version,
            quote_measure=rule.quote_measure,
            comparison_operator=rule.comparison_operator,
            threshold_decimal=Decimal(str(rule.threshold_decimal)),
            threshold_unit=rule.threshold_unit,
            reference_methodology=rule.reference_methodology,
            recurrence_policy=rule.recurrence_policy,
            cooldown_seconds=rule.cooldown_seconds,
            expires_at=rule.expires_at,
            enabled=rule.enabled,
            state=rule.state,
            revision=rule.revision,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            evaluation_state=eval_resp,
            last_trigger=last_trigger,
        )
