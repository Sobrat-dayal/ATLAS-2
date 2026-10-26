"""Enumerations for Institutional Economics V1 (Stage 89).

Defines controlled taxonomies for indicator categories, measurement units,
frequencies, seasonal adjustments, price bases, and observation statuses.
"""

from enum import StrEnum


class IndicatorCategory(StrEnum):
    """High-level macroeconomic classification taxonomy."""
    NATIONAL_ACCOUNTS = "NATIONAL_ACCOUNTS"
    INFLATION = "INFLATION"
    LABOR_MARKET = "LABOR_MARKET"
    INTEREST_RATES = "INTEREST_RATES"
    MONETARY = "MONETARY"
    INDUSTRIAL_ACTIVITY = "INDUSTRIAL_ACTIVITY"
    CONSUMPTION = "CONSUMPTION"
    FISCAL = "FISCAL"
    EXTERNAL_SECTOR = "EXTERNAL_SECTOR"
    HOUSING = "HOUSING"
    BUSINESS_SURVEYS = "BUSINESS_SURVEYS"
    OTHER = "OTHER"


class StatisticalUnit(StrEnum):
    """Statistical measurement units for economic observations."""
    PERCENT = "PERCENT"                          # e.g., 5.2% (interest rate, ratio, or pre-computed growth rate)
    PERCENTAGE_POINTS = "PERCENTAGE_POINTS"      # e.g., +0.50 %p change in rate or share
    BASIS_POINTS = "BASIS_POINTS"                # e.g., +50 bps change in interest rate
    INDEX_POINTS = "INDEX_POINTS"                # e.g., 120.5 (CPI level, base year = 100)
    CURRENCY_USD_BILLIONS = "CURRENCY_USD_BILLIONS" # e.g., $28,781B USD
    LOCAL_CURRENCY_BILLIONS = "LOCAL_CURRENCY_BILLIONS" # e.g., EUR 3,840B or INR 295,360B
    PERSONS_THOUSANDS = "PERSONS_THOUSANDS"      # e.g., 161,200 thousand employed
    RATIO = "RATIO"                              # e.g., 1.25 debt-to-GDP


class ReportingFrequency(StrEnum):
    """Standardized statistical reporting frequencies."""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL = "ANNUAL"
    IRREGULAR = "IRREGULAR"


class SeasonalAdjustmentKind(StrEnum):
    """Seasonal adjustment qualification."""
    SEASONALLY_ADJUSTED = "SEASONALLY_ADJUSTED"
    NOT_ADJUSTED = "NOT_ADJUSTED"
    SEASONALLY_ADJUSTED_ANNUAL_RATE = "SEASONALLY_ADJUSTED_ANNUAL_RATE"


class PriceBasisKind(StrEnum):
    """Price basis for national accounts and real vs nominal series."""
    CURRENT_PRICES = "CURRENT_PRICES"       # Nominal
    CONSTANT_PRICES = "CONSTANT_PRICES"     # Real
    CHAIN_VOLUME = "CHAIN_VOLUME"           # Chained volume measures
    NOT_APPLICABLE = "NOT_APPLICABLE"       # Rates, indices, or non-monetary series


class ObservationStatus(StrEnum):
    """Publication lifecycle and revision status of an observation."""
    OBSERVED = "OBSERVED"
    PRELIMINARY = "PRELIMINARY"
    REVISED = "REVISED"
    FINAL = "FINAL"
    ESTIMATED = "ESTIMATED"
    MISSING = "MISSING"


class TransformationType(StrEnum):
    """Approved versioned statistical transformation algorithms."""
    SOURCE_REPORTED = "SOURCE_REPORTED"
    LEVEL = "LEVEL"
    ABSOLUTE_CHANGE = "ABSOLUTE_CHANGE"
    PERCENT_CHANGE = "PERCENT_CHANGE"
    YEAR_OVER_YEAR = "YEAR_OVER_YEAR"
    MONTH_OVER_MONTH = "MONTH_OVER_MONTH"
    QUARTER_OVER_QUARTER = "QUARTER_OVER_QUARTER"
    ANNUALIZED_QUARTERLY_GROWTH = "ANNUALIZED_QUARTERLY_GROWTH"
    PERCENTAGE_POINT_CHANGE = "PERCENTAGE_POINT_CHANGE"
    BASIS_POINT_CHANGE = "BASIS_POINT_CHANGE"


class GeographicScopeKind(StrEnum):
    """Geographic scope classification."""
    COUNTRY = "COUNTRY"
    ECONOMIC_AREA = "ECONOMIC_AREA"     # e.g., Euro Area (EA19/EA20)
    REGION = "REGION"                   # e.g., Latin America, Emerging Asia
    GLOBAL_AGGREGATE = "GLOBAL_AGGREGATE" # e.g., World Total (official only)
