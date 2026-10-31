"""Facility operational status validation and rules (Stage 132)."""

from __future__ import annotations

from atlas.maps.corporate.domain import CorporateFacilityStatus


def is_facility_operational(status: CorporateFacilityStatus) -> bool:
    """Check if facility is currently verified operational.

    Announced, planned, or under construction facilities are strictly NOT operational.
    """
    return status == CorporateFacilityStatus.OPERATIONAL


def resolve_facility_status(
    status_str: str | None,
    announced_only: bool = False,
    is_closed: bool = False,
) -> CorporateFacilityStatus:
    """Resolve status safely, defaulting to STATUS_UNKNOWN rather than guessing active operation."""
    if not status_str:
        if announced_only:
            return CorporateFacilityStatus.ANNOUNCED
        if is_closed:
            return CorporateFacilityStatus.PERMANENTLY_CLOSED
        return CorporateFacilityStatus.STATUS_UNKNOWN

    clean = status_str.strip().upper()
    try:
        return CorporateFacilityStatus(clean)
    except (ValueError, KeyError):
        return CorporateFacilityStatus.STATUS_UNKNOWN

