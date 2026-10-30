"""ATLAS Portfolios V1 — Optimization Domain Models (Stage 114).

Dataclasses for studies, runs, model estimates, constraints, solver results,
and hypothetical candidate allocations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from atlas.portfolios.optimization.enums import (
    ConstraintType,
    CovarianceModel,
    ExpectedReturnModel,
    FeasibilityStatus,
    OptimizationObjective,
    SolverStatus,
    StudyStatus,
)


@dataclass
class OptimizationConstraintItem:
    """Individual constraint applied to portfolio optimization."""

    constraint_id: str
    constraint_type: ConstraintType
    scope: str = "GLOBAL"  # GLOBAL, SECURITY, SECTOR, ASSET_CLASS, CASH, etc.
    target_id: Optional[str] = None  # e.g. "AAPL", "information_technology", "USD"
    lower_bound: Optional[Decimal] = None
    upper_bound: Optional[Decimal] = None
    is_hard: bool = True
    penalty_weight: Decimal = Decimal("1.0")


@dataclass
class ExpectedReturnEstimate:
    """Model estimates of expected annualized returns per eligible asset."""

    model: ExpectedReturnModel
    symbols: List[str]
    estimates: Dict[str, Decimal]  # symbol -> expected return
    horizon_days: int = 365
    annualization_factor: Decimal = Decimal("252.0")
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CovarianceEstimate:
    """Model estimate of the annualized asset return covariance matrix."""

    model: CovarianceModel
    symbols: List[str]
    matrix: List[List[float]]  # n x n covariance matrix
    is_psd: bool = True
    condition_number: float = 1.0
    regularization_applied: bool = False
    eigenvalues: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SolverDiagnostics:
    """Detailed numerical solver performance and convergence diagnostics."""

    solver_name: str
    solver_version: str
    problem_type: str
    status: SolverStatus
    iterations: int = 0
    objective_value: Optional[float] = None
    solve_time_ms: float = 0.0
    max_constraint_violation: float = 0.0
    active_constraints: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CandidatePortfolio:
    """Hypothetical optimized candidate asset allocation."""

    weights: Dict[str, Decimal]  # symbol -> candidate weight
    cash_weight: Decimal
    estimated_return: Decimal
    estimated_variance: Decimal
    estimated_volatility: Decimal
    estimated_sharpe: Optional[Decimal] = None
    estimated_turnover: Decimal = Decimal("0.0")
    estimated_cost: Decimal = Decimal("0.0")
    feasibility_status: FeasibilityStatus = FeasibilityStatus.FEASIBLE
    constraint_slacks: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class EfficientFrontierPoint:
    """Single discrete point along the solved efficient frontier."""

    target_return: Decimal
    candidate_weights: Dict[str, Decimal]
    estimated_return: Decimal
    estimated_volatility: Decimal
    estimated_sharpe: Optional[Decimal] = None
    solver_status: SolverStatus = SolverStatus.OPTIMAL
    is_dominated: bool = False


@dataclass
class CurrentVsCandidateItem:
    """Comparative line-item for current holdings vs hypothetical candidate."""

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
    trade_direction: str  # "BUY", "SELL", "HOLD"
    estimated_cost: Decimal = Decimal("0.00")


@dataclass
class SensitivityScenarioResult:
    """Comparative outcome for an assumption sensitivity scenario."""

    scenario_name: str
    parameter_name: str
    parameter_value: str
    estimated_return: Decimal
    estimated_volatility: Decimal
    estimated_turnover: Decimal
    candidate_weights: Dict[str, Decimal]


@dataclass
class OptimizationStudy:
    """Persistent optimization analytical study container."""

    study_id: str
    portfolio_id: str
    owner_user_id: str
    name: str
    description: str = ""
    status: StudyStatus = StudyStatus.ACTIVE
    default_objective: OptimizationObjective = OptimizationObjective.MINIMUM_VARIANCE
    universe_symbols: List[str] = field(default_factory=list)
    base_currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    revision: int = 1


@dataclass
class PortfolioOptimizationRun:
    """Immutable record of an executed portfolio optimization calculation."""

    run_id: str
    study_id: Optional[str]
    portfolio_id: str
    owner_user_id: str
    objective_type: OptimizationObjective
    base_currency: str
    universe_symbols: List[str]
    baseline_nav: Decimal
    baseline_weights: Dict[str, Decimal]
    expected_returns: ExpectedReturnEstimate
    covariance: CovarianceEstimate
    constraints: List[OptimizationConstraintItem]
    candidate: CandidatePortfolio
    frontier_points: List[EfficientFrontierPoint] = field(default_factory=list)
    comparisons: List[CurrentVsCandidateItem] = field(default_factory=list)
    diagnostics: SolverDiagnostics = field(default_factory=lambda: SolverDiagnostics(
        solver_name="scipy.optimize",
        solver_version="1.18.1",
        problem_type="Convex Quadratic Programming (QP)",
        status=SolverStatus.OPTIMAL,
    ))
    sensitivity_results: List[SensitivityScenarioResult] = field(default_factory=list)
    input_hash: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
