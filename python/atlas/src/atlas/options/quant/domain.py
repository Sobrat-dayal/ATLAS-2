"""Domain Models for QuantLib Options Strategy Engine (Stage 142)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from atlas.options.domain import (
    AtlasOptionContract,
    ContractAdjustmentStatus,
    DeliverableType,
    ExerciseStyle,
    LegSide,
    MoneynessState,
    OptionDeliverable,
    OptionGreeks,
    OptionQuote,
    OptionType,
    QuoteQualityFlag,
    SettlementMethod,
)


class PricingModelFamily(str, Enum):
    """Supported quantitative derivative pricing model families."""

    BLACK_SCHOLES_MERTON = "BLACK_SCHOLES_MERTON"
    BLACK_76 = "BLACK_76"
    BACHELIER = "BACHELIER"
    BARONE_ADESI_WHALEY = "BARONE_ADESI_WHALEY"
    BJERKSUND_STENSLAND = "BJERKSUND_STENSLAND"
    BINOMIAL_CRR = "BINOMIAL_CRR"
    FINITE_DIFFERENCE = "FINITE_DIFFERENCE"


class GreekUnitConvention(str, Enum):
    """Explicit measurement unit specifications for Greeks."""

    DELTA_PER_UNDERLYING_UNIT = "per 1.0 underlying price unit"
    GAMMA_PER_UNDERLYING_UNIT_SQUARED = "per 1.0 underlying price unit squared"
    THETA_PER_CALENDAR_DAY = "per 1 calendar day"
    THETA_PER_YEAR = "per 1 year (annualized)"
    VEGA_PER_PERCENTAGE_POINT = "per 1 percentage point IV change (0.01)"
    VEGA_PER_VOLATILITY_UNIT = "per 1.0 full volatility unit (1.0)"
    RHO_PER_PERCENTAGE_POINT = "per 100 bps / 1 percentage point rate change (0.01)"
    RHO_PER_BASIS_POINT = "per 1 basis point rate change (0.0001)"


@dataclass
class QuantPricingModelDefinition:
    """Metadata specification for a registered pricing model."""

    model_id: str
    family: PricingModelFamily
    name: str
    description: str
    supported_exercise_styles: List[ExerciseStyle]
    supports_discrete_dividends: bool
    supports_analytic_greeks: bool
    engine_class_name: str
    default_numerical_steps: Optional[int] = None
    is_active: bool = True


@dataclass
class MarketInputSnapshot:
    """Atomic market data input snapshot for reproducible pricing runs."""

    snapshot_id: str
    underlying_symbol: str
    underlying_spot_price: float
    underlying_quote_timestamp: str
    risk_free_rate: float
    rate_curve_name: str
    dividend_yield: float
    dividend_schedule: List[Dict[str, Any]] = field(default_factory=list)
    valuation_as_of: str = ""
    is_stale: bool = False
    source_manifest: Dict[str, str] = field(default_factory=dict)


@dataclass
class QuantModelGreeks:
    """Computed model sensitivities with explicit units."""

    delta: float
    gamma: float
    theta_per_day: float
    theta_annual: float
    vega_per_point: float  # scaled per 1% IV change
    vega_per_unit: float   # unscaled per 1.0 IV unit
    rho_per_point: float   # scaled per 1% rate change
    rho_per_bp: float      # scaled per 1 bp
    vanna: Optional[float] = None
    volga: Optional[float] = None
    calculation_method: str = "ANALYTIC"
    bump_size_used: Optional[float] = None


@dataclass
class QuantPricingDiagnostics:
    """Numerical execution diagnostics for transparency."""

    execution_time_ms: float
    converged: bool
    iterations_or_steps: int
    grid_points: Optional[int] = None
    approximation_error: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    quantlib_version: str = "1.44"


@dataclass
class OptionPricingResult:
    """Complete quantitative pricing output for an option contract."""

    pricing_run_id: str
    contract_id: str
    underlying_symbol: str
    strike_price: float
    expiration_date: str
    exercise_style: ExerciseStyle
    model_id: str
    theoretical_price: float
    observed_market_bid: Optional[float]
    observed_market_ask: Optional[float]
    observed_market_mark: Optional[float]
    model_market_difference: Optional[float]  # Theoretical - Mark
    contract_multiplier: float
    currency: str
    greeks: QuantModelGreeks
    diagnostics: QuantPricingDiagnostics
    valuation_date: str
    market_snapshot_id: str
    pricing_status: str = "SUCCESS"


@dataclass
class QuantStrategyLeg:
    """Validated strategy leg representation for quantitative pricing and payoff."""

    contract_id: str
    side: LegSide
    quantity: int
    entry_premium: float
    multiplier: float
    strike_price: float
    expiration_date: str
    option_type: OptionType
    exercise_style: ExerciseStyle
    custom_fee: float = 0.0


@dataclass
class PreExpirationValuationPoint:
    """Pre-expiration mark-to-market valuation across underlying prices at an intermediate date t."""

    underlying_price: float
    strategy_mark_to_market: float
    pnl_versus_opening: float
    aggregate_delta: float
    aggregate_gamma: float
    aggregate_vega: float
    aggregate_theta: float


@dataclass
class StrategyComparisonItem:
    """Side-by-side comparison record between different strategies."""

    strategy_id: str
    strategy_name: str
    net_opening_cash_flow: float
    is_net_debit: bool
    max_profit: Optional[float]
    max_loss: Optional[float]
    is_unbounded_loss: bool
    breakevens: List[float]
    net_delta: float
    net_gamma: float
    net_theta_per_day: float
    net_vega_per_point: float
    legs_count: int
    underlying_symbol: str


STAGE_142_DISCLAIMERS = {
    "options_risk": (
        "Options involve substantial risk and are not suitable for all investors. Prior to buying or selling "
        "options, investors must read Characteristics and Risks of Standardized Options (ODD)."
    ),
    "model_risk": (
        "Theoretical option values and Greeks are derived from mathematical models (such as Black-Scholes-Merton, "
        "Barone-Adesi-Whaley, or Finite Difference methods). They are analytical approximations based on stated "
        "assumptions (constant volatility, lognormal returns, friction-free markets) and do not represent executable "
        "quotes or guaranteed trading outcomes."
    ),
    "execution_boundary": (
        "ATLAS derivatives workbench is an analytical and quantitative research engine. It performs NO automated "
        "trading, order routing, fill simulation, or paper execution. Historical backtesting is scheduled for Stage 143, "
        "paper trading for Stage 144, and broker integration for Stage 145."
    ),
    "arbitrage_disclaimer": (
        "Differences between model-generated theoretical prices and observed market quotes reflect model basis, "
        "liquidity premia, or friction costs, and must NOT be construed as risk-free arbitrage opportunities."
    ),
    "assignment_risk": (
        "American-style options may be exercised by the holder at any time prior to expiration. Short positions "
        "carry risk of early assignment, especially in-the-money options prior to ex-dividend dates."
    ),
}
