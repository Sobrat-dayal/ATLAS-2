"""ATLAS Corporate Geography and Facility Mapping Module (Stage 132)."""

from atlas.maps.corporate.domain import (
    CompanyComparisonResult,
    CompanyFootprintResponse,
    CompanyFootprintSummary,
    CorporateFacility,
    CorporateFacilityStatus,
    CorporateFacilityType,
    FacilityEntityLink,
    FacilityEvidenceClaim,
    FacilityRelationshipType,
    FacilityStatusHistory,
    GeographicPrecisionClass,
    VerificationStatus,
)
from atlas.maps.corporate.seed import create_reference_test_service
from atlas.maps.corporate.service import AtlasCorporateGeoService

__all__ = [
    "AtlasCorporateGeoService",
    "CompanyComparisonResult",
    "CompanyFootprintResponse",
    "CompanyFootprintSummary",
    "CorporateFacility",
    "CorporateFacilityStatus",
    "CorporateFacilityType",
    "FacilityEntityLink",
    "FacilityEvidenceClaim",
    "FacilityRelationshipType",
    "FacilityStatusHistory",
    "GeographicPrecisionClass",
    "VerificationStatus",
    "create_reference_test_service",
]

