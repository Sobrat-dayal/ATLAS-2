"""Domain Models and Dataclasses for Global Economic Calendar (Stage 92)."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .enums import (
    AlertStatus,
    EconomicEventCategory,
    EconomicEventImportance,
    EconomicEventKind,
    EconomicEventStatus,
    EventAlertType,
    ForecastAggregationMethod,
    ReleaseStage,
    SchedulePrecision,
    SurpriseDirection,
)


@dataclass
class EconomicReleaseFamily:
    """Grouping of macroeconomic releases from a single statistical authority."""
    family_id: str
    name: str
    category: EconomicEventCategory
    geography_id: str
    agency_name: str
    default_importance: EconomicEventImportance
    description: str


@dataclass
class EconomicEventObservation:
    """Official observation published during an economic release."""
    observation_id: str
    event_id: str
    economic_series_id: str
    indicator_name: str
    reference_period: str
    actual_value: Optional[Decimal]
    previous_value: Optional[Decimal]
    revised_previous_value: Optional[Decimal]
    unit: str
    release_stage: ReleaseStage
    source_revision: str = "REV-ORIGINAL"


@dataclass
class ConsensusSnapshot:
    """Pre-release consensus forecast snapshot from authorized statistical sources."""
    snapshot_id: str
    event_id: str
    economic_series_id: str
    consensus_value: Decimal
    unit: str
    aggregation_method: ForecastAggregationMethod
    contributor_count: Optional[int]
    snapshot_timestamp: datetime
    provider_name: str


@dataclass
class EconomicSurpriseMetric:
    """Quantified difference between actual statistical release and pre-release consensus."""
    event_id: str
    economic_series_id: str
    actual_value: Decimal
    consensus_value: Decimal
    unit: str
    surprise_value: Decimal
    percentage_point_diff: Optional[Decimal] = None
    basis_point_diff: Optional[Decimal] = None
    relative_surprise_pct: Optional[Decimal] = None
    direction: SurpriseDirection = SurpriseDirection.IN_LINE
    methodology_version: str = "METHOD-STAGE92-V1"


@dataclass
class ScheduleRevision:
    """Audit record of an official publication schedule revision or postponement."""
    revision_id: str
    event_id: str
    previous_scheduled_time: datetime
    new_scheduled_time: datetime
    reason: Optional[str]
    revised_at: datetime


@dataclass
class EconomicCalendarEvent:
    """Authoritative canonical macroeconomic calendar event."""
    event_id: str
    official_event_identifier: str
    event_kind: EconomicEventKind
    category: EconomicEventCategory
    release_family_id: str
    title: str
    geographic_entity_ids: List[str]
    institution_entity_id: Optional[str]
    scheduled_start: datetime  # UTC normalized
    scheduled_end: Optional[datetime]  # UTC normalized for multi-day events
    schedule_precision: SchedulePrecision
    source_timezone: str  # IANA timezone (e.g. America/New_York)
    reference_period: str  # e.g. "2024-10", "2024-Q3"
    release_stage: ReleaseStage
    event_status: EconomicEventStatus
    importance: EconomicEventImportance
    indicators: List[str]
    official_source_id: str
    official_source_name: str
    official_source_url: str
    published_at: Optional[datetime] = None  # Exact verified publication timestamp in UTC
    is_verified: bool = True
    provenance_id: str = "prov-stage92-official"
    source_revision: str = "REV-ORIGINAL"
    observations: List[EconomicEventObservation] = field(default_factory=list)
    consensus_snapshots: List[ConsensusSnapshot] = field(default_factory=list)
    schedule_revisions: List[ScheduleRevision] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class UserEventAlert:
    """User-owned notification rule configured for an economic release event."""
    alert_id: str
    owner_user_id: str
    event_id: str
    alert_type: EventAlertType
    reminder_offset_minutes: int = 15
    is_enabled: bool = True
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered_at: Optional[datetime] = None
    trigger_count: int = 0
    idempotency_key: str = ""


@dataclass
class AlertDeliveryIntent:
    """Durable notification intent record dispatched through Stage 49 Notification Center."""
    intent_id: str
    alert_id: str
    owner_user_id: str
    event_id: str
    title: str
    body: str
    scheduled_for: datetime
    delivered_at: Optional[datetime] = None
    is_delivered: bool = False
    delivery_error: Optional[str] = None
