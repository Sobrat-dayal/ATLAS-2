"""ATLAS Portfolios V1 — Enumerations and Classification Registries.

Defines the institutional portfolio, investment account, transaction, lot,
cash balance, valuation completeness, and reconciliation status enums according
to Stage 110 specifications.
"""

from enum import Enum


class PortfolioType(str, Enum):
    """Institutional classification of a managed portfolio."""

    PERSONAL = "PERSONAL"
    MODEL_ACCOUNTING = "MODEL_ACCOUNTING"
    INSTITUTIONAL = "INSTITUTIONAL"


class PortfolioStatus(str, Enum):
    """Lifecycle status of a portfolio."""

    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class AccountType(str, Enum):
    """Supported investment account containers."""

    BROKERAGE_RECORD = "BROKERAGE_RECORD"
    INVESTMENT_ACCOUNT = "INVESTMENT_ACCOUNT"
    CASH_ACCOUNT = "CASH_ACCOUNT"
    MANUAL_PORTFOLIO_ACCOUNT = "MANUAL_PORTFOLIO_ACCOUNT"


class AccountStatus(str, Enum):
    """Lifecycle status of an individual account."""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class TransactionType(str, Enum):
    """Immutable ledger transaction types supported by Portfolios V1."""

    BUY = "BUY"
    SELL = "SELL"
    CASH_DEPOSIT = "CASH_DEPOSIT"
    CASH_WITHDRAWAL = "CASH_WITHDRAWAL"
    CASH_TRANSFER_IN = "CASH_TRANSFER_IN"
    CASH_TRANSFER_OUT = "CASH_TRANSFER_OUT"
    CASH_DIVIDEND = "CASH_DIVIDEND"
    CASH_INTEREST = "CASH_INTEREST"
    ACCOUNT_FEE = "ACCOUNT_FEE"
    WITHHOLDING_TAX = "WITHHOLDING_TAX"
    STOCK_SPLIT_ADJUSTMENT = "STOCK_SPLIT_ADJUSTMENT"
    CORRECTION_REVERSAL = "CORRECTION_REVERSAL"


class TransactionStatus(str, Enum):
    """State of a posted transaction journal record."""

    POSTED = "POSTED"
    REVERSED = "REVERSED"
    CORRECTED = "CORRECTED"


class CashBalanceType(str, Enum):
    """Economic cash balance classifications."""

    POSTED_CASH = "POSTED_CASH"
    SETTLED_CASH = "SETTLED_CASH"
    UNSETTLED_RECEIVABLE = "UNSETTLED_RECEIVABLE"
    UNSETTLED_PAYABLE = "UNSETTLED_PAYABLE"
    AVAILABLE_CASH = "AVAILABLE_CASH"


class CostBasisMethod(str, Enum):
    """Tax-lot identification and cost-basis accounting methods."""

    FIFO = "FIFO"


class ValuationCompletenessStatus(str, Enum):
    """Completeness state of a computed portfolio or account valuation."""

    COMPLETE = "COMPLETE"
    PARTIAL_MISSING_PRICES = "PARTIAL_MISSING_PRICES"
    PARTIAL_MISSING_FX = "PARTIAL_MISSING_FX"
    PARTIAL_STALE_DATA = "PARTIAL_STALE_DATA"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"


class QuoteFreshness(str, Enum):
    """Freshness classification for market data observations."""

    REALTIME = "REALTIME"
    DELAYED = "DELAYED"
    END_OF_DAY = "END_OF_DAY"
    HISTORICAL = "HISTORICAL"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"


class ReconciliationStatus(str, Enum):
    """Integrity audit result for ledger and projection reconciliation."""

    RECONCILED = "RECONCILED"
    RECONCILIATION_WARNING = "RECONCILIATION_WARNING"
    OUT_OF_BALANCE = "OUT_OF_BALANCE"
    INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

