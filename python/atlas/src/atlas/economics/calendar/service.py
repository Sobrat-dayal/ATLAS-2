"""Domain Service for Global Economic Calendar (Stage 92)."""

import uuid
import zoneinfo
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from .enums import (
    AlertStatus,
    EconomicEventCategory,
    EconomicEventKind,
    EconomicEventStatus,
    EventAlertType,
    SurpriseDirection,
)
from .errors import (
    EconomicEventAlertQuotaExceededError,
    EconomicEventDateRangeInvalidError,
    EconomicEventTimezoneInvalidError,
)
from .models import (
    AlertDeliveryIntent,
    EconomicCalendarEvent,
    EconomicSurpriseMetric,
    UserEventAlert,
)
from .repository import EconomicCalendarRepository
from .schemas import (
    AlertDeliveryIntentDTO,
    CalendarQueryContextDTO,
    ConsensusSnapshotDTO,
    CreateEventAlertRequestDTO,
    EconomicCalendarCoverageDTO,
    EconomicCalendarEventDetailDTO,
    EconomicCalendarEventDTO,
    EconomicCalendarResponseDTO,
    EconomicEventObservationDTO,
    EconomicSurpriseMetricDTO,
    ScheduleRevisionDTO,
    UpdateEventAlertRequestDTO,
    UserEventAlertDTO,
)


