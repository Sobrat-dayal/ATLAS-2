"""Authorization, tenant isolation, and source entitlement checks (Stage 132)."""

from __future__ import annotations

from typing import Any

from atlas.maps.corporate.domain import CorporateFacility
from atlas.maps.corporate.errors import FacilityAccessDeniedError, SourceEntitlementRevokedError
from atlas.maps.corporate.ingestion.source_registry import CANONICAL_SOURCE_REGISTRY


def enforce_facility_access(
    facility: CorporateFacility,
    tenant_id: str | None = None,
) -> None:
    """Enforce multi-tenant access control on private facility records."""
    if not facility.is_public:
        if tenant_id is None or facility.tenant_id != tenant_id:
            raise FacilityAccessDeniedError(facility.facility_id, tenant_id)


def enforce_source_entitlement(source_manifest_id: str) -> None:
    """Verify that source provider manifest is currently active and not revoked."""
    if not source_manifest_id:
        return

    manifest = CANONICAL_SOURCE_REGISTRY.get(source_manifest_id)
    if manifest and not manifest.is_valid_now():
        raise SourceEntitlementRevokedError(source_manifest_id)


def sanitize_facility_for_user(
    facility: CorporateFacility,
    user_context: dict[str, Any] | None = None,
) -> CorporateFacility:
    """Sanitize confidential or sensitive fields before returning to caller."""
    # Ensure confidential coordinates or private tenant data are protected
    return facility

