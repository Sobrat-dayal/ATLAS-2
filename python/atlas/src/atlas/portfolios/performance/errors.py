"""Typed domain exceptions for ATLAS Portfolio Performance (Stage 111)."""

from typing import Optional


class PortfolioPerformanceError(Exception):
    """Base exception for portfolio performance domain."""

    def __init__(self, message: str, code: str = "PORTFOLIO_PERFORMANCE_ERROR", status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class PortfolioPerformanceNotFoundError(PortfolioPerformanceError):
    def __init__(self, message: str = "Performance calculation run not found"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_NOT_FOUND", status_code=404)


class PortfolioPerformanceAccessDeniedError(PortfolioPerformanceError):
    def __init__(self, message: str = "Access to portfolio performance denied"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_ACCESS_DENIED", status_code=403)


class PortfolioPerformancePeriodInvalidError(PortfolioPerformanceError):
    def __init__(self, message: str = "Performance calculation period is invalid"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_PERIOD_INVALID", status_code=400)


class PortfolioPerformancePeriodBeforeInceptionError(PortfolioPerformanceError):
    def __init__(self, message: str = "Requested start date is before portfolio funding/inception"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_PERIOD_BEFORE_INCEPTION", status_code=400)


class PortfolioPerformanceMethodUnsupportedError(PortfolioPerformanceError):
    def __init__(self, message: str = "Requested return methodology is unsupported"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_METHOD_UNSUPPORTED", status_code=400)


class PortfolioPerformanceBeginningValuationMissingError(PortfolioPerformanceError):
    def __init__(self, message: str = "Beginning boundary valuation is missing"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_BEGINNING_VALUATION_MISSING", status_code=422)


class PortfolioPerformanceEndingValuationMissingError(PortfolioPerformanceError):
    def __init__(self, message: str = "Ending boundary valuation is missing"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_ENDING_VALUATION_MISSING", status_code=422)


class PortfolioPerformanceFlowBoundaryMissingError(PortfolioPerformanceError):
    def __init__(self, message: str = "Valuation at external cash flow boundary is missing"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_FLOW_BOUNDARY_MISSING", status_code=422)


class PortfolioPerformanceUnclassifiedCashFlowError(PortfolioPerformanceError):
    def __init__(self, message: str = "Transaction could not be classified for cash flow boundary"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_UNCLASSIFIED_CASH_FLOW", status_code=422)


class PortfolioPerformanceCashFlowInvalidError(PortfolioPerformanceError):
    def __init__(self, message: str = "Cash flow schedule is mathematically invalid"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_CASH_FLOW_INVALID", status_code=400)


class PortfolioPerformanceFlowReconciliationFailedError(PortfolioPerformanceError):
    def __init__(self, message: str = "Performance monetary bridge reconciliation failed"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_FLOW_RECONCILIATION_FAILED", status_code=422)


class PortfolioPerformancePriceUnavailableError(PortfolioPerformanceError):
    def __init__(self, message: str = "Canonical market price observation unavailable"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_PRICE_UNAVAILABLE", status_code=422)


class PortfolioPerformanceFxUnavailableError(PortfolioPerformanceError):
    def __init__(self, message: str = "Historical exchange rate observation unavailable"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_FX_UNAVAILABLE", status_code=422)


class PortfolioPerformanceTwrUnavailableError(PortfolioPerformanceError):
    def __init__(self, message: str = "Exact time-weighted return cannot be computed"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_TWR_UNAVAILABLE", status_code=422)


class PortfolioPerformanceMwrUnavailableError(PortfolioPerformanceError):
    def __init__(self, message: str = "Money-weighted return cannot be computed"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_MWR_UNAVAILABLE", status_code=422)


class PortfolioPerformanceXirrError(PortfolioPerformanceError):
    """Base class for XIRR specific numerical errors."""
    def __init__(self, message: str = "XIRR numerical error", code: str = "PORTFOLIO_PERFORMANCE_XIRR_ERROR", status_code: int = 422):
        super().__init__(message, code=code, status_code=status_code)


class PortfolioPerformanceXirrNoSolutionError(PortfolioPerformanceXirrError):
    def __init__(self, message: str = "XIRR solver could not find a valid real solution root"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_XIRR_NO_SOLUTION", status_code=422)


class PortfolioPerformanceXirrMultipleRootsError(PortfolioPerformanceXirrError):
    def __init__(self, message: str = "XIRR cash flow schedule contains multiple sign variations with multiple roots"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_XIRR_MULTIPLE_ROOTS", status_code=422)


class PortfolioPerformanceXirrNonConvergenceError(PortfolioPerformanceXirrError):
    def __init__(self, message: str = "XIRR numerical solver failed to converge within bounded iterations"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_XIRR_NONCONVERGENCE", status_code=422)


class PortfolioPerformanceXirrInvalidCashFlowsError(PortfolioPerformanceXirrError):
    def __init__(self, message: str = "Cash flow sequence must contain both positive and negative flows for XIRR"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_XIRR_INVALID_CASH_FLOWS", status_code=400)



class PortfolioPerformanceAnnualizationInvalidError(PortfolioPerformanceError):
    def __init__(self, message: str = "Period duration is zero or invalid for geometric annualization"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_ANNUALIZATION_INVALID", status_code=400)


class PortfolioPerformanceBenchmarkNotFoundError(PortfolioPerformanceError):
    def __init__(self, message: str = "Canonical benchmark not found"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_BENCHMARK_NOT_FOUND", status_code=404)


class PortfolioPerformanceBenchmarkDataMissingError(PortfolioPerformanceError):
    def __init__(self, message: str = "Benchmark market observations missing for requested period"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_BENCHMARK_DATA_MISSING", status_code=422)


class PortfolioPerformanceBenchmarkBasisMismatchError(PortfolioPerformanceError):
    def __init__(self, message: str = "Benchmark return basis does not match portfolio total return"):
        super().__init__(message, code="PORTFOLIO_PERFORMANCE_BENCHMARK_BASIS_MISMATCH", status_code=400)
