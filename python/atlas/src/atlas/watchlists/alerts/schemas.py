"""Pydantic schemas and enums for Watchlist Alerts V1 (Stage 80)."""

import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AlertRuleType(str, Enum):
    """Supported condition types for financial alerts."""

    PRICE_ABOVE = "PRICE_ABOVE"
    PRICE_BELOW = "PRICE_BELOW"
    CROSSING_ABOVE = "CROSSING_ABOVE"
    CROSSING_BELOW = "CROSSING_BELOW"
    PERCENTAGE_CHANGE_ABOVE = "PERCENTAGE_CHANGE_ABOVE"
    PERCENTAGE_CHANGE_BELOW = "PERCENTAGE_CHANGE_BELOW"


class QuoteMeasure(str, Enum):
    """Financial quote measures eligible for monitoring."""

    LAST = "LAST"
    BID = "BID"
    ASK = "ASK"
    MID = "MID"
    OPEN = "OPEN"
    HIGH = "HIGH"
    LOW = "LOW"
    CLOSE = "CLOSE"
    NAV = "NAV"
    YIELD = "YIELD"


class ComparisonOperator(str, Enum):
    """Mathematical comparator applied to observation vs threshold."""

    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    CROSS_ABOVE = "CROSS_ABOVE"
    CROSS_BELOW = "CROSS_BELOW"


class RecurrencePolicy(str, Enum):
    """Lifecycle recurrence mode."""

    ONE_SHOT = "ONE_SHOT"
    RECURRING = "RECURRING"


class AlertState(str, Enum):
    """User-controlled administrative lifecycle state."""

    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"


class AlertEvaluationStatus(str, Enum):
    """Operational evaluation health and state machine state."""

    WAITING_FOR_BASELINE = "WAITING_FOR_BASELINE"
    ARMED = "ARMED"
    TRIGGERED = "TRIGGERED"
    COOLDOWN = "COOLDOWN"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DEGRADED = "DEGRADED"
    ENTITLEMENT_DENIED = "ENTITLEMENT_DENIED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"


class ArmedSide(str, Enum):
    """Position relative to threshold when baseline or prior observation was established."""

    ABOVE = "ABOVE"
    BELOW = "BELOW"
    AT = "AT"


class ReferenceMethodology(str, Enum):
    """Qualified baseline methodology for percentage-change alerts."""

    SESSION_PREVIOUS_CLOSE = "SESSION_PREVIOUS_CLOSE"
    ROLLING_24H = "ROLLING_24H"
    PREVIOUS_NAV = "PREVIOUS_NAV"


class NotificationDeliveryStatus(str, Enum):
    """Outbox delivery tracking status."""

    PENDING = "PENDING"
    DELIVERED = "DELIVERED"
    RETRYING = "RETRYING"
    FAILED = "FAILED"


# --- Request Models ---


class CreateAlertRequest(BaseModel):
    """Request payload to create a new persistent Watchlist Alert."""

    model_config = ConfigDict(extra="forbid")

    watchlist_item_id: UUID = Field(..., description="Target watchlist item UUID")
    rule_type: AlertRuleType = Field(..., description="Condition type")
    quote_measure: QuoteMeasure = Field(default=QuoteMeasure.LAST, description="Quote measure to monitor")
    threshold: Decimal = Field(..., description="Exact threshold value in validated units")
    threshold_unit: str = Field(default="USD", min_length=1, max_length=32, description="Currency or unit (e.g. USD, %, bps)")
    reference_methodology: Optional[ReferenceMethodology] = Field(
        default=None, description="Required for percentage change alerts"
    )
    recurrence_policy: RecurrencePolicy = Field(
        default=RecurrencePolicy.ONE_SHOT, description="One-shot or recurring alert"
    )
    cooldown_seconds: int = Field(
        default=0, ge=0, le=604800, description="Cooldown interval in seconds between triggers"
    )
    expires_at: Optional[datetime.datetime] = Field(
        default=None, description="Optional UTC expiration timestamp"
    )

    @model_validator(mode="after")
    def validate_semantics(self) -> "CreateAlertRequest":
        # Percentage change rules require a valid reference methodology
        if self.rule_type in (AlertRuleType.PERCENTAGE_CHANGE_ABOVE, AlertRuleType.PERCENTAGE_CHANGE_BELOW):
            if not self.reference_methodology:
                raise ValueError("reference_methodology is required for percentage-change alerts.")
        
        # Expiration must be in the future if set
        if self.expires_at is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if self.expires_at <= now:
                raise ValueError("expires_at must be in the future.")
        
        return self


