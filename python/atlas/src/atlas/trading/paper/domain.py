"""ATLAS Paper Trading Engine — Domain Models (Stage 144)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class PaperOrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIAL = "PARTIAL"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class PaperOrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PaperOrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class AssetClass(str, Enum):
    EQUITY = "EQUITY"
    OPTION = "OPTION"
    FUTURE = "FUTURE"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"


class TimeInForce(str, Enum):
    DAY = "DAY"
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    GTD = "GTD"


class OptionSide(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


# ---------------------------------------------------------------------------
# Core Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class PaperFill:
    """Represents a single fill (execution) of an order."""

    fill_id: str
    order_id: str
    account_id: str
    symbol: str
    side: PaperOrderSide
    qty: float
    price: float
    fee: float
    slippage_cost: float
    filled_at: datetime
    asset_class: AssetClass


@dataclass
class PaperOrder:
    """Represents a paper trading order."""

    order_id: str
    account_id: str
    symbol: str
    side: PaperOrderSide
    order_type: PaperOrderType
    qty: float
    filled_qty: float
    limit_price: Optional[float]
    stop_price: Optional[float]
    status: PaperOrderStatus
    asset_class: AssetClass
    time_in_force: TimeInForce
    submitted_at: datetime
    updated_at: datetime
    fills: List[PaperFill] = field(default_factory=list)
    option_contract: Optional[Dict] = None
    notes: str = ""
    client_order_id: Optional[str] = None


@dataclass
class PaperPosition:
    """Represents an open paper trading position."""

    position_id: str
    account_id: str
    symbol: str
    asset_class: AssetClass
    side: PaperOrderSide
    qty: float
    avg_cost: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    opened_at: datetime
    updated_at: datetime
    option_contract: Optional[Dict] = None


@dataclass
class PaperAccount:
    """Represents a paper trading account."""

    account_id: str
    tenant_id: str
    label: str
    currency: str
    initial_cash: float
    cash: float
    equity: float
    margin_used: float
    buying_power: float
    daily_realized_pnl: float
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    kill_switch_active: bool = False
    description: str = ""


@dataclass
class RiskPolicy:
    """Risk policy constraints for a paper trading account."""

    max_order_value: float = 50_000.0
    max_position_value: float = 100_000.0
    max_daily_loss: float = 5_000.0
    max_drawdown_pct: float = 0.20
    max_open_orders: int = 50
    max_notional_per_symbol: float = 25_000.0
    leverage_limit: float = 2.0


@dataclass
class KillSwitchEvent:
    """Records when and why a kill switch was activated."""

    account_id: str
    triggered_at: datetime
    reason: str
    triggered_by: str


@dataclass
class AccountSnapshot:
    """Point-in-time snapshot of account state."""

    snapshot_id: str
    account_id: str
    cash: float
    equity: float
    positions_value: float
    margin_used: float
    realized_pnl: float
    unrealized_pnl: float
    timestamp: datetime


# ---------------------------------------------------------------------------
# Disclaimers
# ---------------------------------------------------------------------------

STAGE_144_DISCLAIMERS: Dict[str, str] = {
    "paper_only": (
        "PAPER TRADING ONLY — All account balances, fills, positions, and P&L are "
        "entirely virtual and simulated. No real money is involved."
    ),
    "no_real_broker": (
        "NO REAL BROKER CONNECTION — This engine does not connect to any live brokerage, "
        "exchange, or market-data feed. All executions are simulated internally."
    ),
    "simulated_fills": (
        "SIMULATED FILLS — Order fills are computed using synthetic bid/ask quotes with "
        "configurable fee and slippage models. Results do not reflect actual market conditions."
    ),
    "hypothetical": (
        "HYPOTHETICAL PERFORMANCE — Past or simulated performance of paper trading strategies "
        "is not indicative of future real-money results. Use for educational and testing purposes only."
    ),
}
