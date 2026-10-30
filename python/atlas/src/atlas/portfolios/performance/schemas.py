"""Pydantic V2 Schemas for ATLAS Portfolio Performance (Stage 111)."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.portfolios.performance.enums import (
    BenchmarkReturnBasis,
    DataCompletenessStatus,
    MeasurementScope,
    PerformanceMethodology,
    PerformancePeriodType,
    PerformanceStatus,
)


class SubperiodReturnDTO(BaseModel):
    subperiod_index: int
    start_time: datetime
    end_time: datetime
    start_value: str
    end_value_pre_flow: str
    net_external_flow: str
    end_value_post_flow: str
    subperiod_return: str
    cumulative_twr_linked: str


class PerformanceCashFlowDTO(BaseModel):
    id: str
    flow_date: datetime
    classification: str
    native_amount: str
    native_currency: str
    base_amount: str
    base_currency: str
    fx_rate: str
    investor_flow_amount: str
    portfolio_flow_amount: str
    description: str


class PeriodicReturnDTO(BaseModel):
    period_label: str
    period_type: str
    start_date: datetime
    end_date: datetime
    return_value: Optional[str] = None
    beginning_value: str
    ending_value: str
    net_external_flows: str
    investment_gain: str
    is_partial: bool
    completeness: str


class BenchmarkDefinitionDTO(BaseModel):
    benchmark_id: str
    name: str
    symbol: str
    benchmark_type: str
    return_basis: str
    currency: str
    description: str


class BenchmarkComparisonDTO(BaseModel):
    benchmark_id: str
    benchmark_name: str
    return_basis: str
    currency: str
    portfolio_return: str
    benchmark_return: str
    arithmetic_difference: str
    period_start: datetime
    period_end: datetime
    rebased_portfolio_index_end: str
    rebased_benchmark_index_end: str
    warning: Optional[str] = None


class PerformanceDataQualityDTO(BaseModel):
    completeness: str
    missing_valuations: int = 0
    missing_market_prices: int = 0
    missing_fx_rates: int = 0
    stale_market_prices: int = 0
    warnings: List[str] = Field(default_factory=list)
    source_manifest: Dict[str, Any] = Field(default_factory=dict)


class PerformanceCalculateRequest(BaseModel):
    portfolio_id: str
    account_id: Optional[str] = None
    period_type: PerformancePeriodType = PerformancePeriodType.YEAR_TO_DATE
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    methodology: PerformanceMethodology = PerformanceMethodology.TIME_WEIGHTED_RETURN
    reporting_currency: Optional[str] = None
    benchmark_id: Optional[str] = None
    idempotency_key: Optional[str] = None


class PerformanceResponse(BaseModel):
    run_id: str
    portfolio_id: str
    account_id: Optional[str] = None
    methodology: str
    period_type: str
    scope: str
    period_start: datetime
    period_end: datetime
    base_currency: str
    status: str
    twr_cumulative: Optional[str] = None
    twr_annualized: Optional[str] = None
    mwr_xirr: Optional[str] = None
    beginning_value: str
    ending_value: str
    net_external_flows: str
    total_contributions: str
    total_withdrawals: str
    total_dividends: str
    total_fees: str
    investment_gain: str
    subperiods: List[SubperiodReturnDTO] = Field(default_factory=list)
    dated_flows: List[PerformanceCashFlowDTO] = Field(default_factory=list)
    benchmark_comparison: Optional[BenchmarkComparisonDTO] = None
    data_quality: PerformanceDataQualityDTO
    calculation_version: str = "1.0.0"
    input_hash: str = ""
    created_at: datetime
    completed_at: Optional[datetime] = None


class PerformanceSeriesPointDTO(BaseModel):
    timestamp: datetime
    portfolio_value: str
    indexed_twr: str
    benchmark_indexed: Optional[str] = None
    cash_flow_amount: Optional[str] = None
    cash_flow_type: Optional[str] = None


class PerformanceSeriesResponse(BaseModel):
    portfolio_id: str
    base_currency: str
    period_start: datetime
    period_end: datetime
    points: List[PerformanceSeriesPointDTO]


class PeriodicReturnsResponse(BaseModel):
    portfolio_id: str
    base_currency: str
    returns: List[PeriodicReturnDTO]


class BenchmarkListResponse(BaseModel):
    benchmarks: List[BenchmarkDefinitionDTO]
    total: int


class PerformanceRunListResponse(BaseModel):
    runs: List[PerformanceResponse]
    total: int

