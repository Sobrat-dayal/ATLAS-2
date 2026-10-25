"""Async SQLAlchemy Repository for Watchlist Alerts V1 (Stage 80)."""

import datetime
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from atlas.watchlists.alerts.errors import (
    AlertNotFoundError,
    AlertRevisionConflictError,
)
from atlas.watchlists.alerts.models import (
    WatchlistAlertEvaluationState,
    WatchlistAlertNotificationOutbox,
    WatchlistAlertRule,
    WatchlistAlertTrigger,
)
from atlas.watchlists.alerts.schemas import (
    AlertEvaluationStatus,
    AlertState,
)


class WatchlistAlertRepository:
    """Repository handling persistence, optimistic concurrency, and query indexing for Watchlist Alerts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_alert(
        self,
        rule: WatchlistAlertRule,
        initial_state: Optional[WatchlistAlertEvaluationState] = None,
    ) -> WatchlistAlertRule:
        """Atomically persists a new alert rule and its initial evaluation state."""
        self.session.add(rule)
        await self.session.flush()

        if initial_state is None:
            initial_state = WatchlistAlertEvaluationState(
                alert_id=rule.id,
                rule_revision=rule.revision,
                evaluation_status=AlertEvaluationStatus.WAITING_FOR_BASELINE.value,
                baseline_established=False,
            )
        else:
            initial_state.alert_id = rule.id
            initial_state.rule_revision = rule.revision

        self.session.add(initial_state)
        await self.session.flush()
        return rule

    async def get_by_id(
        self,
        alert_id: UUID,
        owner_user_id: Optional[UUID] = None,
    ) -> Optional[WatchlistAlertRule]:
        """Retrieves an alert rule by ID, optionally verifying user ownership."""
        stmt = (
            select(WatchlistAlertRule)
            .options(
                selectinload(WatchlistAlertRule.evaluation_state),
                selectinload(WatchlistAlertRule.triggers),
            )
            .where(WatchlistAlertRule.id == alert_id)
        )
        if owner_user_id is not None:
            stmt = stmt.where(WatchlistAlertRule.owner_user_id == owner_user_id)

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_watchlist(
        self,
        watchlist_id: UUID,
        owner_user_id: UUID,
    ) -> List[WatchlistAlertRule]:
        """Lists all alert rules for a specific watchlist owned by user."""
        stmt = (
            select(WatchlistAlertRule)
            .options(
                selectinload(WatchlistAlertRule.evaluation_state),
                selectinload(WatchlistAlertRule.triggers),
            )
            .where(
                and_(
                    WatchlistAlertRule.watchlist_id == watchlist_id,
                    WatchlistAlertRule.owner_user_id == owner_user_id,
                    WatchlistAlertRule.state != AlertState.DELETED.value,
                )
            )
            .order_by(WatchlistAlertRule.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_user_alerts(
        self,
        owner_user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WatchlistAlertRule], int, int, int]:
        """Lists user alerts with pagination and counts (total, active, paused)."""
        # Count total
        count_stmt = select(func.count(WatchlistAlertRule.id)).where(
            and_(
                WatchlistAlertRule.owner_user_id == owner_user_id,
                WatchlistAlertRule.state != AlertState.DELETED.value,
            )
        )
        total_count = (await self.session.execute(count_stmt)).scalar_one() or 0

        # Count active (enabled)
        active_stmt = select(func.count(WatchlistAlertRule.id)).where(
            and_(
                WatchlistAlertRule.owner_user_id == owner_user_id,
                WatchlistAlertRule.enabled.is_(True),
                WatchlistAlertRule.state == AlertState.ENABLED.value,
            )
        )
        active_count = (await self.session.execute(active_stmt)).scalar_one() or 0

        # Count paused
        paused_stmt = select(func.count(WatchlistAlertRule.id)).where(
            and_(
                WatchlistAlertRule.owner_user_id == owner_user_id,
                WatchlistAlertRule.state == AlertState.PAUSED.value,
            )
        )
        paused_count = (await self.session.execute(paused_stmt)).scalar_one() or 0

        # Fetch page
        stmt = (
            select(WatchlistAlertRule)
            .options(
                selectinload(WatchlistAlertRule.evaluation_state),
                selectinload(WatchlistAlertRule.triggers),
            )
            .where(
                and_(
                    WatchlistAlertRule.owner_user_id == owner_user_id,
                    WatchlistAlertRule.state != AlertState.DELETED.value,
                )
            )
            .order_by(WatchlistAlertRule.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total_count, active_count, paused_count

    async def count_active_for_user(self, owner_user_id: UUID) -> int:
        """Returns the number of currently active alerts for quota validation."""
        stmt = select(func.count(WatchlistAlertRule.id)).where(
            and_(
                WatchlistAlertRule.owner_user_id == owner_user_id,
                WatchlistAlertRule.enabled.is_(True),
                WatchlistAlertRule.state == AlertState.ENABLED.value,
            )
        )
        return (await self.session.execute(stmt)).scalar_one() or 0

    async def count_active_for_instrument(
        self, owner_user_id: UUID, instrument_entity_id: UUID
    ) -> int:
        """Returns the number of active alerts for a specific instrument and user."""
        stmt = select(func.count(WatchlistAlertRule.id)).where(
            and_(
                WatchlistAlertRule.owner_user_id == owner_user_id,
                WatchlistAlertRule.instrument_entity_id == instrument_entity_id,
                WatchlistAlertRule.enabled.is_(True),
                WatchlistAlertRule.state == AlertState.ENABLED.value,
            )
        )
        return (await self.session.execute(stmt)).scalar_one() or 0

    async def update_alert(
        self,
        alert_id: UUID,
        owner_user_id: UUID,
        expected_revision: int,
        threshold: Optional[Decimal] = None,
        cooldown_seconds: Optional[int] = None,
        recurrence_policy: Optional[str] = None,
        expires_at: Optional[datetime.datetime] = None,
    ) -> WatchlistAlertRule:
        """Updates an alert with optimistic concurrency protection and resets baseline if threshold changed."""
        rule = await self.get_by_id(alert_id, owner_user_id=owner_user_id)
        if rule is None or rule.state == AlertState.DELETED.value:
            raise AlertNotFoundError(f"Alert {alert_id} not found.")

        if rule.revision != expected_revision:
            raise AlertRevisionConflictError(
                f"Alert revision conflict: expected {expected_revision}, current is {rule.revision}."
            )

        threshold_changed = False
        if threshold is not None and rule.threshold_decimal != threshold:
            rule.threshold_decimal = float(threshold)
            threshold_changed = True

        if cooldown_seconds is not None:
            rule.cooldown_seconds = cooldown_seconds

        if recurrence_policy is not None:
            rule.recurrence_policy = recurrence_policy

        if expires_at is not None:
            rule.expires_at = expires_at

        rule.revision += 1
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc)

        # Invalidate baseline if rule criteria changed (Requirement 61)
        if threshold_changed and rule.evaluation_state is not None:
            rule.evaluation_state.baseline_established = False
            rule.evaluation_state.armed_side = None
            rule.evaluation_state.evaluation_status = AlertEvaluationStatus.WAITING_FOR_BASELINE.value
            rule.evaluation_state.rule_revision = rule.revision

        await self.session.flush()
        return rule

    async def pause_alert(self, alert_id: UUID, owner_user_id: UUID) -> WatchlistAlertRule:
        """Pauses an alert rule."""
        rule = await self.get_by_id(alert_id, owner_user_id=owner_user_id)
        if rule is None or rule.state == AlertState.DELETED.value:
            raise AlertNotFoundError(f"Alert {alert_id} not found.")

        rule.enabled = False
        rule.state = AlertState.PAUSED.value
        rule.revision += 1
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc)

        if rule.evaluation_state is not None:
            rule.evaluation_state.evaluation_status = AlertEvaluationStatus.DEGRADED.value
            rule.evaluation_state.rule_revision = rule.revision

        await self.session.flush()
        return rule

    async def resume_alert(self, alert_id: UUID, owner_user_id: UUID) -> WatchlistAlertRule:
        """Resumes an alert rule. Safely resets baseline to prevent retroactive triggers (Requirement 60)."""
        rule = await self.get_by_id(alert_id, owner_user_id=owner_user_id)
        if rule is None or rule.state == AlertState.DELETED.value:
            raise AlertNotFoundError(f"Alert {alert_id} not found.")

        rule.enabled = True
        rule.state = AlertState.ENABLED.value
        rule.revision += 1
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc)

        # Safe re-baselining upon resume
        if rule.evaluation_state is not None:
            rule.evaluation_state.baseline_established = False
            rule.evaluation_state.armed_side = None
            rule.evaluation_state.evaluation_status = AlertEvaluationStatus.WAITING_FOR_BASELINE.value
            rule.evaluation_state.rule_revision = rule.revision

        await self.session.flush()
        return rule

    async def delete_alert(self, alert_id: UUID, owner_user_id: UUID) -> bool:
        """Soft-deletes or removes an alert rule."""
        rule = await self.get_by_id(alert_id, owner_user_id=owner_user_id)
        if rule is None or rule.state == AlertState.DELETED.value:
            return False

        rule.enabled = False
        rule.state = AlertState.DELETED.value
        rule.revision += 1
        rule.updated_at = datetime.datetime.now(datetime.timezone.utc)
        await self.session.flush()
        return True

    async def disable_alerts_for_item(self, watchlist_item_id: UUID) -> int:
        """Disables active alerts when a watchlist item is removed (Requirement 15)."""
        stmt = (
            update(WatchlistAlertRule)
            .where(
                and_(
                    WatchlistAlertRule.watchlist_item_id == watchlist_item_id,
                    WatchlistAlertRule.enabled.is_(True),
                )
            )
            .values(
                enabled=False,
                state=AlertState.DISABLED.value,
                revision=WatchlistAlertRule.revision + 1,
                updated_at=datetime.datetime.now(datetime.timezone.utc),
            )
        )
        res = await self.session.execute(stmt)
        return res.rowcount

    async def disable_alerts_for_watchlist(self, watchlist_id: UUID) -> int:
        """Disables active alerts when a parent watchlist is removed (Requirement 16)."""
        stmt = (
            update(WatchlistAlertRule)
            .where(
                and_(
                    WatchlistAlertRule.watchlist_id == watchlist_id,
                    WatchlistAlertRule.enabled.is_(True),
                )
            )
            .values(
                enabled=False,
                state=AlertState.DISABLED.value,
                revision=WatchlistAlertRule.revision + 1,
                updated_at=datetime.datetime.now(datetime.timezone.utc),
            )
        )
        res = await self.session.execute(stmt)
        return res.rowcount

    async def get_active_rules_for_series(
        self,
        market_series_identity: str,
        quote_measure: str,
    ) -> List[WatchlistAlertRule]:
        """Indexed retrieval of active alert rules matching a series and quote measure (Requirement 72)."""
        now = datetime.datetime.now(datetime.timezone.utc)
        stmt = (
            select(WatchlistAlertRule)
            .options(selectinload(WatchlistAlertRule.evaluation_state))
            .where(
                and_(
                    WatchlistAlertRule.market_series_identity == market_series_identity,
                    WatchlistAlertRule.quote_measure == quote_measure,
                    WatchlistAlertRule.enabled.is_(True),
                    WatchlistAlertRule.state == AlertState.ENABLED.value,
                )
            )
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        # Filter out expired rules
        active_rows = []
        for r in rows:
            if r.expires_at is not None and r.expires_at <= now:
                r.enabled = False
                r.state = AlertState.EXPIRED.value
                if r.evaluation_state:
                    r.evaluation_state.evaluation_status = AlertEvaluationStatus.EXPIRED.value
            else:
                active_rows.append(r)
        return active_rows

    async def get_all_active_rules(self) -> List[WatchlistAlertRule]:
        """Returns all currently enabled and active alert rules for worker indexing."""
        now = datetime.datetime.now(datetime.timezone.utc)
        stmt = (
            select(WatchlistAlertRule)
            .options(selectinload(WatchlistAlertRule.evaluation_state))
            .where(
                and_(
                    WatchlistAlertRule.enabled.is_(True),
                    WatchlistAlertRule.state == AlertState.ENABLED.value,
                )
            )
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        active = []
        for r in rows:
            if r.expires_at is not None and r.expires_at <= now:
                r.enabled = False
                r.state = AlertState.EXPIRED.value
                if r.evaluation_state:
                    r.evaluation_state.evaluation_status = AlertEvaluationStatus.EXPIRED.value
            else:
                active.append(r)
        return active

    async def commit_trigger_transaction(
        self,
        rule: WatchlistAlertRule,
        trigger: WatchlistAlertTrigger,
        outbox: WatchlistAlertNotificationOutbox,
    ) -> None:
        """Atomically persists trigger history, updates evaluation state, and queues notification outbox (Requirement 101)."""
        self.session.add(trigger)
        self.session.add(outbox)
        await self.session.flush()

    async def get_trigger_history(
        self,
        owner_user_id: UUID,
        alert_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[WatchlistAlertTrigger], int]:
        """Returns paginated immutable trigger history for user or specific alert."""
        count_stmt = select(func.count(WatchlistAlertTrigger.id)).where(
            WatchlistAlertTrigger.owner_user_id == owner_user_id
        )
        if alert_id is not None:
            count_stmt = count_stmt.where(WatchlistAlertTrigger.alert_id == alert_id)

        total_count = (await self.session.execute(count_stmt)).scalar_one() or 0

        stmt = select(WatchlistAlertTrigger).where(
            WatchlistAlertTrigger.owner_user_id == owner_user_id
        )
        if alert_id is not None:
            stmt = stmt.where(WatchlistAlertTrigger.alert_id == alert_id)

        stmt = stmt.order_by(WatchlistAlertTrigger.created_at.desc()).offset(offset).limit(limit)
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows), total_count

    async def get_pending_outbox_items(
        self, limit: int = 50
    ) -> List[WatchlistAlertNotificationOutbox]:
        """Fetches pending outbox notifications ready for delivery."""
        now = datetime.datetime.now(datetime.timezone.utc)
        stmt = (
            select(WatchlistAlertNotificationOutbox)
            .where(
                and_(
                    WatchlistAlertNotificationOutbox.status.in_(["PENDING", "RETRYING"]),
                    WatchlistAlertNotificationOutbox.next_attempt_at <= now,
                    WatchlistAlertNotificationOutbox.retry_count
                    < WatchlistAlertNotificationOutbox.max_retries,
                )
            )
            .order_by(WatchlistAlertNotificationOutbox.next_attempt_at.asc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows)
