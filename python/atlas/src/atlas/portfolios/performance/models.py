"""Domain models for ATLAS Portfolio Performance (Stage 111)."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from atlas.portfolios.performance.enums import (
    BenchmarkReturnBasis,
    CashFlowClassification,
    DataCompletenessStatus,
    FeeTreatmentPolicy,
    IncomeTreatmentPolicy,
    MeasurementScope,
    PerformanceMethodology,
    PerformancePeriodType,
    PerformanceStatus,
)


@dataclass
class PerformanceCashFlow:
    """Classified cash movement relative to the measured portfolio/account boundary."""
    id: str
    portfolio_id: str
    account_id: Optional[str]
    source_transaction_id: Optional[str]
    classification: CashFlowClassification
    flow_date: datetime
    native_amount: Decimal
    native_currency: str
    base_amount: Decimal
    base_currency: str
    fx_rate: Decimal
    investor_flow_amount: Decimal  # Investor perspective: negative for contribution, positive for withdrawal
    portfolio_flow_amount: Decimal  # Portfolio perspective: positive for contribution, negative for withdrawal
    description: str


@dataclass
class ValuationPoint:
    """Historical portfolio valuation mark."""
    timestamp: datetime
    portfolio_value: Decimal
    cash_value: Decimal
    positions_value: Decimal
    currency: str
    data_completeness: DataCompletenessStatus
    is_stale: bool = False


@dataclass
class SubperiodReturn:
    """Discrete subperiod bounded by external cash flows for exact TWR."""
    subperiod_index: int
    start_time: datetime
    end_time: datetime
    start_value: Decimal
    end_value_pre_flow: Decimal
    net_external_flow: Decimal
    end_value_post_flow: Decimal
    subperiod_return: Decimal
    cumulative_twr_linked: Decimal


@dataclass
class PeriodicReturn:
    """Periodic performance measurement for tables and calendar analytics."""
    period_label: str
    period_type: str  # "DAILY", "MONTHLY", "QUARTERLY", "ANNUAL", "YTD", "TRAILING"
    start_date: datetime
    end_date: datetime
    return_value: Optional[Decimal]
    beginning_value: Decimal
    ending_value: Decimal
    net_external_flows: Decimal
    investment_gain: Decimal
    is_partial: bool
    completeness: DataCompletenessStatus


@dataclass
class BenchmarkDefinition:
    """Canonical market index benchmark metadata."""
    benchmark_id: str
    name: str
    symbol: str
    benchmark_type: str
    return_basis: BenchmarkReturnBasis
    currency: str
    description: str


@dataclass
class BenchmarkComparison:
    """Comparison of portfolio return against a canonical market benchmark."""
    benchmark_id: str
    benchmark_name: str
    return_basis: BenchmarkReturnBasis
    currency: str
    portfolio_return: Decimal
    benchmark_return: Decimal
    arithmetic_difference: Decimal
    period_start: datetime
    period_end: datetime
    rebased_portfolio_index_start: Decimal
    rebased_portfolio_index_end: Decimal
    rebased_benchmark_index_start: Decimal
    rebased_benchmark_index_end: Decimal
    warning: Optional[str] = None


@dataclass
class PerformanceDataQuality:
    """Audit of input completeness and quote freshness for a calculation."""
    completeness: DataCompletenessStatus
    missing_valuations: int = 0
    missing_market_prices: int = 0
    missing_fx_rates: int = 0
    stale_market_prices: int = 0
    warnings: List[str] = field(default_factory=list)
    source_manifest: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceRun:
    """Immutable, versioned record of a portfolio performance calculation."""
    run_id: str
    portfolio_id: str
    account_id: Optional[str]
    owner_user_id: str
    methodology: PerformanceMethodology
    period_type: PerformancePeriodType
    scope: MeasurementScope
    period_start: datetime
    period_end: datetime
    base_currency: str
    status: PerformanceStatus
    twr_cumulative: Optional[Decimal]
    twr_annualized: Optional[Decimal]
    mwr_xirr: Optional[Decimal]
    beginning_value: Decimal
    ending_value: Decimal
    net_external_flows: Decimal
    total_contributions: Decimal
    total_withdrawals: Decimal
    total_dividends: Decimal
    total_fees: Decimal
    investment_gain: Decimal
    data_quality: PerformanceDataQuality
    subperiods: List[SubperiodReturn] = field(default_factory=list)
    dated_flows: List[PerformanceCashFlow] = field(default_factory=list)
    benchmark_comparison: Optional[BenchmarkComparison] = None
    calculation_version: str = "1.0.0"
    input_hash: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
