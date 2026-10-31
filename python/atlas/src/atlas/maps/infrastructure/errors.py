"""Domain and operational exceptions for ATLAS Physical Infrastructure Intelligence (Stage 133)."""

from __future__ import annotations


class InfrastructureDomainError(Exception):
    """Base exception for all infrastructure domain errors."""

    def __init__(self, message: str, code: str = "INFRASTRUCTURE_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class AssetNotFoundError(InfrastructureDomainError):
    """Raised when an infrastructure asset cannot be found."""

    def __init__(self, asset_id: str) -> None:
        super().__init__(f"Infrastructure asset '{asset_id}' not found.", code="ASSET_NOT_FOUND")
        self.asset_id = asset_id


class NetworkNotFoundError(InfrastructureDomainError):
    """Raised when an infrastructure network cannot be found."""

    def __init__(self, network_id: str) -> None:
        super().__init__(f"Infrastructure network '{network_id}' not found.", code="NETWORK_NOT_FOUND")
        self.network_id = network_id


class IncompatibleCapacityUnitError(InfrastructureDomainError):
    """Raised when attempting to add or compare incompatible dimensional capacity units."""

    def __init__(self, unit_a: str, unit_b: str, reason: str = "") -> None:
        detail = f" Cannot combine {unit_a} and {unit_b}."
        if reason:
            detail += f" ({reason})"
        super().__init__(
            f"Incompatible capacity units:{detail}",
            code="INCOMPATIBLE_CAPACITY_UNITS",
        )
        self.unit_a = unit_a
        self.unit_b = unit_b


class InvalidTopologyError(InfrastructureDomainError):
    """Raised when network topology is invalid (missing nodes, malformed edges, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_TOPOLOGY")


class TraversalDepthExceededError(InfrastructureDomainError):
    """Raised when graph query exceeds maximum allowable traversal depth."""

    def __init__(self, depth: int, max_depth: int = 5) -> None:
        super().__init__(
            f"Traversal depth {depth} exceeds maximum authorized depth {max_depth}.",
            code="TRAVERSAL_DEPTH_EXCEEDED",
        )
        self.depth = depth
        self.max_depth = max_depth


class CycleDetectedInNetworkError(InfrastructureDomainError):
    """Raised when an illegal cycle is encountered during bounded network traversal."""

    def __init__(self, cycle_path: list[str]) -> None:
        super().__init__(
            f"Cycle detected in network traversal along path: {' -> '.join(cycle_path)}",
            code="CYCLE_DETECTED",
        )
        self.cycle_path = cycle_path


class InvalidHistoricalAsOfError(InfrastructureDomainError):
    """Raised when an as-of query specifies an invalid or future date."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="INVALID_HISTORICAL_AS_OF")


class SensitiveAssetAccessDeniedError(InfrastructureDomainError):
    """Raised when access to private or critical infrastructure is unauthorized."""

    def __init__(self, asset_id: str, tenant_id: str | None = None) -> None:
        super().__init__(
            f"Access denied to sensitive or private infrastructure asset '{asset_id}'.",
            code="SENSITIVE_ASSET_ACCESS_DENIED",
        )
        self.asset_id = asset_id
        self.tenant_id = tenant_id


class CommercialUseProhibitedError(InfrastructureDomainError):
    """Raised when attempting commercial usage of a non-commercial dataset."""

    def __init__(self, source_id: str) -> None:
        super().__init__(
            f"Dataset '{source_id}' is restricted to non-commercial usage. Commercial publication prohibited.",
            code="COMMERCIAL_USE_PROHIBITED",
        )
        self.source_id = source_id


class EntitlementRevokedError(InfrastructureDomainError):
    """Raised when an entitlement for a source dataset has been revoked."""

    def __init__(self, source_id: str) -> None:
        super().__init__(
            f"Entitlement for dataset '{source_id}' has been revoked. Derived assets and aggregates are inaccessible.",
            code="ENTITLEMENT_REVOKED",
        )
        self.source_id = source_id


class InvalidPrecisionClassError(InfrastructureDomainError):
    """Raised when geographic precision class is unrecognized."""

    def __init__(self, precision: str) -> None:
        super().__init__(f"Invalid geographic precision class '{precision}'.", code="INVALID_PRECISION_CLASS")
        self.precision = precision

