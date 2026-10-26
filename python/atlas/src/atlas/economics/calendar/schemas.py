"""Pydantic V2 Schemas and DTOs for Global Economic Calendar (Stage 92)."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

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


class EconomicReleaseFamilyDTO(BaseModel):
    """Release family grouping of macroeconomic series."""
    model_config = ConfigDict(from_attributes=True)

    family_id: str
    name: str
    category: EconomicEventCategory
    geography_id: str
    agency_name: str
    default_importance: EconomicEventImportance
    description: str


class EconomicEventObservationDTO(BaseModel):
    """Observation data published in an economic release event."""
    model_config = ConfigDict(from_attributes=True)

    observation_id: str
    event_id: str
    economic_series_id: str
    indicator_name: str
    reference_period: str
    actual_value: Optional[float] = None
    previous_value: Optional[float] = None
    revised_previous_value: Optional[float] = None
    unit: str
    release_stage: ReleaseStage
    source_revision: str


class ConsensusSnapshotDTO(BaseModel):
    """Consensus forecast snapshot."""
    model_config = ConfigDict(from_attributes=True)

    snapshot_id: str
    event_id: str
    economic_series_id: str
    consensus_value: float
    unit: str
    aggregation_method: ForecastAggregationMethod
    contributor_count: Optional[int] = None
    snapshot_timestamp: datetime
    provider_name: str


class EconomicSurpriseMetricDTO(BaseModel):
    """Statistical surprise calculation."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    economic_series_id: str
    actual_value: float
    consensus_value: float
    unit: str
    surprise_value: float
    percentage_point_diff: Optional[float] = None
    basis_point_diff: Optional[float] = None
    relative_surprise_pct: Optional[float] = None
    direction: SurpriseDirection
    methodology_version: str


class ScheduleRevisionDTO(BaseModel):
    """Record of an official release rescheduling or postponement."""
    model_config = ConfigDict(from_attributes=True)

    revision_id: str
    event_id: str
    previous_scheduled_time: datetime
    new_scheduled_time: datetime
    reason: Optional[str] = None
    revised_at: datetime


class EconomicCalendarEventDTO(BaseModel):
    """Calendar event overview row."""
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    official_event_identifier: str
    event_kind: EconomicEventKind
    category: EconomicEventCategory
    release_family_id: str
    title: str
    geographic_entity_ids: List[str]
    institution_entity_id: Optional[str] = None
    scheduled_start: datetime  # UTC
    scheduled_end: Optional[datetime] = None
    scheduled_start_display: str  # Localized display string e.g. "2024-11-07 14:00"
    display_timezone: str
    schedule_precision: SchedulePrecision
    source_timezone: str
    reference_period: str
    release_stage: ReleaseStage
    event_status: EconomicEventStatus
    importance: EconomicEventImportance
    indicators: List[str]
    official_source_id: str
    official_source_name: str
    official_source_url: str
    published_at: Optional[datetime] = None
    is_verified: bool
    # Primary headline observation values
    primary_series_id: Optional[str] = None
    actual_value: Optional[float] = None
    consensus_value: Optional[float] = None
    previous_value: Optional[float] = None
    revised_previous_value: Optional[float] = None
    unit: Optional[str] = None
    surprise: Optional[EconomicSurpriseMetricDTO] = None


class EconomicCalendarEventDetailDTO(BaseModel):
    """Comprehensive event detail view."""
    model_config = ConfigDict(from_attributes=True)

    event: EconomicCalendarEventDTO
    observations: List[EconomicEventObservationDTO]
    consensus_snapshots: List[ConsensusSnapshotDTO]
    schedule_revisions: List[ScheduleRevisionDTO]
    surprises: List[EconomicSurpriseMetricDTO]
    notes: Optional[str] = None
    provenance_id: str
    source_revision: str


class CalendarQueryContextDTO(BaseModel):
    """Metadata describing the query context."""
    model_config = ConfigDict(from_attributes=True)

    display_timezone: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    view_preset: str
    total_events: int


class EconomicCalendarResponseDTO(BaseModel):
    """Top-level response envelope for calendar queries."""
    model_config = ConfigDict(from_attributes=True)

    context: CalendarQueryContextDTO
    events: List[EconomicCalendarEventDTO]
    categories: List[str]
    supported_geographies: List[str]


class UserEventAlertDTO(BaseModel):
    """User-owned economic event notification rule."""
    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    owner_user_id: str
    event_id: str
    event_title: str
    scheduled_time: datetime
    alert_type: EventAlertType
    reminder_offset_minutes: int
    is_enabled: bool
    status: AlertStatus
    created_at: datetime
    last_triggered_at: Optional[datetime] = None
    trigger_count: int


class CreateEventAlertRequestDTO(BaseModel):
    """Request payload to create a new event alert."""
    event_id: str
    alert_type: EventAlertType = EventAlertType.BEFORE_SCHEDULED_RELEASE
    reminder_offset_minutes: int = 15
    is_enabled: bool = True


class UpdateEventAlertRequestDTO(BaseModel):
    """Request payload to update an existing event alert."""
    reminder_offset_minutes: Optional[int] = None
    is_enabled: Optional[bool] = None
    status: Optional[AlertStatus] = None


class AlertDeliveryIntentDTO(BaseModel):
    """Notification dispatch delivery history."""
    model_config = ConfigDict(from_attributes=True)

    intent_id: str
    alert_id: str
    owner_user_id: str
    event_id: str
    title: str
    body: str
    scheduled_for: datetime
    delivered_at: Optional[datetime] = None
    is_delivered: bool
    delivery_error: Optional[str] = None


class EconomicCalendarCoverageDTO(BaseModel):
    """Coverage matrix across jurisdictions and indicators."""
    model_config = ConfigDict(from_attributes=True)

    supported_geographies: List[str]
    supported_categories: List[str]
    total_events_count: int
    verified_events_count: int
    forecast_coverage_pct: float
    schedule_precision_coverage: dict
