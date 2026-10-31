"""Domain Exceptions for NautilusTrader Historical Backtesting Engine (Stage 143)."""

from __future__ import annotations
from typing import Any, Dict, Optional


class BacktestDomainError(Exception):
    """Base domain exception for ATLAS NautilusTrader backtesting engine."""

    def __init__(
        self,
        message: str,
        code: str = "BACKTEST_DOMAIN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class BacktestEngineError(BacktestDomainError):
    """Raised when an internal NautilusTrader engine execution fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="BACKTEST_ENGINE_ERROR", details=details)


class BacktestDatasetNotFoundError(BacktestDomainError):
    """Raised when a requested historical dataset manifest cannot be found."""

    def __init__(self, dataset_id: str):
        super().__init__(
            f"Historical dataset '{dataset_id}' was not found in the historical catalog.",
            code="BACKTEST_DATASET_NOT_FOUND",
            details={"dataset_id": dataset_id},
        )


class BacktestDatasetIneligibleError(BacktestDomainError):
    """Raised when a dataset fails data quality gates (e.g. gaps, missing quotes)."""

    def __init__(self, dataset_id: str, reason: str, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        d.update({"dataset_id": dataset_id, "reason": reason})
        super().__init__(
            f"Dataset '{dataset_id}' is ineligible for backtest simulation: {reason}",
            code="BACKTEST_DATASET_INELIGIBLE",
            details=d,
        )


class BacktestStrategyNotFoundError(BacktestDomainError):
    """Raised when a strategy definition cannot be found in the Strategy Registry."""

    def __init__(self, strategy_id: str, version: Optional[str] = None):
        super().__init__(
            f"Strategy '{strategy_id}' (version: {version or 'latest'}) was not found in registry.",
            code="BACKTEST_STRATEGY_NOT_FOUND",
            details={"strategy_id": strategy_id, "version": version},
        )


class BacktestInvalidParameterError(BacktestDomainError):
    """Raised when strategy parameters violate validation rules (e.g. fast_ma >= slow_ma)."""

    def __init__(self, parameter_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        d.update({"parameter_name": parameter_name, "reason": reason})
        super().__init__(
            f"Invalid strategy parameter '{parameter_name}': {reason}",
            code="BACKTEST_INVALID_PARAMETER",
            details=d,
        )


class BacktestLookAheadError(BacktestDomainError):
    """Raised when future data leakage or same-bar look-ahead is detected."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Temporal Look-Ahead Violation: {message}",
            code="BACKTEST_LOOK_AHEAD_VIOLATION",
            details=details,
        )


class BacktestResourceQuotaExceededError(BacktestDomainError):
    """Raised when a backtest run or parameter sweep exceeds compute/memory quotas."""

    def __init__(self, resource_type: str, requested: int, maximum: int):
        super().__init__(
            f"Resource quota exceeded for {resource_type}: requested {requested}, maximum permitted is {maximum}.",
            code="BACKTEST_RESOURCE_QUOTA_EXCEEDED",
            details={"resource_type": resource_type, "requested": requested, "maximum": maximum},
        )


class BacktestMultiTenantAccessDeniedError(BacktestDomainError):
    """Raised when a user attempts to access another tenant's private run or strategy."""

    def __init__(self, resource_id: str, principal_sub: str):
        super().__init__(
            f"Access denied: User '{principal_sub}' is not authorized to access backtest resource '{resource_id}'.",
            code="BACKTEST_TENANT_ACCESS_DENIED",
            details={"resource_id": resource_id, "principal_sub": principal_sub},
        )


class BacktestLicenseRevokedError(BacktestDomainError):
    """Raised when a required historical market data license has been revoked."""

    def __init__(self, source_id: str):
        super().__init__(
            f"Access denied: Historical market data source license '{source_id}' is revoked or not entitled.",
            code="BACKTEST_LICENSE_REVOKED",
            details={"source_id": source_id},
        )
