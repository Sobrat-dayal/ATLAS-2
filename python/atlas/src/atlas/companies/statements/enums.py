"""Canonical Enums for Company Financial Statements (Stage 82)."""

from enum import Enum


class StatementType(str, Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW_STATEMENT = "cash_flow_statement"


class StatementPeriodType(str, Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    TTM = "ttm"
    SEMIANNUAL = "semiannual"
    NINE_MONTH = "nine_month"


class ConsolidationScope(str, Enum):
    CONSOLIDATED = "consolidated"
    STANDALONE = "standalone"


class AccountingFramework(str, Enum):
    US_GAAP = "us_gaap"
    IFRS = "ifrs"
    IND_AS = "ind_as"
    OTHER = "other"
    UNKNOWN = "unknown"


class ScaleType(str, Enum):
    AUTO = "auto"
    BILLIONS = "billions"
    MILLIONS = "millions"
    THOUSANDS = "thousands"
    ORIGINAL = "original"


class ComparisonMode(str, Enum):
    NONE = "none"
    YOY_ABSOLUTE = "yoy_absolute"
    YOY_PERCENT = "yoy_percent"
    QOQ_ABSOLUTE = "qoq_absolute"
    QOQ_PERCENT = "qoq_percent"
    COMMON_SIZE = "common_size"


class RevisionPolicy(str, Enum):
    LATEST = "latest"
    ORIGINAL = "original"


class DerivationKind(str, Enum):
    REPORTED = "reported"
    NORMALIZED = "normalized"
    DERIVED_QUARTER = "derived_quarter"
    DERIVED_TTM = "derived_ttm"
    SUBTOTAL = "subtotal"


class DiagnosticStatus(str, Enum):
    CONSISTENT = "consistent"
    WITHIN_ROUNDING_TOLERANCE = "within_rounding_tolerance"
    NOT_COMPARABLE = "not_comparable"
    INCOMPLETE = "incomplete"
    REQUIRES_REVIEW = "requires_review"
