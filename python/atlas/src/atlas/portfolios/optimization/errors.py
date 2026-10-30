"""ATLAS Portfolios V1 — Optimization Errors (Stage 114).

Typed domain exceptions for portfolio optimization, solver execution,
and constraint verification.
"""

from typing import Any, Optional


class PortfolioOptimizationError(Exception):
    """Base exception for all portfolio optimization errors."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_ERROR"

    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class PortfolioOptimizationStudyNotFoundError(PortfolioOptimizationError):
    """Raised when an optimization study is not found."""

    status_code: int = 404
    code: str = "PORTFOLIO_OPTIMIZATION_STUDY_NOT_FOUND"


class PortfolioOptimizationRunNotFoundError(PortfolioOptimizationError):
    """Raised when an optimization run is not found."""

    status_code: int = 404
    code: str = "PORTFOLIO_OPTIMIZATION_RUN_NOT_FOUND"


class PortfolioOptimizationAccessDeniedError(PortfolioOptimizationError):
    """Raised when a user attempts unauthorized access to a study or run."""

    status_code: int = 403
    code: str = "PORTFOLIO_OPTIMIZATION_ACCESS_DENIED"


class PortfolioOptimizationUniverseEmptyError(PortfolioOptimizationError):
    """Raised when the investment universe contains no eligible instruments."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_UNIVERSE_EMPTY"


class PortfolioOptimizationNavInvalidError(PortfolioOptimizationError):
    """Raised when baseline portfolio NAV is non-positive or unavailable."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_NAV_INVALID"


class PortfolioOptimizationHistoricalDataInsufficientError(PortfolioOptimizationError):
    """Raised when return observations are insufficient for covariance estimation."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_HISTORICAL_DATA_INSUFFICIENT"


class PortfolioOptimizationCovarianceNotPsdError(PortfolioOptimizationError):
    """Raised when the covariance matrix fails positive-semidefinite validation."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_COVARIANCE_NOT_PSD"


class PortfolioOptimizationConstraintConflictError(PortfolioOptimizationError):
    """Raised when constraint bounds are contradictory (e.g. min > max or total max < 1.0)."""

    status_code: int = 422
    code: str = "PORTFOLIO_OPTIMIZATION_CONSTRAINT_CONFLICT"


class PortfolioOptimizationInfeasibleError(PortfolioOptimizationError):
    """Raised when the solver determines no mathematically feasible allocation exists."""

    status_code: int = 422
    code: str = "PORTFOLIO_OPTIMIZATION_INFEASIBLE"


class PortfolioOptimizationUnboundedError(PortfolioOptimizationError):
    """Raised when the optimization objective is unbounded under specified constraints."""

    status_code: int = 422
    code: str = "PORTFOLIO_OPTIMIZATION_UNBOUNDED"


class PortfolioOptimizationNumericalFailureError(PortfolioOptimizationError):
    """Raised when the numerical solver encounters ill-conditioning or singularity."""

    status_code: int = 500
    code: str = "PORTFOLIO_OPTIMIZATION_NUMERICAL_FAILURE"


class PortfolioOptimizationSolverTimeoutError(PortfolioOptimizationError):
    """Raised when solver execution exceeds the allocated time limit."""

    status_code: int = 504
    code: str = "PORTFOLIO_OPTIMIZATION_SOLVER_TIMEOUT"


class PortfolioOptimizationRiskFreeRateUnavailableError(PortfolioOptimizationError):
    """Raised when a valid risk-free rate is missing for Sharpe optimization."""

    status_code: int = 400
    code: str = "PORTFOLIO_OPTIMIZATION_RISK_FREE_RATE_UNAVAILABLE"


class PortfolioOptimizationBenchmarkNotFoundError(PortfolioOptimizationError):
    """Raised when a benchmark reference is missing for tracking-error optimization."""

    status_code: int = 404
    code: str = "PORTFOLIO_OPTIMIZATION_BENCHMARK_NOT_FOUND"
