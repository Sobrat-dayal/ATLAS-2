"""Enums and Constants for Company Financial Ratios (Stage 83)."""

from enum import Enum


class RatioCategory(str, Enum):
    PROFITABILITY = "profitability"
    LIQUIDITY = "liquidity"
    SOLVENCY = "solvency"
    EFFICIENCY = "efficiency"
    CASH_FLOW = "cash_flow"
    VALUATION = "valuation"


class RatioStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    NOT_MEANINGFUL = "NOT_MEANINGFUL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INCOMPATIBLE_INPUTS = "INCOMPATIBLE_INPUTS"
    NOT_ENTITLED = "NOT_ENTITLED"


class RatioPeriodType(str, Enum):
    ANNUAL = "ANNUAL"
    QUARTERLY = "QUARTERLY"
    TTM = "TTM"


class UnitKind(str, Enum):
    PERCENT = "PERCENT"
    MULTIPLE = "MULTIPLE"
    DAYS = "DAYS"
    MONETARY = "MONETARY"
    CURRENCY_PER_SHARE = "CURRENCY_PER_SHARE"
    DIMENSIONLESS = "DIMENSIONLESS"


class DenominatorPolicy(str, Enum):
    STRICT_POSITIVE = "STRICT_POSITIVE"
    NON_ZERO = "NON_ZERO"
    AVERAGE_BALANCE = "AVERAGE_BALANCE"
    PERIOD_END = "PERIOD_END"


class NegativePolicy(str, Enum):
    VALID_NEGATIVE = "VALID_NEGATIVE"
    NOT_MEANINGFUL = "NOT_MEANINGFUL"
