"""Domain errors for ATLAS Options Analytics (Stage 141).

Enforces institutional invariants:
- Typed error conditions
- Strict boundary between Stage 141 analytics and Stage 142 QuantLib pricing
- Prohibits applying single-expiration vanilla payoffs to multi-expiration or adjusted contracts
- Multi-tenant portfolio isolation
- Data source entitlement and quality errors
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class OptionsDomainError(Exception):
    """Base exception for all Options Analytics subsystem operations."""

    def __init__(
        self,
        message: str,
        code: str = "OPTIONS_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class OptionsContractNotFoundError(OptionsDomainError):
    """Raised when an option contract cannot be found in the contract master."""

    def __init__(self, contract_id: str):
        super().__init__(
            f"Option contract '{contract_id}' not found in canonical security master.",
            code="OPTIONS_CONTRACT_NOT_FOUND",
            details={"contract_id": contract_id},
        )
        self.contract_id = contract_id


class OptionsUnderlyingNotFoundError(OptionsDomainError):
    """Raised when an underlying asset has no listed or supported options."""

    def __init__(self, underlying_id: str):
        super().__init__(
            f"Underlying instrument '{underlying_id}' not found or has no listed options coverage.",
            code="OPTIONS_UNDERLYING_NOT_FOUND",
            details={"underlying_id": underlying_id},
        )
        self.underlying_id = underlying_id


class OptionsTenantAccessDeniedError(OptionsDomainError):
    """Raised when a principal attempts to access private options positions belonging to another tenant/user."""

    def __init__(
        self,
        portfolio_id: str,
        user_id: Optional[str] = None,
        message: str = "Access to private options portfolio is denied.",
    ):
        super().__init__(
            message,
            code="OPTIONS_TENANT_ACCESS_DENIED",
            details={"portfolio_id": portfolio_id, "user_id": user_id},
        )


class OptionsEntitlementRequiredError(OptionsDomainError):
    """Raised when real-time quotes or proprietary options data requires an ungranted license."""

    def __init__(self, source_id: str, message: str = "Active market data entitlement required."):
        super().__init__(
            message,
            code="OPTIONS_ENTITLEMENT_REQUIRED",
            details={"source_id": source_id},
        )
        self.source_id = source_id


class OptionsSourceUnavailableError(OptionsDomainError):
    """Raised when an upstream options data provider is offline or unreachable."""

    def __init__(self, source_id: str, message: str = "Options market data source is unavailable."):
        super().__init__(
            message,
            code="OPTIONS_SOURCE_UNAVAILABLE",
            details={"source_id": source_id},
        )
        self.source_id = source_id


class OptionsAdjustedDeliverableUnsupportedError(OptionsDomainError):
    """Raised when attempting to apply standard 100-share expiration payoff formulas to nonstandard adjusted contracts."""

    def __init__(
        self,
        contract_id: str,
        deliverable_summary: str,
        message: str = "Standard vanilla expiration payoff calculation is unsupported for nonstandard adjusted contracts.",
    ):
        super().__init__(
            message,
            code="OPTIONS_ADJUSTED_DELIVERABLE_UNSUPPORTED",
            details={"contract_id": contract_id, "deliverable_summary": deliverable_summary},
        )


class OptionsMultiExpirationPayoffUnsupportedError(OptionsDomainError):
    """Raised when attempting to calculate a single-expiration payoff curve for multi-expiration strategies."""

    def __init__(
        self,
        expirations: list[str],
        message: str = "Single-expiration payoff calculation is invalid for multi-expiration strategies (calendar/diagonal spreads). Mark-to-market valuation is reserved for Stage 142.",
    ):
        super().__init__(
            message,
            code="OPTIONS_MULTI_EXPIRATION_UNSUPPORTED",
            details={"expirations": expirations},
        )


class OptionsInvalidStrategyLegError(OptionsDomainError):
    """Raised when a strategy leg contains invalid quantities, prices, or incompatible underlyings."""

    def __init__(self, leg_index: int, reason: str):
        super().__init__(
            f"Strategy leg {leg_index} is invalid: {reason}",
            code="OPTIONS_INVALID_STRATEGY_LEG",
            details={"leg_index": leg_index, "reason": reason},
        )


class OptionsDataQualityError(OptionsDomainError):
    """Raised when an option quote violates market sanity checks (crossed market, negative prices)."""

    def __init__(self, contract_id: str, reason: str):
        super().__init__(
            f"Option quote quality check failed for '{contract_id}': {reason}",
            code="OPTIONS_DATA_QUALITY_ERROR",
            details={"contract_id": contract_id, "reason": reason},
        )

