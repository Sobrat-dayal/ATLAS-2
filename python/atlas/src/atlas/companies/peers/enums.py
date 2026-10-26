"""Enums and Constants for Company Peers and Comparable Company Analysis (Stage 87)."""

from enum import Enum


class PeerRelationshipType(str, Enum):
    """Categorization of peer relationships with strict semantics."""

    COMPARABLE_CANDIDATE = "COMPARABLE_CANDIDATE"  # Statistically or industry-matched candidate
    USER_SELECTED_PEER = "USER_SELECTED_PEER"  # Explicitly added by analyst in custom group
    SOURCE_DEFINED_PEER = "SOURCE_DEFINED_PEER"  # Declared by authoritative data provider / 10-K
    VERIFIED_COMPETITOR = "VERIFIED_COMPETITOR"  # Verified direct commercial market competitor


class IndustryTaxonomy(str, Enum):
    """Standardized industry taxonomy frameworks."""

    GICS = "GICS"  # Global Industry Classification Standard (MSCI / S&P)
    SIC = "SIC"  # Standard Industrial Classification (US SEC)
    NAICS = "NAICS"  # North American Industry Classification System
    ICB = "ICB"  # Industry Classification Benchmark (FTSE Russell)


class PeriodAlignmentMode(str, Enum):
    """Temporal alignment mode for multi-company financial comparisons."""

    LATEST_COMMON_FISCAL_YEAR = "LATEST_COMMON_FISCAL_YEAR"
    LATEST_AVAILABLE = "LATEST_AVAILABLE"
    SELECTED_FISCAL_PERIOD = "SELECTED_FISCAL_PERIOD"
    QUALIFIED_TTM = "QUALIFIED_TTM"


class MetricObservationStatus(str, Enum):
    """Availability and qualification state of a single comparable observation."""

    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    NOT_MEANINGFUL = "NOT_MEANINGFUL"  # E.g. negative P/E or negative ROE denominator
    INCOMPATIBLE = "INCOMPATIBLE"  # Mixed accounting standards without reconciliation
    STALE = "STALE"  # Market price or statement beyond freshness threshold
    NOT_APPLICABLE = "NOT_APPLICABLE"  # Specialized industry exclusion (e.g. D/E for banks)
    NOT_ENTITLED = "NOT_ENTITLED"  # User lacking license tier for underlying dataset
    SOURCE_ERROR = "SOURCE_ERROR"


class OutlierPolicy(str, Enum):
    """Policy for statistical outlier identification and display."""

    ALL_VALID_VALUES = "ALL_VALID_VALUES"
    EXCLUDE_SELECTED_OUTLIERS = "EXCLUDE_SELECTED_OUTLIERS"
    WINSORIZED = "WINSORIZED"


class SubjectInclusionPolicy(str, Enum):
    """Whether benchmark peer statistics (median, mean) include or exclude the subject company."""

    EXCLUDE_SUBJECT = "EXCLUDE_SUBJECT"  # Pure peer benchmark
    INCLUDE_SUBJECT = "INCLUDE_SUBJECT"  # Total group benchmark


class ComparisonMetricCategory(str, Enum):
    """Analytical categories of financial and valuation comparison metrics."""

    SCALE = "SCALE"  # Revenue, Assets, Market Cap, Enterprise Value
    GROWTH = "GROWTH"  # Revenue Growth, Net Income Growth
    PROFITABILITY = "PROFITABILITY"  # Gross Margin, Operating Margin, Net Margin, ROE, ROA, ROIC
    LIQUIDITY = "LIQUIDITY"  # Current Ratio, Quick Ratio
    SOLVENCY = "SOLVENCY"  # Debt/Equity, Debt/Assets, Net Debt/EBITDA
    EFFICIENCY = "EFFICIENCY"  # Asset Turnover, Inventory Turnover
    CASH_FLOW = "CASH_FLOW"  # Free Cash Flow, FCF Margin, Operating Cash Flow
    VALUATION = "VALUATION"  # P/E, Forward P/E, P/B, P/S, EV/EBITDA, EV/Revenue, FCF Yield
