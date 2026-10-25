"""Reliable asynchronous notification dispatch worker integrating with Stage 49 (Stage 80).

Features:
- Consumes from `watchlist_alert_notification_outbox`.
- Formats structured, verified financial observation messages.
- Discloses market data freshness and delayed-data status.
- Provides deep links back to the Watchlist item and instrument.
- Idempotent delivery using `dedupe_key = f"alert_trigger:{trigger_id}"`.
- Bounded retries with exponential backoff.
"""

import datetime
import logging
from typing import Optional

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from atlas.notifications.enums import (
    NotificationActionKind,
    NotificationCategory,
    NotificationSeverity,
)
from atlas.notifications.schemas import CreateNotification
from atlas.notifications.service import NotificationService
from atlas.watchlists.alerts.models import (
    WatchlistAlertTrigger,
)
from atlas.watchlists.alerts.repository import WatchlistAlertRepository
from atlas.watchlists.alerts.schemas import NotificationDeliveryStatus

logger = logging.getLogger(__name__)


class AlertNotificationDispatcher:
    """Consumes pending alert outbox records and delivers notifications to the Stage 49 Notification Center."""

    def __init__(
        self,
        session: AsyncSession,
        repository: Optional[WatchlistAlertRepository] = None,
        notification_service: Optional[NotificationService] = None,
    ) -> None:
        self.session = session
        self.repository = repository or WatchlistAlertRepository(session)
        self.notification_service = notification_service or NotificationService(session)

    async def dispatch_pending(self, limit: int = 50) -> int:
        """Polls and dispatches pending alert notifications. Returns count of dispatched records."""
        outbox_items = await self.repository.get_pending_outbox_items(limit=limit)
        if not outbox_items:
            return 0

        dispatched_count = 0
        now = datetime.datetime.now(datetime.timezone.utc)

        for item in outbox_items:
            payload = item.payload
            symbol = payload.get("symbol", "Instrument")
            condition = payload.get("condition", "Alert")
            threshold = payload.get("threshold", "")
            unit = payload.get("threshold_unit", "")
            observed = payload.get("observed_value", "")
            measure = payload.get("measure", "LAST")
            obs_time = payload.get("observation_time", "")
            eval_time = payload.get("evaluated_at", "")
            source = payload.get("source", "Canonical")
            venue = payload.get("venue")
            is_delayed = payload.get("is_delayed", False)

            # Format human-friendly condition description
            cond_map = {
                "PRICE_ABOVE": "above",
                "PRICE_BELOW": "below",
                "CROSSING_ABOVE": "crossed above",
                "CROSSING_BELOW": "crossed below",
                "PERCENTAGE_CHANGE_ABOVE": "% change crossed above",
                "PERCENTAGE_CHANGE_BELOW": "% change crossed below",
            }
            verb = cond_map.get(condition, condition)

            title = f"Alert: {symbol} {verb} {threshold} {unit}".strip()

            feed_label = "Delayed" if is_delayed else "Realtime"
            venue_label = f" ({venue})" if venue else ""

            # Structured, verified financial message (Requirement 111 & 112)
            message = (
                f"Financial condition verified:\n"
                f"• Instrument: {symbol}\n"
                f"• Condition: {verb} {threshold} {unit}\n"
                f"• Observed Value: {observed} {unit} ({measure})\n"
                f"• Market Observation: {obs_time}\n"
                f"• Evaluated: {eval_time}\n"
                f"• Source: {source}{venue_label} [{feed_label}]"
            )

            # Deep link to watchlists module (Requirement 114)
            action_route = "/watchlists"

            create_dto = CreateNotification(
                recipient_user_id=item.owner_user_id,
                category=NotificationCategory.MARKET,
                severity=NotificationSeverity.INFO,
                title=title[:160],
                message=message[:2000],
                producer_key="alerts.watchlist_evaluator",
                dedupe_key=f"alert_trigger:{item.trigger_id}",
                action_kind=NotificationActionKind.INTERNAL_ROUTE,
                action_route=action_route,
                action_entity_id=None,
            )

            try:
                notif_response = await self.notification_service.create_notification(create_dto)

                # Mark Outbox as DELIVERED
                item.status = NotificationDeliveryStatus.DELIVERED.value
                item.last_attempt_at = now
                item.updated_at = now

                # Update Trigger record
                trig_stmt = (
                    update(WatchlistAlertTrigger)
                    .where(WatchlistAlertTrigger.id == item.trigger_id)
                    .values(
                        notification_status=NotificationDeliveryStatus.DELIVERED.value,
                        notification_id=notif_response.notification_id,
                        notification_error=None,
                    )
                )
                await self.session.execute(trig_stmt)
                await self.session.commit()
                dispatched_count += 1
                logger.info("Alert notification delivered for trigger %s", item.trigger_id)

            except Exception as e:
                logger.warning(
                    "Notification dispatch failed for trigger %s (attempt %s/%s): %s",
                    item.trigger_id,
                    item.retry_count + 1,
                    item.max_retries,
                    e,
                )
                item.retry_count += 1
                item.last_attempt_at = now
                item.error_message = str(e)[:1000]
                item.updated_at = now

                if item.retry_count >= item.max_retries:
                    item.status = NotificationDeliveryStatus.FAILED.value
                    trig_status = NotificationDeliveryStatus.FAILED.value
                else:
                    item.status = NotificationDeliveryStatus.RETRYING.value
                    trig_status = NotificationDeliveryStatus.RETRYING.value
                    # Exponential backoff: 5s * (2 ^ retry)
                    backoff_secs = 5 * (2 ** min(item.retry_count, 6))
                    item.next_attempt_at = now + datetime.timedelta(seconds=backoff_secs)

                trig_stmt = (
                    update(WatchlistAlertTrigger)
                    .where(WatchlistAlertTrigger.id == item.trigger_id)
                    .values(
                        notification_status=trig_status,
                        notification_error=str(e)[:500],
                    )
                )
                await self.session.execute(trig_stmt)
                await self.session.commit()

        return dispatched_count
