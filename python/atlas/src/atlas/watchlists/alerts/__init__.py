"""Watchlist Alerts Subsystem (Stage 80)."""

from atlas.watchlists.alerts.capabilities import (
    ASSET_CLASS_MEASURE_COMPATIBILITY,
    COOLDOWN_PRESETS,
    MAX_ACTIVE_ALERTS_PER_USER,
    MAX_ALERTS_PER_INSTRUMENT,
    REFERENCE_METHODOLOGIES,
    SUPPORTED_CAPABILITIES,
    get_alert_capabilities,
    validate_measure_for_asset_class,
)
from atlas.watchlists.alerts.conditions import (
    ConditionEvaluationResult,
    compute_percentage_change,
    determine_side,
    evaluate_alert_condition,
)
from atlas.watchlists.alerts.errors import (
    AlertDataUnavailableError,
    AlertEvaluationUnavailableError,
    AlertLimitExceededError,
    AlertNotEntitledError,
    AlertNotFoundError,
    AlertRevisionConflictError,
    IncompatibleQuoteMeasureError,
    IncompatibleReferenceMethodError,
    InvalidAlertConditionError,
    InvalidCooldownError,
    InvalidExpirationError,
    InvalidThresholdUnitError,
    UnsupportedAlertTypeError,
    WatchlistAlertError,
    WatchlistItemNotFoundError,
)
from atlas.watchlists.alerts.evaluation import (
    AlertEvaluationEngine,
    NormalizedObservation,
)
from atlas.watchlists.alerts.models import (
    WatchlistAlertEvaluationState,
    WatchlistAlertNotificationOutbox,
    WatchlistAlertRule,
    WatchlistAlertTrigger,
)
from atlas.watchlists.alerts.notification_dispatch import AlertNotificationDispatcher
from atlas.watchlists.alerts.repository import WatchlistAlertRepository
from atlas.watchlists.alerts.router import router as alerts_router
from atlas.watchlists.alerts.schemas import (
    AlertCapabilitiesResponse,
    AlertCapabilityItem,
    AlertEvaluationStateResponse,
    AlertEvaluationStatus,
    AlertHealthStatusResponse,
    AlertHistoryResponse,
    AlertListResponse,
    AlertRuleResponse,
    AlertRuleType,
    AlertState,
    AlertTriggerResponse,
    ArmedSide,
    ComparisonOperator,
    CreateAlertRequest,
    NotificationDeliveryStatus,
    QuoteMeasure,
    RecurrencePolicy,
    ReferenceMethodology,
    UpdateAlertRequest,
)
from atlas.watchlists.alerts.service import WatchlistAlertService
from atlas.watchlists.alerts.worker import WatchlistAlertWorker

__all__ = [
    # Models
    "WatchlistAlertRule",
    "WatchlistAlertEvaluationState",
    "WatchlistAlertTrigger",
    "WatchlistAlertNotificationOutbox",
    # Enums & Schemas
    "AlertRuleType",
    "QuoteMeasure",
    "ComparisonOperator",
    "RecurrencePolicy",
    "AlertState",
    "AlertEvaluationStatus",
    "ArmedSide",
    "ReferenceMethodology",
    "NotificationDeliveryStatus",
    "CreateAlertRequest",
    "UpdateAlertRequest",
    "AlertRuleResponse",
    "AlertEvaluationStateResponse",
    "AlertTriggerResponse",
    "AlertListResponse",
    "AlertHistoryResponse",
    "AlertCapabilitiesResponse",
    "AlertCapabilityItem",
    "AlertHealthStatusResponse",
    # Errors
    "WatchlistAlertError",
    "AlertNotFoundError",
    "AlertLimitExceededError",
    "InvalidAlertConditionError",
    "InvalidThresholdUnitError",
    "IncompatibleQuoteMeasureError",
    "IncompatibleReferenceMethodError",
    "AlertDataUnavailableError",
    "AlertNotEntitledError",
    "InvalidExpirationError",
    "InvalidCooldownError",
    "AlertRevisionConflictError",
    "AlertEvaluationUnavailableError",
    "UnsupportedAlertTypeError",
    "WatchlistItemNotFoundError",
    # Capabilities
    "MAX_ACTIVE_ALERTS_PER_USER",
    "MAX_ALERTS_PER_INSTRUMENT",
    "ASSET_CLASS_MEASURE_COMPATIBILITY",
    "SUPPORTED_CAPABILITIES",
    "REFERENCE_METHODOLOGIES",
    "COOLDOWN_PRESETS",
    "get_alert_capabilities",
    "validate_measure_for_asset_class",
    # Conditions
    "ConditionEvaluationResult",
    "compute_percentage_change",
    "determine_side",
    "evaluate_alert_condition",
    # Engine & Worker
    "AlertEvaluationEngine",
    "NormalizedObservation",
    "AlertNotificationDispatcher",
    "WatchlistAlertWorker",
    # Repository & Service
    "WatchlistAlertRepository",
    "WatchlistAlertService",
    # Router
    "alerts_router",
]
