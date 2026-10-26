"""Enums for Company Earnings Intelligence (Stage 84).

Defines stable types for earnings events, reporting periods, accounting bases,
surprise classifications, management guidance, and call sessions.
"""

from enum import Enum


class EarningsEventType(str, Enum):
    """Classification of corporate earnings events."""
    EARNINGS_RELEASE = "EARNINGS_RELEASE"
    EARNINGS_CALL = "EARNINGS_CALL"
    RESULTS_PRESENTATION = "RESULTS_PRESENTATION"
    SHAREHOLDER_MEETING = "SHAREHOLDER_MEETING"


class EarningsEventStatus(str, Enum):
    """Operational confirmation status of an earnings announcement."""
    CONFIRMED = "CONFIRMED"
    ESTIMATED = "ESTIMATED"
    TENTATIVE = "TENTATIVE"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class MarketSession(str, Enum):
    """Relation of earnings announcement timing to exchange trading sessions."""
    BEFORE_MARKET = "BEFORE_MARKET"
    AFTER_MARKET = "AFTER_MARKET"
    DURING_HOURS = "DURING_HOURS"
    UNSPECIFIED = "UNSPECIFIED"


class EarningsPeriodType(str, Enum):
    """Fiscal reporting interval."""
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    SEMI_ANNUAL = "SEMI_ANNUAL"


class EPSBasis(str, Enum):
    """Basis for reported and estimated per-share earnings."""
    DILUTED = "DILUTED"
    BASIC = "BASIC"
    ADJUSTED = "ADJUSTED"
    HEADLINE = "HEADLINE"


class AccountingBasis(str, Enum):
    """Regulatory accounting standard framework."""
    GAAP = "GAAP"
    NON_GAAP = "NON_GAAP"
    IFRS = "IFRS"


class SurpriseClassification(str, Enum):
    """Analytical categorization of actual vs. consensus performance."""
    BEAT = "BEAT"
    MISS = "MISS"
    IN_LINE = "IN_LINE"
    NOT_COMPARABLE = "NOT_COMPARABLE"
    UNAVAILABLE = "UNAVAILABLE"


class GuidanceMetricType(str, Enum):
    """Target metric in corporate management guidance."""
    REVENUE = "REVENUE"
    EPS = "EPS"
    OPERATING_INCOME = "OPERATING_INCOME"
    NET_INCOME = "NET_INCOME"
    GROSS_MARGIN = "GROSS_MARGIN"
    CAPEX = "CAPEX"


class GuidanceStatus(str, Enum):
    """Lifecycle state of corporate guidance."""
    ACTIVE = "ACTIVE"
    REVISED = "REVISED"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"


class TranscriptStatus(str, Enum):
    """Availability and licensing state of earnings call transcripts."""
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    PENDING = "PENDING"
    UNAVAILABLE = "UNAVAILABLE"
