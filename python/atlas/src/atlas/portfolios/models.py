"""ATLAS Portfolios V1 — Domain Models and Dataclasses.

Implements all ledger, tax-lot, position, cash balance, valuation snapshot,
and reconciliation dataclasses for institutional portfolio management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from atlas.portfolios.enums import (
    AccountStatus,
    AccountType,
    CashBalanceType,
    CostBasisMethod,
    PortfolioStatus,
    PortfolioType,
    QuoteFreshness,
    ReconciliationStatus,
    TransactionStatus,
    TransactionType,
    ValuationCompletenessStatus,
)


@dataclass
class Portfolio:
    """Canonical portfolio container."""

    id: str
    user_id: str
    name: str
    portfolio_type: PortfolioType
    base_currency: str
    status: PortfolioStatus = PortfolioStatus.ACTIVE
    cost_basis_method: CostBasisMethod = CostBasisMethod.FIFO
    description: Optional[str] = None
    revision: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InvestmentAccount:
    """Institutional investment account record belonging to a portfolio."""

    id: str
    portfolio_id: str
    user_id: str
    account_name: str
    account_type: AccountType
    primary_currency: str
    custodian_name: Optional[str] = None
    account_number_mask: Optional[str] = None
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioTransaction:
    """Immutable ledger transaction journal entry."""

    id: str
    portfolio_id: str
    account_id: str
    user_id: str
    transaction_type: TransactionType
    cash_currency: str
    trade_date: datetime
    settlement_date: datetime
    status: TransactionStatus = TransactionStatus.POSTED
    instrument_id: Optional[str] = None
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    gross_amount: Optional[Decimal] = None
    fee: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    net_cash_amount: Decimal = Decimal("0")
    idempotency_key: Optional[str] = None
    notes: Optional[str] = None
    reverses_transaction_id: Optional[str] = None
    reversed_by_transaction_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioCashLedgerEntry:
    """Granular cash journal entry."""

    id: str
    portfolio_id: str
    account_id: str
    transaction_id: str
    currency: str
    amount: Decimal
    balance_type: CashBalanceType
    effective_date: datetime
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioSecurityLot:
    """FIFO tax-lot record for an open or partially disposed security position."""

    id: str
    portfolio_id: str
    account_id: str
    instrument_id: str
    acquisition_transaction_id: str
    acquisition_date: datetime
    original_quantity: Decimal
    remaining_quantity: Decimal
    unit_cost_basis: Decimal
    total_cost_basis: Decimal
    currency: str
    is_fully_disposed: bool = False
    disposed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioLotConsumption:
    """Audit record of tax-lot consumption during a sale."""

    id: str
    sell_transaction_id: str
    lot_id: str
    quantity_consumed: Decimal
    unit_cost_basis: Decimal
    total_cost_basis_consumed: Decimal
    proceeds_allocated: Decimal
    fee_allocated: Decimal
    realized_pnl: Decimal
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioPosition:
    """Projected security holding derived deterministically from the transaction journal."""

    portfolio_id: str
    instrument_id: str
    symbol: str
    exchange: str
    quantity: Decimal
    open_lot_count: int
    remaining_cost_basis: Decimal
    cost_basis_currency: str
    average_unit_cost: Optional[Decimal]
    realized_pnl: Decimal
    as_of: datetime
    account_id: Optional[str] = None
    company_name: Optional[str] = None
    unrealized_pnl: Optional[Decimal] = None
    projection_revision: int = 1


@dataclass
class PortfolioCashBalance:
    """Per-account, per-currency cash balance snapshot."""

    account_id: str
    currency: str
    posted_cash: Decimal
    settled_cash: Decimal
    unsettled_receivable: Decimal
    unsettled_payable: Decimal
    available_cash: Decimal
    as_of: datetime


@dataclass
class PortfolioPositionValuation:
    """Marked-to-market valuation row for an individual security position."""

    instrument_id: str
    symbol: str
    exchange: str
    quantity: Decimal
    remaining_basis: Decimal
    basis_currency: str
    valuation_status: ValuationCompletenessStatus
    quote_freshness: QuoteFreshness
    account_id: Optional[str] = None
    company_name: Optional[str] = None
    mark_price: Optional[Decimal] = None
    price_currency: Optional[str] = None
    mark_as_of: Optional[datetime] = None
    mark_source: Optional[str] = None
    native_market_value: Optional[Decimal] = None
    fx_rate_to_base: Optional[Decimal] = None
    fx_pair: Optional[str] = None
    fx_as_of: Optional[datetime] = None
    base_market_value: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None


@dataclass
class PortfolioCashValuation:
    """Marked-to-market valuation row for account cash balances."""

    account_id: str
    currency: str
    posted_cash: Decimal
    settled_cash: Decimal
    unsettled_receivable: Decimal
    unsettled_payable: Decimal
    available_cash: Decimal
    fx_rate_to_base: Decimal
    base_cash_value: Decimal
    as_of: datetime


@dataclass
class PortfolioValuation:
    """Complete portfolio valuation snapshot."""

    id: str
    portfolio_id: str
    as_of: datetime
    base_currency: str
    valuation_status: ValuationCompletenessStatus
    known_valued_subtotal: Decimal
    total_cash_market_value: Decimal
    total_cost_basis: Decimal
    total_realized_pnl: Decimal
    missing_prices_count: int
    missing_fx_count: int
    stale_quotes_count: int
    position_valuations: list[PortfolioPositionValuation] = field(default_factory=list)
    cash_valuations: list[PortfolioCashValuation] = field(default_factory=list)
    source_manifest: dict[str, Any] = field(default_factory=dict)
    calculation_version: str = "1.0.0"
    verified_total_portfolio_value: Optional[Decimal] = None
    total_positions_market_value: Optional[Decimal] = None
    total_unrealized_pnl: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioReconciliationResult:
    """Audit verification report reconciling transaction journal to holdings and cash."""

    portfolio_id: str
    status: ReconciliationStatus
    reconciliation_timestamp: datetime
    total_transactions_checked: int
    total_lots_checked: int
    total_positions_checked: int
    total_cash_entries_checked: int
    discrepancies: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_balanced: bool = True

