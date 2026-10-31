"""Facility type validation and semantics (Stage 132)."""

from __future__ import annotations

from atlas.maps.corporate.domain import CorporateFacilityType
from atlas.maps.corporate.errors import UnsupportedFacilityTypeError


def validate_facility_type(type_str: str) -> CorporateFacilityType:
    """Validate and return canonical CorporateFacilityType enum."""
    try:
        return CorporateFacilityType(type_str.upper())
    except (ValueError, KeyError):
        raise UnsupportedFacilityTypeError(
            f"Invalid facility type '{type_str}'. Must be one of {[t.value for t in CorporateFacilityType]}",
            error_code="UNSUPPORTED_FACILITY_TYPE",
            details={"facility_type": type_str},
        )


def verify_type_claims(facility_type: CorporateFacilityType, evidence_text: str) -> bool:
    """Verify that evidence text supports the assigned facility type.

    Guarantees:
    - A legal registered office is never assumed to be an operating manufacturing facility or HQ.
    - Manufacturing classification requires explicit plant/factory/assembly evidence.
    """
    lower = evidence_text.lower()

    if facility_type == CorporateFacilityType.REGISTERED_OFFICE:
        # Valid as registered address, statutory seat, agent office
        return True

    if facility_type in (CorporateFacilityType.MANUFACTURING_FACILITY, CorporateFacilityType.ASSEMBLY_FACILITY):
        manufacturing_keywords = [
            "manufactur", "plant", "factory", "assembly", "fabricat", "production facility", "works", "foundry"
        ]
        return any(kw in lower for kw in manufacturing_keywords)

    if facility_type == CorporateFacilityType.CORPORATE_HEADQUARTERS:
        hq_keywords = ["headquarters", "principal executive", "global hq", "corporate office", "head office"]
        return any(kw in lower for kw in hq_keywords)

    return True

