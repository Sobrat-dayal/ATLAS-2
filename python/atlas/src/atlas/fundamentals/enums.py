from enum import Enum


class FinancialStatementType(str, Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW_STATEMENT = "cash_flow_statement"

class FinancialPeriodNature(str, Enum):
    INSTANT = "instant"
    DURATION = "duration"

class FiscalPeriod(str, Enum):
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"
    H1 = "h1"
    H2 = "h2"
    NINE_MONTHS = "nine_months"
    FY = "fy"
    OTHER = "other"

class ReportingPeriodType(str, Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    NINE_MONTH = "nine_month"
    OTHER = "other"

class AccountingStandard(str, Enum):
    US_GAAP = "us_gaap"
    IFRS = "ifrs"
    OTHER = "other"
    UNKNOWN = "unknown"

class AuditStatus(str, Enum):
    AUDITED = "audited"
    UNAUDITED = "unaudited"
    UNKNOWN = "unknown"

class FinancialUnitKind(str, Enum):
    CURRENCY = "currency"
    SHARES = "shares"
    CURRENCY_PER_SHARE = "currency_per_share"
    COUNT = "count"
    DIMENSIONLESS = "dimensionless"
    PERCENT = "percent"

class FundamentalDataOperation(str, Enum):
    INCOME_STATEMENTS = "income_statements"
    BALANCE_SHEETS = "balance_sheets"
    CASH_FLOW_STATEMENTS = "cash_flow_statements"
    FINANCIAL_FACTS = "financial_facts"
