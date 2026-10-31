"""Domain models and entity definitions for Corporate Geography and Facility Mapping (Stage 132).

Strictly distinguishes between legal entities, issuers, securities, headquarters,
registered offices, manufacturing facilities, operational vs announced status,
owner vs operator roles, and verified vs approximate coordinates.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CorporateFacilityType(str, Enum):
    """Canonical taxonomy of corporate physical and operational facilities."""

    CORPORATE_HEADQUARTERS = "CORPORATE_HEADQUARTERS"
    REGISTERED_OFFICE = "REGISTERED_OFFICE"
    REGIONAL_HEADQUARTERS = "REGIONAL_HEADQUARTERS"
    CORPORATE_OFFICE = "CORPORATE_OFFICE"
    MANUFACTURING_FACILITY = "MANUFACTURING_FACILITY"
    ASSEMBLY_FACILITY = "ASSEMBLY_FACILITY"
    RESEARCH_AND_DEVELOPMENT = "RESEARCH_AND_DEVELOPMENT"
    DISTRIBUTION_CENTER = "DISTRIBUTION_CENTER"
    WAREHOUSE = "WAREHOUSE"
    CORPORATE_CAMPUS = "CORPORATE_CAMPUS"
    CUSTOMER_SUPPORT_CENTER = "CUSTOMER_SUPPORT_CENTER"
    SERVICE_CENTER = "SERVICE_CENTER"
    OTHER_VERIFIED_FACILITY = "OTHER_VERIFIED_FACILITY"


class CorporateFacilityStatus(str, Enum):
    """Evidence-backed operational status of a corporate facility."""

    ANNOUNCED = "ANNOUNCED"
    PLANNED = "PLANNED"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    OPERATIONAL = "OPERATIONAL"
    TEMPORARILY_CLOSED = "TEMPORARILY_CLOSED"
    PERMANENTLY_CLOSED = "PERMANENTLY_CLOSED"
    SOLD = "SOLD"
    RELOCATED = "RELOCATED"
    HISTORICAL = "HISTORICAL"
    STATUS_UNKNOWN = "STATUS_UNKNOWN"


class GeographicPrecisionClass(str, Enum):
    """Categorical classification of coordinate accuracy and spatial resolution."""

    VERIFIED_SITE_POINT = "VERIFIED_SITE_POINT"
    VERIFIED_SITE_POLYGON = "VERIFIED_SITE_POLYGON"
    VERIFIED_STREET_ADDRESS = "VERIFIED_STREET_ADDRESS"
    GEOCODED_ADDRESS_APPROXIMATE = "GEOCODED_ADDRESS_APPROXIMATE"
    LOCALITY_CENTROID = "LOCALITY_CENTROID"
    ADMINISTRATIVE_REGION_ONLY = "ADMINISTRATIVE_REGION_ONLY"
    COUNTRY_ONLY = "COUNTRY_ONLY"
    LOCATION_UNRESOLVED = "LOCATION_UNRESOLVED"


class FacilityRelationshipType(str, Enum):
    """Canonical relationship role linking a legal entity to a physical facility."""

    OWNED_BY = "OWNED_BY"
    OPERATED_BY = "OPERATED_BY"
    LEASED_BY = "LEASED_BY"
    OCCUPIED_BY = "OCCUPIED_BY"
    MANAGED_BY = "MANAGED_BY"
    HEADQUARTERS_OF = "HEADQUARTERS_OF"
    REGISTERED_ADDRESS_OF = "REGISTERED_ADDRESS_OF"
    ANNOUNCED_BY = "ANNOUNCED_BY"
    FORMERLY_OPERATED_BY = "FORMERLY_OPERATED_BY"


class VerificationStatus(str, Enum):
    """Evidence confidence and verification state for corporate claims."""

    VERIFIED = "VERIFIED"
    CORROBORATED = "CORROBORATED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"


@dataclass
class FacilityEntityLink:
    """Association connecting a facility to a legal entity or company in a specific role."""

    link_id: str
    facility_id: str
    legal_entity_id: str
    company_id: str
    relationship_type: FacilityRelationshipType
    role_description: str = ""
    ownership_percentage: Optional[float] = None
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None
    source_manifest_id: str = ""
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


@dataclass
class FacilityStatusHistory:
    """Historical timeline of operational status revisions."""

    history_id: str
    facility_id: str
    status: CorporateFacilityStatus
    valid_from: Optional[datetime.datetime] = None
    valid_to: Optional[datetime.datetime] = None
    source_manifest_id: str = ""
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    recorded_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


@dataclass
class FacilityEvidenceClaim:
    """Traceable evidence citation proving a facility existence, location, or relationship."""

    claim_id: str
    facility_id: str
    subject_entity_id: str
    predicate: str
    source_title: str
    source_document_id: str
    publisher: str
    publication_date: datetime.datetime
    exact_evidence_span: str
    document_url: Optional[str] = None
    licensing_policy: str = "authorized_disclosure"
    verification_status: VerificationStatus = VerificationStatus.VERIFIED


@dataclass
class CorporateFacility:
    """Canonical corporate facility representation with verified geography and relationships."""

    facility_id: str
    canonical_name: str
    facility_type: CorporateFacilityType
    facility_status: CorporateFacilityStatus
    precision_class: GeographicPrecisionClass
    country_code: str
    administrative_region: str = ""
    locality: str = ""
    address_text: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    geometry_type: str = "POINT"
    coordinates: Optional[Any] = None
    primary_entity_id: str = ""
    operating_start_date: Optional[datetime.date] = None
    operating_end_date: Optional[datetime.date] = None
    source_manifest_id: str = ""
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    is_public: bool = True
    tenant_id: Optional[str] = None
    links: list[FacilityEntityLink] = field(default_factory=list)
    evidence_claims: list[FacilityEvidenceClaim] = field(default_factory=list)
    status_history: list[FacilityStatusHistory] = field(default_factory=list)
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def to_geojson_feature(self) -> dict[str, Any]:
        """Convert facility to GeoJSON Feature with precision-aware geometry and properties."""
        coords = None
        if self.longitude is not None and self.latitude is not None:
            if self.geometry_type.upper() == "POLYGON" and isinstance(self.coordinates, list):
                coords = self.coordinates
            else:
                coords = [self.longitude, self.latitude]

        geom = None
        if coords is not None:
            geom = {
                "type": self.geometry_type.capitalize() if self.geometry_type.upper() == "POLYGON" else "Point",
                "coordinates": coords,
            }

        return {
            "type": "Feature",
            "id": self.facility_id,
            "geometry": geom,
            "properties": {
                "facility_id": self.facility_id,
                "canonical_name": self.canonical_name,
                "facility_type": self.facility_type.value,
                "facility_status": self.facility_status.value,
                "precision_class": self.precision_class.value,
                "country_code": self.country_code,
                "administrative_region": self.administrative_region,
                "locality": self.locality,
                "primary_entity_id": self.primary_entity_id,
                "verification_status": self.verification_status.value,
                "source_manifest_id": self.source_manifest_id,
                "links_count": len(self.links),
                "is_public": self.is_public,
            },
        }


@dataclass
class FacilityCorrection:
    """User-submitted correction proposal for review."""

    correction_id: str
    facility_id: str
    user_id: str
    tenant_id: Optional[str]
    correction_type: str  # REPORT_INCORRECT_LOCATION, REPORT_DUPLICATE, etc.
    details: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    submitted_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


@dataclass
class CompanyFootprintSummary:
    """Aggregated statistical summary of a company's recorded geographic footprint."""

    company_id: str
    canonical_name: str
    ticker: Optional[str]
    total_facilities: int
    distinct_facilities: int
    countries_count: int
    facility_type_breakdown: dict[str, int]
    status_breakdown: dict[str, int]
    direct_facilities_count: int
    subsidiary_facilities_count: int
    unresolved_locations_count: int
    source_coverage: dict[str, Any]


@dataclass
class CompanyFootprintResponse:
    """Complete company geographic footprint payload."""

    company_id: str
    canonical_entity_reference: dict[str, Any]
    scope: str  # "direct" or "subsidiary_inclusive"
    facilities: list[CorporateFacility]
    summary: CompanyFootprintSummary
    historical_as_of: Optional[str] = None
    generated_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


@dataclass
class CompanyComparisonResult:
    """Side-by-side comparison of two company geographic footprints."""

    company_a: CompanyFootprintSummary
    company_b: CompanyFootprintSummary
    shared_countries: list[str]
    unique_countries_a: list[str]
    unique_countries_b: list[str]
    type_comparison: dict[str, dict[str, int]]
    as_of: Optional[str] = None

