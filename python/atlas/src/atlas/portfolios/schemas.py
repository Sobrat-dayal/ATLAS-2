"""ATLAS Portfolios V1 — Pydantic Request & Response Schemas.

Defines all input validation models and response DTOs for the portfolio API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from atlas.portfolios.enums import (
    AccountStatus,
    AccountType,
    CostBasisMethod,
    PortfolioStatus,
    PortfolioType,
    QuoteFreshness,
    ReconciliationStatus,
    TransactionStatus,
    TransactionType,
    ValuationCompletenessStatus,
)


# ---------------------------------------------------------------------------
# Portfolio Schemas
# ---------------------------------------------------------------------------


class PortfolioCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, max_length=200, description="Name of the portfolio.")
    base_currency: str = Field(
        default="USD", min_length=3, max_length=5, description="ISO-4217 reporting currency."
    )
    portfolio_type: PortfolioType = Field(
        default=PortfolioType.PERSONAL, description="Institutional portfolio classification."
    )
    description: Optional[str] = Field(
        default=None, max_length=1000, description="Optional description."
    )


class PortfolioUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[PortfolioStatus] = None
    revision: int = Field(..., description="Optimistic concurrency revision tag.")


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    portfolio_type: PortfolioType
    base_currency: str
    status: PortfolioStatus
    cost_basis_method: CostBasisMethod
    description: Optional[str] = None
    account_count: int = 0
    revision: int
    created_at: datetime
    updated_at: datetime


class PortfolioListResponse(BaseModel):
    items: list[PortfolioResponse]
    total: int


# ---------------------------------------------------------------------------
# Account Schemas
# ---------------------------------------------------------------------------


class AccountCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_name: str = Field(..., min_length=1, max_length=200)
    account_type: AccountType = Field(default=AccountType.INVESTMENT_ACCOUNT)
    primary_currency: str = Field(default="USD", min_length=3, max_length=5)
    custodian_name: Optional[str] = Field(default=None, max_length=200)
    account_number_mask: Optional[str] = Field(default=None, max_length=50)


class AccountUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    custodian_name: Optional[str] = Field(default=None, max_length=200)
    account_number_mask: Optional[str] = Field(default=None, max_length=50)
    status: Optional[AccountStatus] = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    portfolio_id: str
    user_id: str
    account_name: str
    account_type: AccountType
    primary_currency: str
    custodian_name: Optional[str] = None
    account_number_mask: Optional[str] = None
    status: AccountStatus
    created_at: datetime
    updated_at: datetime


class AccountListResponse(BaseModel):
    items: list[AccountResponse]
    total: int


# ---------------------------------------------------------------------------
# Transaction Schemas
# ---------------------------------------------------------------------------


class TransactionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    transaction_type: TransactionType
    cash_currency: str = Field(default="USD", min_length=3, max_length=5)
    trade_date: Optional[datetime] = None
    settlement_date: Optional[datetime] = None
    instrument_id: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    gross_amount: Optional[Decimal] = None
    fee: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    idempotency_key: Optional[str] = None
    notes: Optional[str] = None


class TransactionPreviewResponse(BaseModel):
    transaction_type: str
    gross_amount: str
    fee: str
    tax: str
    net_cash_amount: str
    estimated_resulting_cash: str
    resulting_quantity: Optional[str] = None
    unit_cost_basis: Optional[str] = None
    consumed_basis: Optional[str] = None
    estimated_realized_pnl: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    portfolio_id: str
    account_id: str
    user_id: str
    transaction_type: TransactionType
    status: TransactionStatus
    cash_currency: str
    trade_date: datetime
    settlement_date: datetime
    instrument_id: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    quantity: Optional[str] = None
    unit_price: Optional[str] = None
    gross_amount: Optional[str] = None
    fee: str
    tax: str
    net_cash_amount: str
    idempotency_key: Optional[str] = None
    notes: Optional[str] = None
    reverses_transaction_id: Optional[str] = None
    reversed_by_transaction_id: Optional[str] = None
    created_at: datetime


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int


class TransactionReverseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str = Field(..., min_length=3, max_length=500)


class TransactionCorrectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    replacement: TransactionCreateRequest
    reason: str = Field(..., min_length=3, max_length=500)


# ---------------------------------------------------------------------------
# Position & Lot Schemas
# ---------------------------------------------------------------------------


class PositionResponse(BaseModel):
    portfolio_id: str
    account_id: Optional[str] = None
    instrument_id: str
    symbol: str
    exchange: str
    company_name: Optional[str] = None
    quantity: str
    open_lot_count: int
    remaining_cost_basis: str
    cost_basis_currency: str
    average_unit_cost: Optional[str] = None
    realized_pnl: str
    unrealized_pnl: Optional[str] = None
    as_of: datetime


class PositionListResponse(BaseModel):
    items: list[PositionResponse]
    total: int


class LotResponse(BaseModel):
    id: str
    portfolio_id: str
    account_id: str
    instrument_id: str
    acquisition_transaction_id: str
    acquisition_date: datetime
    original_quantity: str
    remaining_quantity: str
    unit_cost_basis: str
    total_cost_basis: str
    currency: str
    is_fully_disposed: bool
    disposed_at: Optional[datetime] = None


class LotListResponse(BaseModel):
    items: list[LotResponse]
    total: int


# ---------------------------------------------------------------------------
# Cash Schemas
# ---------------------------------------------------------------------------


class CashBalanceResponse(BaseModel):
    account_id: str
    currency: str
    posted_cash: str
    settled_cash: str
    unsettled_receivable: str
    unsettled_payable: str
    available_cash: str
    as_of: datetime


class CashLedgerEntryResponse(BaseModel):
    id: str
    account_id: str
    transaction_id: str
    currency: str
    amount: str
    balance_type: str
    effective_date: datetime
    description: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Valuation Schemas
# ---------------------------------------------------------------------------


class PositionValuationResponse(BaseModel):
    instrument_id: str
    symbol: str
    exchange: str
    quantity: str
    remaining_basis: str
    basis_currency: str
    valuation_status: ValuationCompletenessStatus
    quote_freshness: QuoteFreshness
    account_id: Optional[str] = None
    company_name: Optional[str] = None
    mark_price: Optional[str] = None
    price_currency: Optional[str] = None
    mark_as_of: Optional[datetime] = None
    mark_source: Optional[str] = None
    native_market_value: Optional[str] = None
    fx_rate_to_base: Optional[str] = None
    fx_pair: Optional[str] = None
    fx_as_of: Optional[datetime] = None
    base_market_value: Optional[str] = None
    unrealized_pnl: Optional[str] = None


class CashValuationResponse(BaseModel):
    account_id: str
    currency: str
    posted_cash: str
    settled_cash: str
    unsettled_receivable: str
    unsettled_payable: str
    available_cash: str
    fx_rate_to_base: str
    base_cash_value: str
    as_of: datetime


class ValuationResponse(BaseModel):
    id: str
    portfolio_id: str
    as_of: datetime
    base_currency: str
    valuation_status: ValuationCompletenessStatus
    known_valued_subtotal: str
    verified_total_portfolio_value: Optional[str] = None
    total_positions_market_value: Optional[str] = None
    total_cash_market_value: str
    total_cost_basis: str
    total_unrealized_pnl: Optional[str] = None
    total_realized_pnl: str
    missing_prices_count: int
    missing_fx_count: int
    stale_quotes_count: int
    position_valuations: list[PositionValuationResponse]
    cash_valuations: list[CashValuationResponse]
    source_manifest: dict[str, Any]
    calculation_version: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Reconciliation Schemas
# ---------------------------------------------------------------------------


class ReconciliationResponse(BaseModel):
    portfolio_id: str
    status: ReconciliationStatus
    reconciliation_timestamp: datetime
    total_transactions_checked: int
    total_lots_checked: int
    total_positions_checked: int
    total_cash_entries_checked: int
    discrepancies: list[str]
    warnings: list[str]
    is_balanced: bool

