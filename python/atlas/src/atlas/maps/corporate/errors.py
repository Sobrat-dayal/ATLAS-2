"""Typed error hierarchy for ATLAS Corporate Geography and Facility Mapping (Stage 132)."""

from __future__ import annotations


class CorporateGeoError(Exception):
    """Base exception for all corporate geographic intelligence operations."""

    def __init__(self, message: str, error_code: str = "CORPORATE_GEO_ERROR", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class CompanyNotFoundError(CorporateGeoError):
    """Raised when a company or legal entity cannot be resolved."""

    def __init__(self, company_id: str) -> None:
        super().__init__(
            f"Company or legal entity not found: {company_id}",
            error_code="COMPANY_NOT_FOUND",
            details={"company_id": company_id},
        )


class FacilityNotFoundError(CorporateGeoError):
    """Raised when a corporate facility record is not found."""

    def __init__(self, facility_id: str) -> None:
        super().__init__(
            f"Corporate facility not found: {facility_id}",
            error_code="FACILITY_NOT_FOUND",
            details={"facility_id": facility_id},
        )


class FacilityAccessDeniedError(CorporateGeoError):
    """Raised when a tenant or user lacks permission to access a private facility record."""

    def __init__(self, facility_id: str, tenant_id: str | None = None) -> None:
        super().__init__(
            f"Access denied to facility {facility_id}",
            error_code="FACILITY_ACCESS_DENIED",
            details={"facility_id": facility_id, "tenant_id": tenant_id},
        )


class SourceEntitlementRevokedError(CorporateGeoError):
    """Raised when access to an underlying source document or provider license has been revoked."""

    def __init__(self, source_manifest_id: str) -> None:
        super().__init__(
            f"Source entitlement revoked or expired for manifest: {source_manifest_id}",
            error_code="SOURCE_ENTITLEMENT_REVOKED",
            details={"source_manifest_id": source_manifest_id},
        )


class InvalidFacilityGeometryError(CorporateGeoError):
    """Raised when coordinates or polygon geometry fail WGS84 standards or SRID checks."""

    def __init__(self, reason: str, coordinates: object = None) -> None:
        super().__init__(
            f"Invalid facility geometry: {reason}",
            error_code="INVALID_FACILITY_GEOMETRY",
            details={"reason": reason, "coordinates": str(coordinates)},
        )


class InvalidPrecisionClassError(CorporateGeoError):
    """Raised when precision classification is violated or inappropriately elevated."""

    def __init__(self, precision_class: str, reason: str) -> None:
        super().__init__(
            f"Invalid precision class '{precision_class}': {reason}",
            error_code="INVALID_PRECISION_CLASS",
            details={"precision_class": precision_class, "reason": reason},
        )


class CycleDetectedInCorporateGraphError(CorporateGeoError):
    """Raised when a cyclical loop is discovered in parent-subsidiary traversal."""

    def __init__(self, cycle_path: list[str]) -> None:
        super().__init__(
            f"Cyclical corporate ownership detected along path: {' -> '.join(cycle_path)}",
            error_code="CORPORATE_GRAPH_CYCLE_DETECTED",
            details={"cycle_path": cycle_path},
        )


class InvalidHistoricalAsOfError(CorporateGeoError):
    """Raised when an as-of query specifies an invalid timestamp or future look-ahead."""

    def __init__(self, as_of: str, reason: str) -> None:
        super().__init__(
            f"Invalid historical as-of '{as_of}': {reason}",
            error_code="INVALID_HISTORICAL_AS_OF",
            details={"as_of": as_of, "reason": reason},
        )


class DuplicateFacilityError(CorporateGeoError):
    """Raised when an identical canonical facility record already exists."""

    def __init__(self, existing_id: str, candidate_name: str) -> None:
        super().__init__(
            f"Duplicate facility detected. Matches existing ID: {existing_id} for '{candidate_name}'",
            error_code="DUPLICATE_FACILITY",
            details={"existing_id": existing_id, "candidate_name": candidate_name},
        )


class UnsupportedFacilityTypeError(CorporateGeoError):
    """Raised when an unrecognized facility type is specified."""

    def __init__(self, message: str, error_code: str = "UNSUPPORTED_FACILITY_TYPE", details: dict | None = None) -> None:
        super().__init__(message, error_code=error_code, details=details)

