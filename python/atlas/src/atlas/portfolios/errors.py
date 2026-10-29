"""ATLAS Portfolios V1 — Typed Domain Exceptions.

All domain errors derive from PortfolioError and map to specific HTTP status
codes and error codes in the API layer.
"""

from typing import Optional


class PortfolioError(Exception):
    """Base exception for all Portfolio domain operations."""

    def __init__(self, message: str, code: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


# ---------------------------------------------------------------------------
# Portfolio Entity Errors
# ---------------------------------------------------------------------------


class PortfolioNotFoundError(PortfolioError):
    def __init__(self, portfolio_id: str):
        super().__init__(
            f"Portfolio '{portfolio_id}' was not found.",
            code="PORTFOLIO_NOT_FOUND",
            status_code=404,
        )


class PortfolioAccessDeniedError(PortfolioError):
    def __init__(self, portfolio_id: str):
        super().__init__(
            f"Access denied to portfolio '{portfolio_id}'.",
            code="PORTFOLIO_ACCESS_DENIED",
            status_code=403,
        )


class PortfolioNameInvalidError(PortfolioError):
    def __init__(self, message: str = "Portfolio name cannot be empty."):
        super().__init__(
            message,
            code="PORTFOLIO_NAME_INVALID",
            status_code=400,
        )


class PortfolioBaseCurrencyUnsupportedError(PortfolioError):
    def __init__(self, currency: str):
        super().__init__(
            f"Portfolio base currency '{currency}' is unsupported.",
            code="PORTFOLIO_BASE_CURRENCY_UNSUPPORTED",
            status_code=400,
        )


class PortfolioRevisionConflictError(PortfolioError):
    def __init__(self, expected: int, current: int):
        super().__init__(
            f"Portfolio revision conflict: expected {expected}, current is {current}.",
            code="PORTFOLIO_REVISION_CONFLICT",
            status_code=409,
        )


class PortfolioArchivedError(PortfolioError):
    def __init__(self, portfolio_id: str):
        super().__init__(
            f"Portfolio '{portfolio_id}' is archived and read-only.",
            code="PORTFOLIO_ARCHIVED",
            status_code=400,
        )


class PortfolioDeleteConflictError(PortfolioError):
    def __init__(self, reason: str):
        super().__init__(
            f"Cannot delete portfolio: {reason}",
            code="PORTFOLIO_DELETE_CONFLICT",
            status_code=409,
        )


# ---------------------------------------------------------------------------
# Account Entity Errors
# ---------------------------------------------------------------------------


class PortfolioAccountNotFoundError(PortfolioError):
    def __init__(self, account_id: str):
        super().__init__(
            f"Account '{account_id}' was not found.",
            code="PORTFOLIO_ACCOUNT_NOT_FOUND",
            status_code=404,
        )


class PortfolioAccountAccessDeniedError(PortfolioError):
    def __init__(self, account_id: str):
        super().__init__(
            f"Access denied to account '{account_id}'.",
            code="PORTFOLIO_ACCOUNT_ACCESS_DENIED",
            status_code=403,
        )


class PortfolioAccountTypeUnsupportedError(PortfolioError):
    def __init__(self, account_type: str):
        super().__init__(
            f"Account type '{account_type}' is unsupported.",
            code="PORTFOLIO_ACCOUNT_TYPE_UNSUPPORTED",
            status_code=400,
        )


class PortfolioAccountCurrencyUnsupportedError(PortfolioError):
    def __init__(self, currency: str):
        super().__init__(
            f"Account currency '{currency}' is unsupported.",
            code="PORTFOLIO_ACCOUNT_CURRENCY_UNSUPPORTED",
            status_code=400,
        )


class PortfolioAccountArchivedError(PortfolioError):
    def __init__(self, account_id: str):
        super().__init__(
            f"Account '{account_id}' is archived and cannot accept transactions.",
            code="PORTFOLIO_ACCOUNT_ARCHIVED",
            status_code=400,
        )


class PortfolioAccountHasPostedTransactionsError(PortfolioError):
    def __init__(self, account_id: str, count: int):
        super().__init__(
            f"Account '{account_id}' cannot be deleted because it contains {count} posted transactions.",
            code="PORTFOLIO_ACCOUNT_HAS_POSTED_TRANSACTIONS",
            status_code=409,
        )


class PortfolioAccountPolicyConflictError(PortfolioError):
    def __init__(self, message: str):
        super().__init__(
            message,
            code="PORTFOLIO_ACCOUNT_POLICY_CONFLICT",
            status_code=400,
        )


# ---------------------------------------------------------------------------
# Transaction Errors
# ---------------------------------------------------------------------------


class PortfolioTransactionNotFoundError(PortfolioError):
    def __init__(self, transaction_id: str):
        super().__init__(
            f"Transaction '{transaction_id}' was not found.",
            code="PORTFOLIO_TRANSACTION_NOT_FOUND",
            status_code=404,
        )


class PortfolioTransactionTypeUnsupportedError(PortfolioError):
    def __init__(self, tx_type: str):
        super().__init__(
            f"Transaction type '{tx_type}' is unsupported.",
            code="PORTFOLIO_TRANSACTION_TYPE_UNSUPPORTED",
            status_code=400,
        )


class PortfolioTransactionInvalidQuantityError(PortfolioError):
    def __init__(self, quantity: str, reason: str = "Quantity must be strictly positive."):
        super().__init__(
            f"Invalid transaction quantity '{quantity}': {reason}",
            code="PORTFOLIO_TRANSACTION_INVALID_QUANTITY",
            status_code=400,
        )


class PortfolioTransactionInvalidPriceError(PortfolioError):
    def __init__(self, price: str, reason: str = "Price must be non-negative."):
        super().__init__(
            f"Invalid transaction price '{price}': {reason}",
            code="PORTFOLIO_TRANSACTION_INVALID_PRICE",
            status_code=400,
        )


class PortfolioTransactionCurrencyMismatchError(PortfolioError):
    def __init__(self, expected: str, provided: str):
        super().__init__(
            f"Currency mismatch: expected '{expected}', got '{provided}'.",
            code="PORTFOLIO_TRANSACTION_CURRENCY_MISMATCH",
            status_code=400,
        )


class PortfolioTransactionInvalidSettlementError(PortfolioError):
    def __init__(self, message: str):
        super().__init__(
            f"Invalid transaction settlement: {message}",
            code="PORTFOLIO_TRANSACTION_INVALID_SETTLEMENT",
            status_code=400,
        )


class PortfolioTransactionInsufficientHoldingsError(PortfolioError):
    def __init__(self, instrument_id: str, available: str, requested: str):
        super().__init__(
            f"Insufficient holdings for instrument '{instrument_id}': available {available}, requested {requested}.",
            code="PORTFOLIO_TRANSACTION_INSUFFICIENT_HOLDINGS",
            status_code=400,
        )


class PortfolioTransactionInsufficientCashError(PortfolioError):
    def __init__(self, currency: str, available: str, required: str):
        super().__init__(
            f"Insufficient settled cash for currency '{currency}': available {available}, required {required}.",
            code="PORTFOLIO_TRANSACTION_INSUFFICIENT_CASH",
            status_code=400,
        )


class PortfolioTransactionDuplicateError(PortfolioError):
    def __init__(self, idempotency_key: str):
        super().__init__(
            f"Transaction with idempotency key '{idempotency_key}' has already been posted.",
            code="PORTFOLIO_TRANSACTION_DUPLICATE",
            status_code=409,
        )


class PortfolioTransactionAlreadyReversedError(PortfolioError):
    def __init__(self, transaction_id: str):
        super().__init__(
            f"Transaction '{transaction_id}' is already reversed or corrected.",
            code="PORTFOLIO_TRANSACTION_ALREADY_REVERSED",
            status_code=409,
        )


class PortfolioTransactionReversalInvalidError(PortfolioError):
    def __init__(self, reason: str):
        super().__init__(
            f"Cannot reverse transaction: {reason}",
            code="PORTFOLIO_TRANSACTION_REVERSAL_INVALID",
            status_code=400,
        )


class PortfolioTransactionCorrectionConflictError(PortfolioError):
    def __init__(self, reason: str):
        super().__init__(
            f"Transaction correction conflict: {reason}",
            code="PORTFOLIO_TRANSACTION_CORRECTION_CONFLICT",
            status_code=409,
        )


class PortfolioTransactionAccountingFailedError(PortfolioError):
    def __init__(self, reason: str):
        super().__init__(
            f"Transaction accounting engine failure: {reason}",
            code="PORTFOLIO_TRANSACTION_ACCOUNTING_FAILED",
            status_code=500,
        )


class PortfolioTransactionInstrumentUnresolvedError(PortfolioError):
    def __init__(self, identifier: str):
        super().__init__(
            f"Could not resolve canonical instrument for identifier '{identifier}'.",
            code="PORTFOLIO_TRANSACTION_INSTRUMENT_UNRESOLVED",
            status_code=400,
        )


class PortfolioTransactionInstrumentUnsupportedError(PortfolioError):
    def __init__(self, instrument_id: str, reason: str):
        super().__init__(
            f"Instrument '{instrument_id}' is unsupported for portfolio transactions: {reason}",
            code="PORTFOLIO_TRANSACTION_INSTRUMENT_UNSUPPORTED",
            status_code=400,
        )


# ---------------------------------------------------------------------------
# Position & Cost Basis Errors
# ---------------------------------------------------------------------------


class PortfolioPositionNotFoundError(PortfolioError):
    def __init__(self, instrument_id: str):
        super().__init__(
            f"No open position found for instrument '{instrument_id}'.",
            code="PORTFOLIO_POSITION_NOT_FOUND",
            status_code=404,
        )


class PortfolioPositionProjectionStaleError(PortfolioError):
    def __init__(self, message: str):
        super().__init__(
            f"Position projection is stale or out of date: {message}",
            code="PORTFOLIO_POSITION_PROJECTION_STALE",
            status_code=409,
        )


class PortfolioPositionReconciliationFailedError(PortfolioError):
    def __init__(self, message: str):
        super().__init__(
            f"Position reconciliation check failed: {message}",
            code="PORTFOLIO_POSITION_RECONCILIATION_FAILED",
            status_code=500,
        )


class PortfolioCostBasisMethodUnsupportedError(PortfolioError):
    def __init__(self, method: str):
        super().__init__(
            f"Cost basis method '{method}' is unsupported. Only FIFO is supported in Stage 110.",
            code="PORTFOLIO_COST_BASIS_METHOD_UNSUPPORTED",
            status_code=400,
        )


class PortfolioCostBasisLotInsufficientError(PortfolioError):
    def __init__(self, message: str):
        super().__init__(
            f"Insufficient tax lots to satisfy cost basis allocation: {message}",
            code="PORTFOLIO_COST_BASIS_LOT_INSUFFICIENT",
            status_code=400,
        )


# ---------------------------------------------------------------------------
# Valuation & Reconciliation Errors
# ---------------------------------------------------------------------------


class PortfolioValuationCalculationFailedError(PortfolioError):
    def __init__(self, reason: str):
        super().__init__(
            f"Valuation calculation failed: {reason}",
            code="PORTFOLIO_VALUATION_CALCULATION_FAILED",
            status_code=500,
        )


class PortfolioValuationIncompleteError(PortfolioError):
    def __init__(self, missing_items: list[str]):
        super().__init__(
            f"Valuation is incomplete due to missing data: {', '.join(missing_items)}",
            code="PORTFOLIO_VALUATION_INCOMPLETE",
            status_code=422,
        )


class PortfolioReconciliationFailedError(PortfolioError):
    def __init__(self, discrepancies: list[str]):
        super().__init__(
            f"Portfolio reconciliation failed with discrepancies: {'; '.join(discrepancies)}",
            code="PORTFOLIO_RECONCILIATION_FAILED",
            status_code=500,
        )

