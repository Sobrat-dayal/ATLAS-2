"""Domain Exceptions for QuantLib Options Strategy Engine (Stage 142)."""

from __future__ import annotations
from typing import Any, Dict, Optional


class QuantDomainError(Exception):
    """Base domain exception for ATLAS QuantLib derivatives engine."""

    def __init__(
        self,
        message: str,
        code: str = "QUANT_DOMAIN_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class QuantLibError(QuantDomainError):
    """Raised when an internal QuantLib computation fails or encounters an unhandled exception."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="QUANTLIB_INTERNAL_ERROR", details=details)


class QuantModelIncompatibleError(QuantDomainError):
    """Raised when the selected pricing model is incompatible with the contract's exercise style or deliverable."""

    def __init__(self, model_id: str, reason: str, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        d.update({"model_id": model_id, "reason": reason})
        super().__init__(
            f"Pricing model '{model_id}' is incompatible: {reason}",
            code="QUANT_MODEL_INCOMPATIBLE",
            details=d,
        )


class QuantContractNotFoundError(QuantDomainError):
    """Raised when an option contract ID cannot be resolved in the canonical registry."""

    def __init__(self, contract_id: str):
        super().__init__(
            f"Option contract '{contract_id}' was not found in the canonical options registry.",
            code="QUANT_CONTRACT_NOT_FOUND",
            details={"contract_id": contract_id},
        )


class QuantEvaluationDateError(QuantDomainError):
    """Raised when an evaluation date is invalid (e.g. after contract expiration or negative maturity)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="QUANT_EVALUATION_DATE_ERROR", details=details)


class QuantNumericalConvergenceError(QuantDomainError):
    """Raised when a numerical method (finite difference, binomial tree, calibration) fails to converge."""

    def __init__(self, method_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        d = details or {}
        d.update({"method_name": method_name, "reason": reason})
        super().__init__(
            f"Numerical method '{method_name}' failed to converge: {reason}",
            code="QUANT_NUMERICAL_CONVERGENCE_ERROR",
            details=d,
        )


class QuantStaleQuoteError(QuantDomainError):
    """Raised when an option quote or underlying price exceeds the staleness threshold under strict policy."""

    def __init__(self, contract_id: str, age_seconds: float, threshold_seconds: float):
        super().__init__(
            f"Quote for contract '{contract_id}' is stale ({age_seconds:.0f}s > threshold {threshold_seconds:.0f}s).",
            code="QUANT_STALE_QUOTE_ERROR",
            details={
                "contract_id": contract_id,
                "age_seconds": age_seconds,
                "threshold_seconds": threshold_seconds,
            },
        )


class QuantInvalidVolatilitySurfaceError(QuantDomainError):
    """Raised when volatility inputs contain arbitrage violations, negative bids, or insufficient points."""

    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Implied volatility surface construction failed: {reason}",
            code="QUANT_INVALID_VOL_SURFACE",
            details=details,
        )


class QuantMultiTenantAccessDeniedError(QuantDomainError):
    """Raised when a user attempts to access another tenant's private saved strategy or position."""

    def __init__(self, resource_id: str, principal_sub: str):
        super().__init__(
            f"Access denied: User '{principal_sub}' is not authorized to access strategy '{resource_id}'.",
            code="QUANT_TENANT_ACCESS_DENIED",
            details={"resource_id": resource_id, "principal_sub": principal_sub},
        )


class QuantEntitlementRequiredError(QuantDomainError):
    """Raised when a required market data source license is missing or revoked."""

    def __init__(self, source_id: str):
        super().__init__(
            f"Market data license for source '{source_id}' is required or has been revoked.",
            code="QUANT_ENTITLEMENT_REQUIRED",
            details={"source_id": source_id},
        )


class QuantResourceQuotaExceededError(QuantDomainError):
    """Raised when computation bounds (number of legs, grid size, scenario steps) exceed safety limits."""

    def __init__(self, resource_type: str, requested: int, maximum: int):
        super().__init__(
            f"Resource quota exceeded for {resource_type}: requested {requested}, maximum permitted is {maximum}.",
            code="QUANT_RESOURCE_QUOTA_EXCEEDED",
            details={"resource_type": resource_type, "requested": requested, "maximum": maximum},
        )
