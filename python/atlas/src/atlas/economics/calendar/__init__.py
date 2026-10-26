"""Global Economic Calendar Package (Stage 92).

Authoritative verified macroeconomic releases, central bank events, consensus forecasts,
actual-versus-forecast surprises, schedule revisions, and timezone-aware financial terminal workspaces.
"""

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
from .errors import (
    EconomicCalendarError,
    EconomicEventAlertNotFoundError,
    EconomicEventAlertQuotaExceededError,
    EconomicEventDateRangeInvalidError,
    EconomicEventForecastUnavailableError,
    EconomicEventIncompatibleForecastError,
    EconomicEventNotFoundError,
    EconomicEventScheduleUnavailableError,
    EconomicEventTimezoneInvalidError,
)
from .models import (
    AlertDeliveryIntent,
    ConsensusSnapshot,
    EconomicCalendarEvent,
    EconomicEventObservation,
    EconomicReleaseFamily,
    EconomicSurpriseMetric,
    ScheduleRevision,
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
    EconomicReleaseFamilyDTO,
    EconomicSurpriseMetricDTO,
    ScheduleRevisionDTO,
    UpdateEventAlertRequestDTO,
    UserEventAlertDTO,
)
from .service import EconomicCalendarService

__all__ = [
    # Enums
    "AlertStatus",
    "EconomicEventCategory",
    "EconomicEventImportance",
    "EconomicEventKind",
    "EconomicEventStatus",
    "EventAlertType",
    "ForecastAggregationMethod",
    "ReleaseStage",
    "SchedulePrecision",
    "SurpriseDirection",
    # Errors
    "EconomicCalendarError",
    "EconomicEventNotFoundError",
    "EconomicEventScheduleUnavailableError",
    "EconomicEventForecastUnavailableError",
    "EconomicEventIncompatibleForecastError",
    "EconomicEventAlertNotFoundError",
    "EconomicEventAlertQuotaExceededError",
    "EconomicEventTimezoneInvalidError",
    "EconomicEventDateRangeInvalidError",
    # Models
    "EconomicReleaseFamily",
    "EconomicEventObservation",
    "ConsensusSnapshot",
    "EconomicSurpriseMetric",
    "ScheduleRevision",
    "EconomicCalendarEvent",
    "UserEventAlert",
    "AlertDeliveryIntent",
    # Schemas
    "EconomicReleaseFamilyDTO",
    "EconomicEventObservationDTO",
    "ConsensusSnapshotDTO",
    "EconomicSurpriseMetricDTO",
    "ScheduleRevisionDTO",
    "EconomicCalendarEventDTO",
    "EconomicCalendarEventDetailDTO",
    "CalendarQueryContextDTO",
    "EconomicCalendarResponseDTO",
    "UserEventAlertDTO",
    "CreateEventAlertRequestDTO",
    "UpdateEventAlertRequestDTO",
    "AlertDeliveryIntentDTO",
    "EconomicCalendarCoverageDTO",
    # Repository & Service
    "EconomicCalendarRepository",
    "EconomicCalendarService",
]
