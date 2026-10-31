"""Domain models for ATLAS Options Analytics (Stage 141).

Canonical types for:
- Option Contracts, OSI Symbology & Contract Multipliers
- Deliverable Specifications & Corporate Adjustments
- Option Quotes, Implied Volatility & Source Greeks
- Options Chains & Moneyness Analytics
- Multi-Leg Strategies, Piecewise Payoff & Breakeven Modeling
- Institutional Safeguards & Disclaimers
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OptionType(str, Enum):
    """Option contract call/put type."""
    CALL = "CALL"
    PUT = "PUT"


class ExerciseStyle(str, Enum):
    """Exercise style convention."""
    AMERICAN = "AMERICAN"
    EUROPEAN = "EUROPEAN"
    BERMUDAN = "BERMUDAN"


class SettlementMethod(str, Enum):
    """Settlement method upon exercise or expiration."""
    PHYSICAL = "PHYSICAL"
    CASH = "CASH"


class MoneynessState(str, Enum):
    """Moneyness relative to underlying reference price."""
    IN_THE_MONEY = "IN_THE_MONEY"
    AT_THE_MONEY = "AT_THE_MONEY"
    OUT_OF_THE_MONEY = "OUT_OF_THE_MONEY"


class DeliverableType(str, Enum):
    """Physical or cash deliverable type."""
    STANDARD_100_SHARES = "STANDARD_100_SHARES"
    NONSTANDARD_CASH_AND_SHARES = "NONSTANDARD_CASH_AND_SHARES"
    CASH_INDEX = "CASH_INDEX"
    CUSTOM_LOT_SHARES = "CUSTOM_LOT_SHARES"


class ContractAdjustmentStatus(str, Enum):
    """Corporate action adjustment status."""
    STANDARD = "STANDARD"
    ADJUSTED_CORPORATE_ACTION = "ADJUSTED_CORPORATE_ACTION"


class LegSide(str, Enum):
    """Multi-leg strategy component side."""
    LONG_CALL = "LONG_CALL"
    SHORT_CALL = "SHORT_CALL"
    LONG_PUT = "LONG_PUT"
    SHORT_PUT = "SHORT_PUT"


class QuoteQualityFlag(str, Enum):
    """Market quote validation and sanity tier."""
    VALID = "VALID"
    ZERO_BID = "ZERO_BID"
    CROSSED_MARKET = "CROSSED_MARKET"
    LOCKED_MARKET = "LOCKED_MARKET"
    STALE_QUOTE = "STALE_QUOTE"
    MISSING_ASK = "MISSING_ASK"
    WIDE_SPREAD = "WIDE_SPREAD"


# Institutional Disclaimers
OPTIONS_DISCLAIMERS: Dict[str, str] = {
    "options_risk": (
        "Options involve substantial financial risk and are not suitable for all investors. "
        "Purchasing options carries the risk of total loss of premium paid. "
        "Writing (selling) naked options carries substantial and theoretically unlimited risk of loss."
    ),
    "execution": (
        "Displayed midpoint and theoretical prices are indicative analytical references and do not "
        "guarantee order execution or fill availability in live markets."
    ),
    "payoff": (
        "Expiration payoff diagrams represent theoretical profit/loss at the contract cutoff date "
        "based on explicit input assumptions. They do not represent current mark-to-market valuation or future price forecasts."
    ),
    "stage142_boundary": (
        "Advanced theoretical option pricing, QuantLib valuation engines, interest-rate curves, "
        "dividend yield models, and model-derived Greeks are reserved for Stage 142."
    ),
    "stage143_boundary": (
        "Historical strategy backtesting, execution slippage simulation, and fill modeling are reserved for Stage 143."
    ),
    "no_broker_trading": (
        "ATLAS Options Analytics is an analytical research workspace. No broker order routing, paper order "
        "execution, or live account mutation is performed."
    ),
}


class OptionDeliverable(BaseModel):
    """Deliverable package specification for an option contract."""
    deliverable_type: DeliverableType = DeliverableType.STANDARD_100_SHARES
    shares_count: float = 100.0
    cash_amount: float = 0.0
    underlying_symbol: str
    summary: str = "100 shares of underlying stock"


class AtlasOptionContract(BaseModel):
    """Canonical listed options contract master specification."""
    option_contract_id: str  # Unique internal canonical identity, e.g. "opt_aapl_20240621_c_180000"
    underlying_instrument_id: str  # Canonical underlying instrument ID, e.g. "inst_eq_aapl"
    underlying_symbol: str  # Ticker symbol, e.g. "AAPL"
    market_id: str = "US_OPTIONS"  # e.g. "US_OPTIONS", "NSE_DERIVATIVES"
    exchange_id: str = "CBOE"  # Primary or listing venue
    osi_symbol: Optional[str] = None  # Standard 21-character OCC OSI key where applicable
    option_type: OptionType
    strike_price: float
    strike_currency: str = "USD"
    expiration_date: str  # "YYYY-MM-DD"
    last_trading_date: Optional[str] = None
    exercise_style: ExerciseStyle = ExerciseStyle.AMERICAN
    settlement_method: SettlementMethod = SettlementMethod.PHYSICAL
    contract_multiplier: float = 100.0
    deliverable: OptionDeliverable = Field(default_factory=lambda: OptionDeliverable(underlying_symbol="UNKNOWN"))
    adjustment_status: ContractAdjustmentStatus = ContractAdjustmentStatus.STANDARD
    adjustment_memo: Optional[str] = None
    is_active: bool = True
    corporate_action_id: Optional[str] = None


class OptionGreeks(BaseModel):
    """Source-provided option sensitivities (local model values)."""
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    rho: Optional[float] = None
    source_model: Optional[str] = None
    as_of: Optional[str] = None
    theta_unit: str = "PER_CALENDAR_DAY"
    vega_unit: str = "PER_VOL_POINT"


class OptionQuote(BaseModel):
    """Normalized options market quote."""
    contract_id: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_size: Optional[int] = None
    ask_size: Optional[int] = None
    last_price: Optional[float] = None
    last_trade_time: Optional[str] = None
    volume: int = 0
    open_interest: int = 0
    open_interest_as_of: Optional[str] = None
    implied_volatility: Optional[float] = None
    greeks: Optional[OptionGreeks] = None
    quote_timestamp: str
    source_id: str = "SRC_CBOE_AUTHORIZED"
    is_delayed: bool = True
    delay_minutes: int = 15
    quality_flags: List[QuoteQualityFlag] = Field(default_factory=list)
    currency: str = "USD"


class OptionChainRow(BaseModel):
    """A single strike row in a dual-sided options chain."""
    strike_price: float
    moneyness: MoneynessState
    call_contract: Optional[AtlasOptionContract] = None
    call_quote: Optional[OptionQuote] = None
    put_contract: Optional[AtlasOptionContract] = None
    put_quote: Optional[OptionQuote] = None


class OptionChainResponse(BaseModel):
    """Complete options chain response for an underlying and expiration."""
    underlying_symbol: str
    underlying_price: float
    underlying_quote_time: str
    expiration_date: str
    days_to_expiration: int
    rows: List[OptionChainRow] = Field(default_factory=list)
    total_call_volume: int = 0
    total_put_volume: int = 0
    total_call_oi: int = 0
    total_put_oi: int = 0
    put_call_volume_ratio: Optional[float] = None
    put_call_oi_ratio: Optional[float] = None
    source_id: str = "SRC_CBOE_AUTHORIZED"
    is_delayed: bool = True
    delay_minutes: int = 15
    disclaimers: Dict[str, str] = Field(default_factory=lambda: dict(OPTIONS_DISCLAIMERS))


class OptionStrategyLeg(BaseModel):
    """Single leg in a multi-leg options strategy."""
    contract_id: str
    side: LegSide
    quantity: int = 1
    entry_premium: float
    premium_basis: str = "INDICATIVE_BID_ASK"
    multiplier: float = 100.0
    estimated_fee: float = 0.0
    custom_fee: float = 0.0


class PayoffCoordinate(BaseModel):
    """Payoff point on underlying settlement price grid."""
    underlying_price: float
    payoff: float
    is_breakeven: bool = False


class OptionStrategyAnalysisResult(BaseModel):
    """Analytical expiration payoff, breakeven and risk bounds for a strategy."""
    strategy_name: str
    underlying_symbol: str
    expiration_date: str
    legs: List[OptionStrategyLeg]
    net_opening_cash_flow: float  # signed: negative = debit paid, positive = credit received
    is_net_debit: bool
    total_estimated_fees: float
    breakevens: List[float]
    max_profit: Optional[float]  # None if mathematically unbounded
    max_loss: Optional[float]  # None if mathematically unbounded
    is_unbounded_profit: bool = False
    is_unbounded_loss: bool = False
    payoff_curve: List[PayoffCoordinate] = Field(default_factory=list)
    risk_warnings: List[str] = Field(default_factory=list)
    disclaimers: Dict[str, str] = Field(default_factory=lambda: dict(OPTIONS_DISCLAIMERS))
    calculation_version: str = "Stage 141 (v1.0.0)"
