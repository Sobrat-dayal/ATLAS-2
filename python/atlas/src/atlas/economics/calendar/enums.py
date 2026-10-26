"""Controlled Enumerations for Global Economic Calendar (Stage 92)."""

from enum import Enum


class EconomicEventKind(str, Enum):
    """Categorization of macro calendar events."""
    ECONOMIC_STATISTICS_RELEASE = "ECONOMIC_STATISTICS_RELEASE"
    CENTRAL_BANK_POLICY_MEETING = "CENTRAL_BANK_POLICY_MEETING"
    CENTRAL_BANK_POLICY_DECISION = "CENTRAL_BANK_POLICY_DECISION"
    CENTRAL_BANK_OFFICIAL_PUBLICATION = "CENTRAL_BANK_OFFICIAL_PUBLICATION"
    OTHER_VERIFIED_MACRO_EVENT = "OTHER_VERIFIED_MACRO_EVENT"


class EconomicEventCategory(str, Enum):
    """Taxonomy of macroeconomic releases."""
    GDP = "gdp"
    INFLATION = "inflation"
    LABOR_MARKET = "labor"
    RETAIL_SALES = "retail"
    INDUSTRIAL_PRODUCTION = "manufacturing"
    BUSINESS_SURVEYS = "surveys"
    INTERNATIONAL_TRADE = "trade"
    FISCAL_BUDGET = "fiscal"
    HOUSING = "housing"
    CENTRAL_BANK = "central_bank"


class SchedulePrecision(str, Enum):
    """Temporal certainty of the scheduled publication instant."""
    EXACT_INSTANT = "EXACT_INSTANT"
    LOCAL_DATE_TIME = "LOCAL_DATE_TIME"
    DATE_ONLY = "DATE_ONLY"
    UNKNOWN = "UNKNOWN"


class EconomicEventStatus(str, Enum):
    """Lifecycle state of an economic calendar event."""
    SCHEDULED = "SCHEDULED"
    RESCHEDULED = "RESCHEDULED"
    RELEASE_VERIFIED = "RELEASE_VERIFIED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    STATUS_UNKNOWN = "STATUS_UNKNOWN"


class ReleaseStage(str, Enum):
    """Official release stage for the reference period."""
    ADVANCE = "ADVANCE"
    PRELIMINARY = "PRELIMINARY"
    REVISED = "REVISED"
    FINAL = "FINAL"
    SINGLE_ESTIMATE = "SINGLE_ESTIMATE"


class EconomicEventImportance(str, Enum):
    """Event market relevance rating based on transparent methodology."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCLASSIFIED = "UNCLASSIFIED"


class ForecastAggregationMethod(str, Enum):
    """Mathematical methodology used for consensus aggregation."""
    MEDIAN = "MEDIAN"
    MEAN = "MEAN"
    WEIGHTED_MEAN = "WEIGHTED_MEAN"


class SurpriseDirection(str, Enum):
    """Actual outcome relative to pre-release consensus."""
    ABOVE_CONSENSUS = "ABOVE_CONSENSUS"
    BELOW_CONSENSUS = "BELOW_CONSENSUS"
    IN_LINE = "IN_LINE"
    UNAVAILABLE = "UNAVAILABLE"


class EventAlertType(str, Enum):
    """Type of notification alert rule."""
    BEFORE_SCHEDULED_RELEASE = "BEFORE_SCHEDULED_RELEASE"
    WHEN_RELEASE_VERIFIED = "WHEN_RELEASE_VERIFIED"
    WHEN_SCHEDULE_CHANGES = "WHEN_SCHEDULE_CHANGES"
    WHEN_OFFICIAL_REVISION_PUBLISHED = "WHEN_OFFICIAL_REVISION_PUBLISHED"


class AlertStatus(str, Enum):
    """Status of user alert rule."""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    FIRED = "FIRED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
