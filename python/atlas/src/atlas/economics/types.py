from enum import StrEnum


class EconomicSeriesKind(StrEnum):
    OUTPUT = "output"
    PRICES = "prices"
    LABOR = "labor"
    INTEREST_RATE = "interest_rate"
    MONETARY = "monetary"
    FISCAL = "fiscal"
    TRADE = "trade"
    HOUSING = "housing"
    CONSUMPTION = "consumption"
    BUSINESS = "business"
    DEMOGRAPHIC = "demographic"
    FINANCIAL_CONDITIONS = "financial_conditions"
    SENTIMENT = "sentiment"
    OTHER = "other"


class EconomicFrequency(StrEnum):
    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"
    IRREGULAR = "irregular"
    OTHER = "other"


class EconomicValueRepresentation(StrEnum):
    LEVEL = "level"
    PERCENT = "percent"
    RATE = "rate"
    INDEX = "index"
    CURRENCY = "currency"
    COUNT = "count"
    RATIO = "ratio"
    CHANGE = "change"
    GROWTH_RATE = "growth_rate"
    OTHER = "other"


class SeasonalAdjustment(StrEnum):
    NOT_ADJUSTED = "not_adjusted"
    SEASONALLY_ADJUSTED = "seasonally_adjusted"
    SEASONALLY_ADJUSTED_ANNUAL_RATE = "seasonally_adjusted_annual_rate"
    OTHER = "other"
