"""Enums and Constants for Financial Screeners V1 (Stage 94)."""

from enum import Enum
from typing import Any, Optional


class CaseInsensitiveStrEnum(str, Enum):
    """Case-insensitive string enum with robust alias parsing."""

    @classmethod
    def _missing_(cls, value: Any) -> Optional["CaseInsensitiveStrEnum"]:
        if isinstance(value, str):
            clean = value.strip().lower()
            for member in cls:
                if member.value.lower() == clean or member.name.lower() == clean:
                    return member
        return None


class UniverseKind(CaseInsensitiveStrEnum):
    """Supported canonical financial screening universes."""

    COMMON_EQUITY = "common_equity"
    ALL_EQUITY = "all_equity"
    GLOBAL_MEGA_CAP = "global_mega_cap"
    US_LARGE_CAP = "us_large_cap"
    TECH_SECTOR = "tech_sector"
    DIVIDEND_STOCKS = "dividend_stocks"
    DELISTED_EQUITY = "delisted_equity"


class SecurityType(CaseInsensitiveStrEnum):
    """Financial security asset class / instrument types."""

    COMMON_STOCK = "common_stock"
    PREFERRED_STOCK = "preferred_stock"
    DEPOSITARY_RECEIPT = "depositary_receipt"
    ETF = "etf"
    FUND = "fund"


class ListingStatus(CaseInsensitiveStrEnum):
    """Listing operational status on venue."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    INACTIVE = "inactive"


class FilterCategory(CaseInsensitiveStrEnum):
    """Functional categorization for screen filters."""

    UNIVERSE = "universe"
    LISTING = "listing"
    GEOGRAPHY = "geography"
    INDUSTRY = "industry"
    MARKET_DATA = "market_data"
    FUNDAMENTALS = "fundamentals"
    VALUATION = "valuation"
    PROFITABILITY = "profitability"


class FilterOperator(CaseInsensitiveStrEnum):
    """Approved typed comparison operators."""

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    BETWEEN = "between"
    IN = "in"


class ValueType(CaseInsensitiveStrEnum):
    """Underlying data types for filter predicates."""

    NUMERIC = "numeric"
    INTEGER = "integer"
    ENUM = "enum"
    BOOLEAN = "boolean"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"


class UnitKind(CaseInsensitiveStrEnum):
    """Measurement units for display and validation."""

    MONETARY = "monetary"
    PERCENT = "percent"
    MULTIPLE = "multiple"
    SHARES = "shares"
    CURRENCY_PER_SHARE = "currency_per_share"
    DIMENSIONLESS = "dimensionless"


class PeriodPolicy(CaseInsensitiveStrEnum):
    """Financial reporting period policy."""

    LATEST_ANNUAL = "latest_annual"
    LATEST_QUARTER = "latest_quarter"
    VALID_TTM = "valid_ttm"


class ConsolidationScope(CaseInsensitiveStrEnum):
    """Accounting consolidation basis."""

    CONSOLIDATED = "consolidated"
    STANDALONE = "standalone"


class FreshnessStatus(CaseInsensitiveStrEnum):
    """Observation freshness qualification."""

    LIVE = "live"
    DELAYED = "delayed"
    END_OF_DAY = "end_of_day"
    STALE = "stale"


class MetricAvailabilityStatus(CaseInsensitiveStrEnum):
    """Cell-level metric status."""

    AVAILABLE = "available"
    MISSING = "missing"
    NOT_MEANINGFUL = "not_meaningful"
    RESTRICTED = "restricted"


class SortDirection(CaseInsensitiveStrEnum):
    """Sorting order."""

    ASC = "asc"
    DESC = "desc"


class ResultGrain(CaseInsensitiveStrEnum):
    """Screener row granularity."""

    SECURITY_LISTING = "security_listing"
    SECURITY_INSTRUMENT = "security_instrument"


class EditorType(CaseInsensitiveStrEnum):
    """Visual builder input control type (Stage 95)."""

    DECIMAL_INPUT = "decimal_input"
    MONETARY_INPUT = "monetary_input"
    PERCENT_INPUT = "percent_input"
    MULTIPLE_INPUT = "multiple_input"
    NUMBER_RANGE = "number_range"
    ENUM_SELECT = "enum_select"
    ENUM_MULTI_SELECT = "enum_multi_select"
    BOOLEAN_SELECT = "boolean_select"
    DATE_INPUT = "date_input"