class EconomicCalendarService:
    """Service orchestrating economic calendar discovery, filtering, surprises, and alerts."""

    MAX_USER_ALERTS = 100

    def __init__(self, repo: Optional[EconomicCalendarRepository] = None):
        self.repo = repo or EconomicCalendarRepository()

    # -------------------------------------------------------------------------
    # Timezone Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_timezone(tz_name: str) -> zoneinfo.ZoneInfo:
        """Validates that a timezone is a valid IANA timezone name."""
        try:
            return zoneinfo.ZoneInfo(tz_name)
        except Exception:
            raise EconomicEventTimezoneInvalidError(tz_name)

    @classmethod
    def format_event_display_time(cls, utc_time: datetime, tz_name: str) -> str:
        """Converts UTC datetime to local civil display string."""
        tz = cls.validate_timezone(tz_name)
        local_dt = utc_time.astimezone(tz)
        return local_dt.strftime("%Y-%m-%d %H:%M")

    # -------------------------------------------------------------------------
    # Surprise Engine
    # -------------------------------------------------------------------------

    @staticmethod
    def calculate_surprise(
        event_id: str,
        economic_series_id: str,
        actual_value: Decimal,
        consensus_value: Decimal,
        unit: str,
    ) -> EconomicSurpriseMetric:
        """Computes statistical difference between actual statistical release and pre-release consensus."""
        diff = actual_value - consensus_value

        pct_diff: Optional[Decimal] = None
        bps_diff: Optional[Decimal] = None
        rel_diff: Optional[Decimal] = None

        if "%" in unit or "pct" in unit.lower():
            pct_diff = diff
            # If policy rate series, calculate basis points: 0.25% diff = 25 bps
            if any(term in economic_series_id.upper() for term in ("RATE", "FUNDS", "REPO", "DFR", "LPR")):
                bps_diff = diff * Decimal("100")

        if consensus_value != Decimal("0"):
            rel_diff = (diff / abs(consensus_value)) * Decimal("100")

        if diff > Decimal("0"):
            direction = SurpriseDirection.ABOVE_CONSENSUS
        elif diff < Decimal("0"):
            direction = SurpriseDirection.BELOW_CONSENSUS
        else:
            direction = SurpriseDirection.IN_LINE

        return EconomicSurpriseMetric(
            event_id=event_id,
            economic_series_id=economic_series_id,
            actual_value=actual_value,
            consensus_value=consensus_value,
            unit=unit,
            surprise_value=diff,
            percentage_point_diff=pct_diff,
            basis_point_diff=bps_diff,
            relative_surprise_pct=rel_diff,
            direction=direction,
        )

    # -------------------------------------------------------------------------
    # DTO Transformation Helpers
    # -------------------------------------------------------------------------

    def _transform_event_dto(
        self, event: EconomicCalendarEvent, display_timezone: str
    ) -> EconomicCalendarEventDTO:
        display_str = self.format_event_display_time(event.scheduled_start, display_timezone)

        # Primary observation (first in list if any)
        primary_obs = event.observations[0] if event.observations else None
        primary_cs = event.consensus_snapshots[0] if event.consensus_snapshots else None

        actual_val = float(primary_obs.actual_value) if primary_obs and primary_obs.actual_value is not None else None
        consensus_val = float(primary_cs.consensus_value) if primary_cs and primary_cs.consensus_value is not None else None
        prev_val = float(primary_obs.previous_value) if primary_obs and primary_obs.previous_value is not None else None
        rev_prev_val = float(primary_obs.revised_previous_value) if primary_obs and primary_obs.revised_previous_value is not None else None
        unit_str = primary_obs.unit if primary_obs else (primary_cs.unit if primary_cs else None)

        surprise_dto: Optional[EconomicSurpriseMetricDTO] = None
        if primary_obs and primary_cs and primary_obs.actual_value is not None:
            metric = self.calculate_surprise(
                event.event_id,
                primary_obs.economic_series_id,
                primary_obs.actual_value,
                primary_cs.consensus_value,
                primary_obs.unit,
            )
            surprise_dto = EconomicSurpriseMetricDTO(
                event_id=metric.event_id,
                economic_series_id=metric.economic_series_id,
                actual_value=float(metric.actual_value),
                consensus_value=float(metric.consensus_value),
                unit=metric.unit,
                surprise_value=float(metric.surprise_value),
                percentage_point_diff=float(metric.percentage_point_diff) if metric.percentage_point_diff is not None else None,
                basis_point_diff=float(metric.basis_point_diff) if metric.basis_point_diff is not None else None,
                relative_surprise_pct=float(metric.relative_surprise_pct) if metric.relative_surprise_pct is not None else None,
                direction=metric.direction,
                methodology_version=metric.methodology_version,
            )

        return EconomicCalendarEventDTO(
            event_id=event.event_id,
            official_event_identifier=event.official_event_identifier,
            event_kind=event.event_kind,
            category=event.category,
            release_family_id=event.release_family_id,
            title=event.title,
            geographic_entity_ids=event.geographic_entity_ids,
            institution_entity_id=event.institution_entity_id,
            scheduled_start=event.scheduled_start,
            scheduled_end=event.scheduled_end,
            scheduled_start_display=display_str,
            display_timezone=display_timezone,
            schedule_precision=event.schedule_precision,
            source_timezone=event.source_timezone,
            reference_period=event.reference_period,
            release_stage=event.release_stage,
            event_status=event.event_status,
            importance=event.importance,
            indicators=event.indicators,
            official_source_id=event.official_source_id,
            official_source_name=event.official_source_name,
            official_source_url=event.official_source_url,
            published_at=event.published_at,
            is_verified=event.is_verified,
            primary_series_id=primary_obs.economic_series_id if primary_obs else None,
            actual_value=actual_val,
            consensus_value=consensus_val,
            previous_value=prev_val,
            revised_previous_value=rev_prev_val,
            unit=unit_str,
            surprise=surprise_dto,
        )

    # -------------------------------------------------------------------------
    # Calendar Query Engine
    # -------------------------------------------------------------------------

    def query_calendar(
        self,
        view_preset: str = "all",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        geography_ids: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        importance_levels: Optional[List[str]] = None,
        event_statuses: Optional[List[str]] = None,
        search: Optional[str] = None,
        display_timezone: str = "UTC",
        current_user_id: Optional[str] = None,
        reference_time: Optional[datetime] = None,
    ) -> EconomicCalendarResponseDTO:
        """Executes multi-dimensional calendar queries with timezone-aware civil date grouping."""
        tz = self.validate_timezone(display_timezone)
        now_dt = reference_time or datetime.now(timezone.utc)
        local_now = now_dt.astimezone(tz)
        local_today = local_now.date()

        # Resolve date boundaries based on view preset
        calc_start_date: Optional[date] = None
        calc_end_date: Optional[date] = None

        if view_preset == "today":
            calc_start_date = local_today
            calc_end_date = local_today
        elif view_preset == "tomorrow":
            calc_start_date = local_today + timedelta(days=1)
            calc_end_date = local_today + timedelta(days=1)
        elif view_preset == "this_week":
            # Monday to Sunday
            start_offset = local_today.weekday()
            calc_start_date = local_today - timedelta(days=start_offset)
            calc_end_date = calc_start_date + timedelta(days=6)
        elif view_preset == "next_week":
            start_offset = local_today.weekday()
            calc_start_date = local_today - timedelta(days=start_offset) + timedelta(days=7)
            calc_end_date = calc_start_date + timedelta(days=6)
        elif start_date or end_date:
            try:
                if start_date:
                    calc_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                if end_date:
                    calc_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise EconomicEventDateRangeInvalidError("Date strings must follow YYYY-MM-DD format.")

        events = self.repo.list_events()
        filtered: List[EconomicCalendarEvent] = []

        # User alerts set for "my_alerts" preset
        user_alert_event_ids = set()
        if current_user_id:
            user_alert_event_ids = {a.event_id for a in self.repo.list_user_alerts(current_user_id) if a.is_enabled}

        for ev in events:
            # Timezone localized civil date
            ev_local_date = ev.scheduled_start.astimezone(tz).date()

            # Date window filter
            if calc_start_date and ev_local_date < calc_start_date:
                continue
            if calc_end_date and ev_local_date > calc_end_date:
                continue

            # Presets
            if view_preset == "upcoming" and ev.scheduled_start < now_dt:
                continue
            if view_preset == "released" and ev.event_status != EconomicEventStatus.RELEASE_VERIFIED:
                continue
            if view_preset == "central_bank" and ev.event_kind not in (
                EconomicEventKind.CENTRAL_BANK_POLICY_MEETING,
                EconomicEventKind.CENTRAL_BANK_POLICY_DECISION,
            ):
                continue
            if view_preset == "my_alerts" and ev.event_id not in user_alert_event_ids:
                continue

            # Geography filter
            if geography_ids and not any(g in ev.geographic_entity_ids for g in geography_ids):
                continue

            # Category filter
            if categories and ev.category.value not in categories and ev.category not in categories:
                continue

            # Importance filter
            if importance_levels and ev.importance.value not in importance_levels and ev.importance not in importance_levels:
                continue

            # Status filter
            if event_statuses and ev.event_status.value not in event_statuses and ev.event_status not in event_statuses:
                continue

            # Text Search
            if search:
                s_lower = search.lower()
                matched = (
                    s_lower in ev.title.lower()
                    or s_lower in ev.official_event_identifier.lower()
                    or any(s_lower in ind.lower() for ind in ev.indicators)
                )
                if not matched:
                    continue

            filtered.append(ev)

        # Sort chronologically by scheduled_start
        filtered.sort(key=lambda x: x.scheduled_start)

        event_dtos = [self._transform_event_dto(e, display_timezone) for e in filtered]

        context = CalendarQueryContextDTO(
            display_timezone=display_timezone,
            start_date=calc_start_date.strftime("%Y-%m-%d") if calc_start_date else None,
            end_date=calc_end_date.strftime("%Y-%m-%d") if calc_end_date else None,
            view_preset=view_preset,
            total_events=len(event_dtos),
        )

        all_cats = [c.value for c in EconomicEventCategory]
        all_geos = ["US", "EU", "GB", "JP", "IN", "CN"]

        return EconomicCalendarResponseDTO(
            context=context,
            events=event_dtos,
            categories=all_cats,
            supported_geographies=all_geos,
        )

    # -------------------------------------------------------------------------
    # Event Detail View
    # -------------------------------------------------------------------------

    def get_event_detail(self, event_id: str, display_timezone: str = "UTC") -> EconomicCalendarEventDetailDTO:
        event = self.repo.get_event(event_id)
        event_dto = self._transform_event_dto(event, display_timezone)

        observations_dto = [
            EconomicEventObservationDTO(
                observation_id=o.observation_id,
                event_id=o.event_id,
                economic_series_id=o.economic_series_id,
                indicator_name=o.indicator_name,
                reference_period=o.reference_period,
                actual_value=float(o.actual_value) if o.actual_value is not None else None,
                previous_value=float(o.previous_value) if o.previous_value is not None else None,
                revised_previous_value=float(o.revised_previous_value) if o.revised_previous_value is not None else None,
                unit=o.unit,
                release_stage=o.release_stage,
                source_revision=o.source_revision,
            )
            for o in event.observations
        ]

        consensus_dto = [
            ConsensusSnapshotDTO(
                snapshot_id=c.snapshot_id,
                event_id=c.event_id,
                economic_series_id=c.economic_series_id,
                consensus_value=float(c.consensus_value),
                unit=c.unit,
                aggregation_method=c.aggregation_method,
                contributor_count=c.contributor_count,
                snapshot_timestamp=c.snapshot_timestamp,
                provider_name=c.provider_name,
            )
            for c in event.consensus_snapshots
        ]

        revisions_dto = [
            ScheduleRevisionDTO(
                revision_id=r.revision_id,
                event_id=r.event_id,
                previous_scheduled_time=r.previous_scheduled_time,
                new_scheduled_time=r.new_scheduled_time,
                reason=r.reason,
                revised_at=r.revised_at,
            )
            for r in event.schedule_revisions
        ]

        # Calculate surprise for all matching observation/consensus pairs
        surprises_dto: List[EconomicSurpriseMetricDTO] = []
        for obs in event.observations:
            matching_cs = next((c for c in event.consensus_snapshots if c.economic_series_id == obs.economic_series_id), None)
            if matching_cs and obs.actual_value is not None:
                s_metric = self.calculate_surprise(
                    event.event_id,
                    obs.economic_series_id,
                    obs.actual_value,
                    matching_cs.consensus_value,
                    obs.unit,
                )
                surprises_dto.append(
                    EconomicSurpriseMetricDTO(
                        event_id=s_metric.event_id,
                        economic_series_id=s_metric.economic_series_id,
                        actual_value=float(s_metric.actual_value),
                        consensus_value=float(s_metric.consensus_value),
                        unit=s_metric.unit,
                        surprise_value=float(s_metric.surprise_value),
                        percentage_point_diff=float(s_metric.percentage_point_diff) if s_metric.percentage_point_diff is not None else None,
                        basis_point_diff=float(s_metric.basis_point_diff) if s_metric.basis_point_diff is not None else None,
                        relative_surprise_pct=float(s_metric.relative_surprise_pct) if s_metric.relative_surprise_pct is not None else None,
                        direction=s_metric.direction,
                        methodology_version=s_metric.methodology_version,
                    )
                )

        return EconomicCalendarEventDetailDTO(
            event=event_dto,
            observations=observations_dto,
            consensus_snapshots=consensus_dto,
            schedule_revisions=revisions_dto,
            surprises=surprises_dto,
            notes=event.notes,
            provenance_id=event.provenance_id,
            source_revision=event.source_revision,
        )

    # -------------------------------------------------------------------------
    # User Event Alerts & Notification Center Integration
    # -------------------------------------------------------------------------

    def create_alert(self, user_id: str, request: CreateEventAlertRequestDTO) -> UserEventAlertDTO:
        # Validate event exists
        event = self.repo.get_event(request.event_id)

        # Check quota
        user_alerts = self.repo.list_user_alerts(user_id)
        if len(user_alerts) >= self.MAX_USER_ALERTS:
            raise EconomicEventAlertQuotaExceededError(self.MAX_USER_ALERTS)

        alert_id = f"alert-{uuid.uuid4().hex[:12]}"
        idempotency_key = f"alert-{user_id}-{request.event_id}-{request.alert_type.value}"

        alert = UserEventAlert(
            alert_id=alert_id,
            owner_user_id=user_id,
            event_id=request.event_id,
            alert_type=request.alert_type,
            reminder_offset_minutes=request.reminder_offset_minutes,
            is_enabled=request.is_enabled,
            status=AlertStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            idempotency_key=idempotency_key,
        )
        self.repo.save_alert(alert)

        return UserEventAlertDTO(
            alert_id=alert.alert_id,
            owner_user_id=alert.owner_user_id,
            event_id=alert.event_id,
            event_title=event.title,
            scheduled_time=event.scheduled_start,
            alert_type=alert.alert_type,
            reminder_offset_minutes=alert.reminder_offset_minutes,
            is_enabled=alert.is_enabled,
            status=alert.status,
            created_at=alert.created_at,
            last_triggered_at=alert.last_triggered_at,
            trigger_count=alert.trigger_count,
        )

    def list_alerts(self, user_id: str) -> List[UserEventAlertDTO]:
        alerts = self.repo.list_user_alerts(user_id)
        results: List[UserEventAlertDTO] = []
        for a in alerts:
            try:
                event = self.repo.get_event(a.event_id)
                results.append(
                    UserEventAlertDTO(
                        alert_id=a.alert_id,
                        owner_user_id=a.owner_user_id,
                        event_id=a.event_id,
                        event_title=event.title,
                        scheduled_time=event.scheduled_start,
                        alert_type=a.alert_type,
                        reminder_offset_minutes=a.reminder_offset_minutes,
                        is_enabled=a.is_enabled,
                        status=a.status,
                        created_at=a.created_at,
                        last_triggered_at=a.last_triggered_at,
                        trigger_count=a.trigger_count,
                    )
                )
            except Exception:
                continue
        return results

    def get_alert(self, alert_id: str, user_id: str) -> UserEventAlertDTO:
        alert = self.repo.get_alert(alert_id, user_id)
        event = self.repo.get_event(alert.event_id)
        return UserEventAlertDTO(
            alert_id=alert.alert_id,
            owner_user_id=alert.owner_user_id,
            event_id=alert.event_id,
            event_title=event.title,
            scheduled_time=event.scheduled_start,
            alert_type=alert.alert_type,
            reminder_offset_minutes=alert.reminder_offset_minutes,
            is_enabled=alert.is_enabled,
            status=alert.status,
            created_at=alert.created_at,
            last_triggered_at=alert.last_triggered_at,
            trigger_count=alert.trigger_count,
        )

    def update_alert(self, alert_id: str, user_id: str, request: UpdateEventAlertRequestDTO) -> UserEventAlertDTO:
        alert = self.repo.get_alert(alert_id, user_id)
        if request.reminder_offset_minutes is not None:
            alert.reminder_offset_minutes = request.reminder_offset_minutes
        if request.is_enabled is not None:
            alert.is_enabled = request.is_enabled
        if request.status is not None:
            alert.status = request.status
        self.repo.save_alert(alert)
        return self.get_alert(alert_id, user_id)

    def delete_alert(self, alert_id: str, user_id: str) -> bool:
        return self.repo.delete_alert(alert_id, user_id)

    def evaluate_alerts(self, as_of: Optional[datetime] = None) -> List[AlertDeliveryIntentDTO]:
        """Simulates alert evaluation worker dispatched against release events."""
        now_dt = as_of or datetime.now(timezone.utc)
        dispatched: List[AlertDeliveryIntentDTO] = []

        for alert in list(self.repo._alerts.values()):
            if not alert.is_enabled or alert.status != AlertStatus.ACTIVE:
                continue

            try:
                event = self.repo.get_event(alert.event_id)
            except Exception:
                continue

            should_trigger = False
            title = ""
            body = ""

            if alert.alert_type == EventAlertType.BEFORE_SCHEDULED_RELEASE:
                trigger_time = event.scheduled_start - timedelta(minutes=alert.reminder_offset_minutes)
                if now_dt >= trigger_time and alert.trigger_count == 0:
                    should_trigger = True
                    title = f"Upcoming Release Reminder: {event.title}"
                    body = f"Scheduled for publication in {alert.reminder_offset_minutes} minutes ({event.official_source_name})."

            elif alert.alert_type == EventAlertType.WHEN_RELEASE_VERIFIED:
                if event.event_status == EconomicEventStatus.RELEASE_VERIFIED and alert.trigger_count == 0:
                    should_trigger = True
                    obs_summary = ""
                    if event.observations and event.observations[0].actual_value is not None:
                        obs = event.observations[0]
                        obs_summary = f" Actual: {obs.actual_value} {obs.unit}."
                    title = f"Release Verified: {event.title}"
                    body = f"Official macroeconomic statistics have been published by {event.official_source_name}.{obs_summary}"

            elif alert.alert_type == EventAlertType.WHEN_SCHEDULE_CHANGES:
                if event.event_status == EconomicEventStatus.RESCHEDULED and len(event.schedule_revisions) > alert.trigger_count:
                    should_trigger = True
                    rev = event.schedule_revisions[-1]
                    title = f"Schedule Changed: {event.title}"
                    body = f"Event rescheduled to {rev.new_scheduled_time.strftime('%Y-%m-%d %H:%M UTC')}. Reason: {rev.reason or 'Official revision'}."

            if should_trigger:
                intent_id = f"intent-{uuid.uuid4().hex[:12]}"
                intent = AlertDeliveryIntent(
                    intent_id=intent_id,
                    alert_id=alert.alert_id,
                    owner_user_id=alert.owner_user_id,
                    event_id=event.event_id,
                    title=title,
                    body=body,
                    scheduled_for=now_dt,
                    delivered_at=now_dt,
                    is_delivered=True,
                )
                self.repo.record_delivery_intent(intent)

                alert.last_triggered_at = now_dt
                alert.trigger_count += 1
                if alert.alert_type in (EventAlertType.BEFORE_SCHEDULED_RELEASE, EventAlertType.WHEN_RELEASE_VERIFIED):
                    alert.status = AlertStatus.FIRED

                dispatched.append(
                    AlertDeliveryIntentDTO(
                        intent_id=intent.intent_id,
                        alert_id=intent.alert_id,
                        owner_user_id=intent.owner_user_id,
                        event_id=intent.event_id,
                        title=intent.title,
                        body=intent.body,
                        scheduled_for=intent.scheduled_for,
                        delivered_at=intent.delivered_at,
                        is_delivered=intent.is_delivered,
                    )
                )

        return dispatched

    def list_delivery_history(self, user_id: str) -> List[AlertDeliveryIntentDTO]:
        intents = self.repo.list_delivery_intents(user_id)
        return [
            AlertDeliveryIntentDTO(
                intent_id=i.intent_id,
                alert_id=i.alert_id,
                owner_user_id=i.owner_user_id,
                event_id=i.event_id,
                title=i.title,
                body=i.body,
                scheduled_for=i.scheduled_for,
                delivered_at=i.delivered_at,
                is_delivered=i.is_delivered,
                delivery_error=i.delivery_error,
            )
            for i in intents
        ]

    # -------------------------------------------------------------------------
    # Coverage Matrix
    # -------------------------------------------------------------------------

    def get_coverage(self) -> EconomicCalendarCoverageDTO:
        events = self.repo.list_events()
        total_count = len(events)
        verified_count = sum(1 for e in events if e.is_verified)
        with_forecast_count = sum(1 for e in events if len(e.consensus_snapshots) > 0)

        precision_counts: Dict[str, int] = {}
        for e in events:
            p_val = e.schedule_precision.value
            precision_counts[p_val] = precision_counts.get(p_val, 0) + 1

        forecast_cov = (with_forecast_count / total_count * 100.0) if total_count > 0 else 0.0

        return EconomicCalendarCoverageDTO(
            supported_geographies=["US", "EU", "GB", "JP", "IN", "CN"],
            supported_categories=[c.value for c in EconomicEventCategory],
            total_events_count=total_count,
            verified_events_count=verified_count,
            forecast_coverage_pct=round(forecast_cov, 1),
            schedule_precision_coverage=precision_counts,
        )
