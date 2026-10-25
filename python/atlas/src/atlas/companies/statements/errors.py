"""Errors for Company Financial Statements (Stage 82)."""

from atlas.core.exceptions import AtlasError


class StatementError(AtlasError):
    """Base exception for statement domain errors."""

    def __init__(self, message: str, code: str = "STATEMENT_ERROR", status_code: int = 400):
        super().__init__(message, code=code, status_code=status_code)


class StatementNotFoundError(StatementError):
    def __init__(self, statement_type: str, company_id: str):
        super().__init__(
            f"Financial statement '{statement_type}' not found for company {company_id}",
            code="STATEMENT_NOT_FOUND",
            status_code=404,
        )


class PeriodNotAvailableError(StatementError):
    def __init__(self, period_id: str):
        super().__init__(
            f"Financial statement period '{period_id}' is not available",
            code="PERIOD_NOT_AVAILABLE",
            status_code=404,
        )


class ReportingScopeNotAvailableError(StatementError):
    def __init__(self, scope: str):
        super().__init__(
            f"Reporting scope '{scope}' is not available for this entity",
            code="REPORTING_SCOPE_NOT_AVAILABLE",
            status_code=404,
        )


class TTMInsufficientPeriodsError(StatementError):
    def __init__(self, message: str = "Insufficient compatible quarterly periods to derive TTM flow metric."):
        super().__init__(
            message,
            code="TTM_INSUFFICIENT_PERIODS",
            status_code=400,
        )


class InvalidStatementQueryError(StatementError):
    def __init__(self, message: str):
        super().__init__(
            message,
            code="INVALID_STATEMENT_QUERY",
            status_code=400,
        )
