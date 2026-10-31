"""Domain Models and Type Definitions for NautilusTrader Historical Backtesting (Stage 143)."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class BacktestRunStatus(str, enum.Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    QUEUED = "QUEUED"
    INITIALIZING = "INITIALIZING"
    LOADING_DATA = "LOADING_DATA"
    RUNNING = "RUNNING"
    ANALYZING = "ANALYZING"
    GENERATING_REPORT = "GENERATING_REPORT"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class FillModelType(str, enum.Enum):
    TOUCHED_BID_ASK = "TOUCHED_BID_ASK"
    CROSS_BID_ASK = "CROSS_BID_ASK"
    VOLUME_CONSTRAINED = "VOLUME_CONSTRAINED"
    PROBABILISTIC = "PROBABILISTIC"


class SlippagePolicy(str, enum.Enum):
    NONE = "NONE"
    FIXED_TICKS = "FIXED_TICKS"
    FIXED_BPS = "FIXED_BPS"
    VOLUME_WEIGHTED = "VOLUME_WEIGHTED"


class FeeModelType(str, enum.Enum):
    ZERO_FEE = "ZERO_FEE"
    PER_SHARE = "PER_SHARE"
    PER_CONTRACT = "PER_CONTRACT"
    MAKER_TAKER = "MAKER_TAKER"
    PERCENTAGE = "PERCENTAGE"


class LatencyModelType(str, enum.Enum):
    ZERO_LATENCY = "ZERO_LATENCY"
    FIXED_MS = "FIXED_MS"
    STOCHASTIC_LOGNORMAL = "STOCHASTIC_LOGNORMAL"


class DataGranularity(str, enum.Enum):
    BARS_1D = "BARS_1D"
    BARS_1H = "BARS_1H"
    BARS_1M = "BARS_1M"
    QUOTE_TICKS = "QUOTE_TICKS"
    TRADE_TICKS = "TRADE_TICKS"
    L2_BOOK = "L2_BOOK"


@dataclass
class HistoricalDatasetManifest:
    """Metadata describing a validated historical market dataset partition."""

    dataset_id: str
    provider_id: str
    symbol: str
    instrument_type: str  # "EQUITY" | "OPTION" | "FX"
    data_granularity: DataGranularity
    start_date: str
    end_date: str
    records_count: int
    has_gaps: bool = False
    gaps_summary: Optional[str] = None
    checksum: str = ""
    license_id: str = "SRC_HISTORICAL_AUTHORIZED"
    currency: str = "USD"
    has_options_quotes: bool = False
    is_delisted_inclusive: bool = True  # Free of survivorship bias


@dataclass
class AtlasBacktestConfig:
    """Canonical run configuration for an event-driven historical backtest."""

    run_id: str
    owner_id: str
    strategy_id: str
    strategy_version: str = "1.0.0"
    strategy_parameters: Dict[str, Any] = field(default_factory=dict)
    instrument_ids: List[str] = field(default_factory=lambda: ["SPY.SIM"])
    dataset_id: str = "ds_spy_daily"
    start_date: str = "2024-01-01"
    end_date: str = "2024-12-31"
    initial_cash: float = 100_000.0
    base_currency: str = "USD"
    account_type: str = "MARGIN"  # "CASH" | "MARGIN"
    fill_model: FillModelType = FillModelType.TOUCHED_BID_ASK
    slippage_policy: SlippagePolicy = SlippagePolicy.NONE
    slippage_value: float = 0.0  # ticks or bps
    fee_model: FeeModelType = FeeModelType.PER_SHARE
    commission_rate: float = 0.005  # $0.005 per share / $0.65 per contract
    latency_model: LatencyModelType = LatencyModelType.ZERO_LATENCY
    latency_ms: float = 0.0
    max_position_size: Optional[float] = None
    max_drawdown_limit_pct: Optional[float] = None
    random_seed: int = 42
    tenant_id: str = "default_tenant"
    is_private: bool = True


@dataclass
class OrderRecord:
    """Traceable record of a simulated order lifecycle event."""

    order_id: str
    run_id: str
    instrument_id: str
    order_side: str  # "BUY" | "SELL"
    order_type: str  # "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT"
    quantity: float
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str = "SUBMITTED"  # "SUBMITTED" | "ACCEPTED" | "FILLED" | "PARTIALLY_FILLED" | "REJECTED" | "CANCELLED"
    rejection_reason: Optional[str] = None
    submitted_at: str = ""
    accepted_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class FillRecord:
    """Simulated execution fill record."""

    fill_id: str
    order_id: str
    instrument_id: str
    order_side: str
    quantity: float
    fill_price: float
    commission: float
    slippage_cost: float
    fill_timestamp: str


@dataclass
class PositionRecord:
    """Simulated portfolio position snapshot."""

    instrument_id: str
    quantity: float
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float


@dataclass
class EquitySnapshot:
    """Time-series point for the portfolio equity curve."""

    timestamp: str
    equity: float
    cash: float
    unrealized_pnl: float
    realized_pnl: float
    drawdown_pct: float
    leverage: float = 0.0


@dataclass
class TradeRecord:
    """Round-trip completed trade analytics."""

    trade_id: str
    instrument_id: str
    direction: str  # "LONG" | "SHORT"
    entry_time: str
    entry_price: float
    exit_time: str
    exit_price: float
    quantity: float
    gross_pnl: float
    commissions: float
    slippage_cost: float
    net_pnl: float
    holding_period_days: float
    exit_reason: str = "STRATEGY_SIGNAL"


@dataclass
class DrawdownMetrics:
    """Maximum and duration drawdown analytics."""

    max_drawdown_dollar: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration_days: float = 0.0
    peak_timestamp: str = ""
    trough_timestamp: str = ""
    recovery_timestamp: Optional[str] = None
    is_recovered: bool = True


@dataclass
class PerformanceMetrics:
    """Rigorous institutional backtest performance metrics."""

    total_return_dollar: float = 0.0
    total_return_pct: float = 0.0
    cagr_pct: float = 0.0
    annualized_volatility_pct: float = 0.0
    sharpe_ratio: Optional[float] = None  # None when zero or undefined variance
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    profit_factor: Optional[float] = None  # None when zero gross losses
    win_rate_pct: float = 0.0
    expectancy_dollar: float = 0.0
    total_trades_count: int = 0
    winning_trades_count: int = 0
    losing_trades_count: int = 0
    avg_winning_trade: float = 0.0
    avg_losing_trade: float = 0.0
    max_consecutive_losses: int = 0
    total_commissions_paid: float = 0.0
    total_slippage_cost: float = 0.0
    turnover_ratio: float = 0.0
    drawdown: DrawdownMetrics = field(default_factory=DrawdownMetrics)


@dataclass
class ReplayEvent:
    """Event representation for step-by-step historical simulation replay."""

    timestamp: str
    event_type: str  # "BAR" | "QUOTE" | "SIGNAL" | "ORDER_SUBMIT" | "ORDER_FILL" | "ORDER_REJECT"
    instrument_id: str
    price: float
    volume: float
    description: str
    portfolio_equity: float
    unrealized_pnl: float


@dataclass
class AtlasStrategyDefinition:
    """Strategy metadata and parameter schema registered in Strategy Registry."""

    strategy_id: str
    version: str
    name: str
    description: str
    supported_instrument_types: List[str]
    required_data_granularity: List[DataGranularity]
    parameter_schema: Dict[str, Any]
    default_parameters: Dict[str, Any]
    is_system_template: bool = True
    owner_id: Optional[str] = None


@dataclass
class ParameterExperimentConfig:
    """Specification for multi-parameter grid search experiments."""

    experiment_id: str
    strategy_id: str
    dataset_id: str
    parameter_grid: Dict[str, List[Any]]
    base_config: AtlasBacktestConfig
    objective_metric: str = "sharpe_ratio"  # "sharpe_ratio" | "total_return_pct" | "profit_factor"
    max_combinations: int = 50


@dataclass
class ParameterExperimentResult:
    """Outcome of a parameter sensitivity experiment."""

    experiment_id: str
    combinations_tested: int
    results_matrix: List[Dict[str, Any]]
    best_parameters: Dict[str, Any]
    best_metric_value: float
    overfitting_warning: bool = False
    warning_memo: Optional[str] = None


@dataclass
class WalkForwardFold:
    """A single chronological train/test fold for walk-forward validation."""

    fold_index: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    selected_parameters: Dict[str, Any]
    in_sample_metric: float
    out_of_sample_metric: float
    out_of_sample_return_pct: float
    out_of_sample_drawdown_pct: float


@dataclass
class WalkForwardResult:
    """Aggregated walk-forward evaluation result."""

    walk_forward_id: str
    strategy_id: str
    folds: List[WalkForwardFold]
    aggregated_out_of_sample_return_pct: float
    efficiency_ratio: float  # OOS metric / IS metric
    robustness_warning: bool = False


@dataclass
class AtlasBacktestResult:
    """Canonical finalized backtest result containing immutable run artifacts."""

    run_id: str
    status: BacktestRunStatus
    config: AtlasBacktestConfig
    dataset_manifest: HistoricalDatasetManifest
    performance: PerformanceMetrics
    equity_curve: List[EquitySnapshot]
    orders: List[OrderRecord]
    fills: List[FillRecord]
    positions: List[PositionRecord]
    trades: List[TradeRecord]
    replay_events: List[ReplayEvent]
    nautilus_version: str = "1.231.0"
    execution_time_seconds: float = 0.0
    quality_warnings: List[str] = field(default_factory=list)
    disclaimers: List[str] = field(default_factory=list)


STAGE_143_DISCLAIMERS = [
    "ATLAS Stage 143 Backtesting Engine simulates historical execution under specified assumptions. Past performance is not indicative of future results.",
    "Simulation models (slippage, latency, fees, matching) reflect analytical approximations and cannot guarantee identical execution in live exchange venues.",
    "In-sample optimized parameters represent historical curve fitting. Out-of-sample and walk-forward verification should always be inspected for overfitting.",
    "Options backtesting requires genuine historical bid/ask quotes and accounts for contract multipliers, expiration dates, and assignment risk.",
    "This system provides quantitative research intelligence only. Automated trade execution, live order routing, and broker integration are strictly prohibited in Stage 143.",
]