class UpdateAlertRequest(BaseModel):
    """Request payload to update an existing Watchlist Alert with revision protection."""

    model_config = ConfigDict(extra="forbid")

    threshold: Optional[Decimal] = Field(default=None, description="New threshold value")
    cooldown_seconds: Optional[int] = Field(default=None, ge=0, le=604800)
    recurrence_policy: Optional[RecurrencePolicy] = None
    expires_at: Optional[datetime.datetime] = None
    expected_revision: int = Field(..., ge=1, description="Expected revision for optimistic concurrency")

    @model_validator(mode="after")
    def validate_update(self) -> "UpdateAlertRequest":
        if self.expires_at is not None:
            now = datetime.datetime.now(datetime.timezone.utc)
            if self.expires_at <= now:
                raise ValueError("expires_at must be in the future.")
        return self


# --- Response Models ---


class AlertEvaluationStateResponse(BaseModel):
    """Current evaluation status, baseline context, and cooldowns."""

    model_config = ConfigDict(from_attributes=True)

    rule_revision: int
    evaluation_status: AlertEvaluationStatus
    armed_side: Optional[ArmedSide] = None
    last_qualified_value: Optional[Decimal] = None
    last_qualified_observation_time: Optional[datetime.datetime] = None
    last_trigger_at: Optional[datetime.datetime] = None
    cooldown_until: Optional[datetime.datetime] = None
    baseline_established: bool
    updated_at: datetime.datetime


class AlertTriggerResponse(BaseModel):
    """Historical record of an alert trigger."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    alert_id: UUID
    rule_revision: int
    owner_user_id: UUID
    watchlist_id: UUID
    watchlist_item_id: UUID
    instrument_entity_id: UUID
    market_series_identity: str
    symbol: str
    event_identity: str
    observation_value: Decimal
    threshold_value: Decimal
    quote_measure: str
    rule_type: str
    source: str
    venue: Optional[str] = None
    observation_time: datetime.datetime
    evaluated_at: datetime.datetime
    trigger_dedup_key: str
    notification_status: NotificationDeliveryStatus
    notification_id: Optional[UUID] = None
    notification_error: Optional[str] = None
    created_at: datetime.datetime


class AlertRuleResponse(BaseModel):
    """Complete representation of a Watchlist Alert Rule."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_user_id: UUID
    watchlist_id: UUID
    watchlist_item_id: UUID
    instrument_entity_id: UUID
    market_series_identity: str
    symbol: str
    rule_type: AlertRuleType
    rule_version: int
    quote_measure: QuoteMeasure
    comparison_operator: ComparisonOperator
    threshold: Decimal = Field(..., alias="threshold_decimal")
    threshold_unit: str
    reference_methodology: Optional[ReferenceMethodology] = None
    recurrence_policy: RecurrencePolicy
    cooldown_seconds: int
    expires_at: Optional[datetime.datetime] = None
    enabled: bool
    state: AlertState
    revision: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    evaluation_state: Optional[AlertEvaluationStateResponse] = None
    last_trigger: Optional[AlertTriggerResponse] = None


class AlertListResponse(BaseModel):
    """Paginated list of user alerts."""

    items: List[AlertRuleResponse]
    total_count: int
    active_count: int
    paused_count: int


class AlertHistoryResponse(BaseModel):
    """Paginated list of alert trigger history records."""

    items: List[AlertTriggerResponse]
    total_count: int
    next_cursor: Optional[str] = None


class AlertCapabilityItem(BaseModel):
    """Specification of a condition capability."""

    rule_type: AlertRuleType
    display_name: str
    description: str
    supported_measures: List[QuoteMeasure]
    supported_asset_classes: List[str]
    requires_reference_methodology: bool
    default_comparator: ComparisonOperator


class AlertCapabilitiesResponse(BaseModel):
    """Full operational catalog of supported conditions and measures."""

    capabilities: List[AlertCapabilityItem]
    reference_methodologies: List[dict]
    cooldown_presets: List[dict]
    max_active_alerts_per_user: int
    max_alerts_per_instrument: int


class AlertHealthStatusResponse(BaseModel):
    """Operational health status of the server-side evaluation worker."""

    status: str  # "HEALTHY", "DEGRADED", "UNAVAILABLE"
    worker_running: bool
    last_heartbeat: Optional[datetime.datetime] = None
    active_rules_in_memory: int
    evaluation_queue_lag_ms: int
    connected_to_market_events: bool
    entitlement_status: str
