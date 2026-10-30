"""ATLAS Portfolios V1 — Optimization Pydantic V2 Schemas (Stage 114).

Request and response contracts for studies, runs, frontier points,
candidate allocations, and solver diagnostics.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from atlas.portfolios.optimization.enums import (
    ConstraintType,
    CovarianceModel,
    ExpectedReturnModel,
    FeasibilityStatus,
    OptimizationObjective,
    SolverStatus,
    StudyStatus,
)


class OptimizationConstraintRequest(BaseModel):
    """Request payload for specifying a portfolio optimization constraint."""

    constraint_id: Optional[str] = None
    constraint_type: ConstraintType
    scope: str = "GLOBAL"
    target_id: Optional[str] = None
    lower_bound: Optional[Decimal] = None
    upper_bound: Optional[Decimal] = None
    is_hard: bool = True
    penalty_weight: Decimal = Decimal("1.0")


class OptimizationConstraintResponse(BaseModel):
    """Response payload representing an applied constraint."""

    constraint_id: str
    constraint_type: ConstraintType
    scope: str
    target_id: Optional[str] = None
    lower_bound: Optional[Decimal] = None
    upper_bound: Optional[Decimal] = None
    is_hard: bool
    penalty_weight: Decimal


class CreateOptimizationStudyRequest(BaseModel):
    """Request payload for creating a persistent optimization study."""

    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    default_objective: OptimizationObjective = OptimizationObjective.MINIMUM_VARIANCE
    universe_symbols: Optional[List[str]] = None


class OptimizationStudyResponse(BaseModel):
    """Response payload for an optimization study."""

    study_id: str
    portfolio_id: str
    name: str
    description: str
    status: StudyStatus
    default_objective: OptimizationObjective
    universe_symbols: List[str]
    base_currency: str
    created_at: datetime
    updated_at: datetime


class OptimizationStudiesListResponse(BaseModel):
    """List response for optimization studies."""

    items: List[OptimizationStudyResponse]
    total: int


class ExecuteOptimizationRequest(BaseModel):
    """Request payload for executing portfolio optimization."""

    study_id: Optional[str] = None
    objective_type: OptimizationObjective = OptimizationObjective.MINIMUM_VARIANCE
    universe_symbols: Optional[List[str]] = None
    expected_return_model: ExpectedReturnModel = ExpectedReturnModel.HISTORICAL_ARITHMETIC_MEAN
    covariance_model: CovarianceModel = CovarianceModel.SAMPLE_COVARIANCE
    user_return_assumptions: Optional[Dict[str, Decimal]] = None
    constraints: Optional[List[OptimizationConstraintRequest]] = None
    risk_aversion: float = 2.0
    risk_free_rate: float = 0.045
    target_return: Optional[float] = None
    max_turnover: Optional[float] = None
    proportional_cost_rate: Decimal = Decimal("0.0010")
    is_long_only: bool = True


class ExpectedReturnEstimateResponse(BaseModel):
    """Response for expected asset returns."""

    model: ExpectedReturnModel
    symbols: List[str]
    estimates: Dict[str, Decimal]
    annualization_factor: Decimal


class CovarianceEstimateResponse(BaseModel):
    """Response for estimated covariance matrix."""

    model: CovarianceModel
    symbols: List[str]
    matrix: List[List[float]]
    is_psd: bool
    condition_number: float
    regularization_applied: bool


class SolverDiagnosticsResponse(BaseModel):
    """Response for solver convergence diagnostics."""

    solver_name: str
    solver_version: str
    problem_type: str
    status: SolverStatus
    iterations: int
    objective_value: Optional[float] = None
    solve_time_ms: float
    max_constraint_violation: float
    active_constraints: List[str]
    warnings: List[str]


class CandidatePortfolioResponse(BaseModel):
    """Response for hypothetical candidate allocation."""

    weights: Dict[str, Decimal]
    cash_weight: Decimal
    estimated_return: Decimal
    estimated_variance: Decimal
    estimated_volatility: Decimal
    estimated_sharpe: Optional[Decimal] = None
    estimated_turnover: Decimal
    estimated_cost: Decimal
    feasibility_status: FeasibilityStatus
    constraint_slacks: Dict[str, Decimal]


class EfficientFrontierPointResponse(BaseModel):
    """Single point on the efficient frontier."""

    target_return: Decimal
    candidate_weights: Dict[str, Decimal]
    estimated_return: Decimal
    estimated_volatility: Decimal
    estimated_sharpe: Optional[Decimal] = None
    solver_status: SolverStatus
    is_dominated: bool


class CurrentVsCandidateItemResponse(BaseModel):
    """Comparison row between current holdings and candidate weights."""

    symbol: str
    name: str
    category_id: str
    category_label: str
    current_weight: Decimal
    candidate_weight: Decimal
    weight_delta: Decimal
    current_value: Decimal
    candidate_value: Decimal
    trade_value_delta: Decimal
    trade_direction: str
    estimated_cost: Decimal


class SensitivityScenarioResponse(BaseModel):
    """Single sensitivity scenario outcome."""

    scenario_name: str
    parameter_name: str
    parameter_value: str
    estimated_return: Decimal
    estimated_volatility: Decimal
    estimated_turnover: Decimal
    candidate_weights: Dict[str, Decimal]


class PortfolioOptimizationRunResponse(BaseModel):
    """Full optimization run result response."""

    run_id: str
    study_id: Optional[str] = None
    portfolio_id: str
    objective_type: OptimizationObjective
    base_currency: str
    universe_symbols: List[str]
    baseline_nav: Decimal
    baseline_weights: Dict[str, Decimal]
    expected_returns: ExpectedReturnEstimateResponse
    covariance: CovarianceEstimateResponse
    constraints: List[OptimizationConstraintResponse]
    candidate: CandidatePortfolioResponse
    frontier_points: List[EfficientFrontierPointResponse]
    comparisons: List[CurrentVsCandidateItemResponse]
    diagnostics: SolverDiagnosticsResponse
    sensitivity_results: List[SensitivityScenarioResponse]
    input_hash: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class OptimizationRunsListResponse(BaseModel):
    """List response for historical optimization runs."""

    items: List[PortfolioOptimizationRunResponse]
    total: int
