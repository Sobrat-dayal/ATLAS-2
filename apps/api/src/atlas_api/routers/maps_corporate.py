"""FastAPI Router for ATLAS Corporate Geography and Facility Mapping (Stage 132).

Provides endpoints for company footprints, facility directories, evidence citations,
historical revisions, spatial queries, H3 aggregations, and company comparisons.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from atlas.maps.corporate.domain import (
    CorporateFacilityStatus,
    CorporateFacilityType,
)
from atlas.maps.corporate.errors import (
    CompanyNotFoundError,
    CycleDetectedInCorporateGraphError,
    DuplicateFacilityError,
    FacilityAccessDeniedError,
    FacilityNotFoundError,
    InvalidFacilityGeometryError,
    InvalidHistoricalAsOfError,
    InvalidPrecisionClassError,
    SourceEntitlementRevokedError,
)
from atlas.maps.corporate.schemas import (
    CompanyComparisonRequestSchema,
    CompanyComparisonResponseSchema,
    CompanyFootprintResponseSchema,
    CompanyFootprintSummarySchema,
    CorporateFacilitySchema,
    FacilityAggregateRequestSchema,
    FacilityCorrectionRequestSchema,
    FacilityCorrectionResponseSchema,
    FacilityEvidenceClaimSchema,
    FacilitySpatialQueryRequestSchema,
    FacilityStatusHistorySchema,
)
from atlas.maps.corporate.seed import create_reference_test_service
from atlas.maps.corporate.service import AtlasCorporateGeoService
from fastapi import APIRouter, HTTPException, Query, status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Maps Corporate Geography"])

_corp_service: Optional[AtlasCorporateGeoService] = None


def get_corporate_service() -> AtlasCorporateGeoService:
    """Retrieve or initialize the singleton Corporate Geographic Intelligence Service."""
    global _corp_service
    if _corp_service is None:
        _corp_service = create_reference_test_service()
    return _corp_service


def _map_facility_to_schema(fac: Any) -> dict[str, Any]:
    """Helper to serialize CorporateFacility domain object to schema-compatible dict."""
    return {
        "facility_id": fac.facility_id,
        "canonical_name": fac.canonical_name,
        "facility_type": fac.facility_type.value if hasattr(fac.facility_type, "value") else str(fac.facility_type),
        "facility_status": fac.facility_status.value if hasattr(fac.facility_status, "value") else str(fac.facility_status),
        "precision_class": fac.precision_class.value if hasattr(fac.precision_class, "value") else str(fac.precision_class),
        "country_code": fac.country_code,
        "administrative_region": fac.administrative_region,
        "locality": fac.locality,
        "address_text": fac.address_text,
        "longitude": fac.longitude,
        "latitude": fac.latitude,
        "geometry_type": fac.geometry_type,
        "coordinates": fac.coordinates,
        "primary_entity_id": fac.primary_entity_id,
        "operating_start_date": fac.operating_start_date.isoformat() if fac.operating_start_date else None,
        "operating_end_date": fac.operating_end_date.isoformat() if fac.operating_end_date else None,
        "source_manifest_id": fac.source_manifest_id,
        "verification_status": fac.verification_status.value if hasattr(fac.verification_status, "value") else str(fac.verification_status),
        "is_public": fac.is_public,
        "links": [
            {
                "link_id": l.link_id,
                "facility_id": l.facility_id,
                "legal_entity_id": l.legal_entity_id,
                "company_id": l.company_id,
                "relationship_type": l.relationship_type.value if hasattr(l.relationship_type, "value") else str(l.relationship_type),
                "role_description": l.role_description,
                "ownership_percentage": l.ownership_percentage,
                "valid_from": l.valid_from.isoformat() if l.valid_from else None,
                "valid_to": l.valid_to.isoformat() if l.valid_to else None,
                "source_manifest_id": l.source_manifest_id,
                "verification_status": l.verification_status.value if hasattr(l.verification_status, "value") else str(l.verification_status),
            }
            for l in fac.links
        ],
        "evidence_claims": [
            {
                "claim_id": c.claim_id,
                "facility_id": c.facility_id,
                "subject_entity_id": c.subject_entity_id,
                "predicate": c.predicate,
                "source_title": c.source_title,
                "source_document_id": c.source_document_id,
                "publisher": c.publisher,
                "publication_date": c.publication_date.isoformat() if c.publication_date else "",
                "exact_evidence_span": c.exact_evidence_span,
                "document_url": c.document_url,
                "licensing_policy": c.licensing_policy,
                "verification_status": c.verification_status.value if hasattr(c.verification_status, "value") else str(c.verification_status),
            }
            for c in fac.evidence_claims
        ],
        "status_history": [
            {
                "history_id": h.history_id,
                "facility_id": h.facility_id,
                "status": h.status.value if hasattr(h.status, "value") else str(h.status),
                "valid_from": h.valid_from.isoformat() if h.valid_from else None,
                "valid_to": h.valid_to.isoformat() if h.valid_to else None,
                "source_manifest_id": h.source_manifest_id,
                "verification_status": h.verification_status.value if hasattr(h.verification_status, "value") else str(h.verification_status),
                "recorded_at": h.recorded_at.isoformat() if h.recorded_at else "",
            }
            for h in fac.status_history
        ],
    }


def _map_summary_to_schema(summary: Any) -> dict[str, Any]:
    return {
        "company_id": summary.company_id,
        "canonical_name": summary.canonical_name,
        "ticker": summary.ticker,
        "total_facilities": summary.total_facilities,
        "distinct_facilities": summary.distinct_facilities,
        "countries_count": summary.countries_count,
        "facility_type_breakdown": summary.facility_type_breakdown,
        "status_breakdown": summary.status_breakdown,
        "direct_facilities_count": summary.direct_facilities_count,
        "subsidiary_facilities_count": summary.subsidiary_facilities_count,
        "unresolved_locations_count": summary.unresolved_locations_count,
        "source_coverage": summary.source_coverage,
    }


# ============================================================================
# Company Footprint & Search Endpoints
# ============================================================================


@router.get("/companies/search", response_model=list[dict[str, Any]])
def search_mapped_companies(
    q: Optional[str] = Query(None, description="Search query by name, ticker, LEI, or CIK"),
    limit: int = Query(20, ge=1, le=100),
) -> list[dict[str, Any]]:
    """Search registered companies available in the corporate geography system."""
    svc = get_corporate_service()
    return svc.resolver.search_companies(q or "", limit=limit)


@router.get("/companies/{company_id}/footprint", response_model=CompanyFootprintResponseSchema)
def get_company_footprint(
    company_id: str,
    include_subsidiaries: bool = Query(True, description="Include verified subsidiary facilities"),
    country: Optional[str] = Query(None, description="ISO 2-letter country code"),
    as_of: Optional[str] = Query(None, description="Historical as-of date (ISO 8601)"),
    limit: int = Query(1000, ge=1, le=5000),
) -> CompanyFootprintResponseSchema:
    """Retrieve verified geographic footprint of a company, including locations and summary."""
    svc = get_corporate_service()
    try:
        resp = svc.get_company_footprint(
            company_identifier=company_id,
            include_subsidiaries=include_subsidiaries,
            country_code=country,
            as_of=as_of,
            limit=limit,
        )
        return CompanyFootprintResponseSchema(
            company_id=resp.company_id,
            canonical_entity_reference=resp.canonical_entity_reference,
            scope=resp.scope,
            facilities=[_map_facility_to_schema(f) for f in resp.facilities],  # type: ignore
            summary=CompanyFootprintSummarySchema(**_map_summary_to_schema(resp.summary)),
            historical_as_of=resp.historical_as_of,
            generated_at=resp.generated_at,
        )
    except CompanyNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except (CycleDetectedInCorporateGraphError, InvalidHistoricalAsOfError) as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.get("/companies/{company_id}/summary", response_model=CompanyFootprintSummarySchema)
def get_company_footprint_summary(
    company_id: str,
    include_subsidiaries: bool = Query(True),
    as_of: Optional[str] = Query(None),
) -> CompanyFootprintSummarySchema:
    """Retrieve statistical summary of recorded facilities for an entity."""
    svc = get_corporate_service()
    try:
        resp = svc.get_company_footprint(
            company_identifier=company_id,
            include_subsidiaries=include_subsidiaries,
            as_of=as_of,
        )
        return CompanyFootprintSummarySchema(**_map_summary_to_schema(resp.summary))
    except CompanyNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/companies/compare", response_model=CompanyComparisonResponseSchema)
def compare_companies(request: CompanyComparisonRequestSchema) -> CompanyComparisonResponseSchema:
    """Compare geographic footprints and presence between two corporate entities."""
    svc = get_corporate_service()
    try:
        res = svc.compare_companies(
            company_a_id=request.company_a_id,
            company_b_id=request.company_b_id,
            include_subsidiaries=request.include_subsidiaries,
            as_of=request.as_of,
        )
        return CompanyComparisonResponseSchema(
            company_a=CompanyFootprintSummarySchema(**_map_summary_to_schema(res.company_a)),
            company_b=CompanyFootprintSummarySchema(**_map_summary_to_schema(res.company_b)),
            shared_countries=res.shared_countries,
            unique_countries_a=res.unique_countries_a,
            unique_countries_b=res.unique_countries_b,
            type_comparison=res.type_comparison,
            as_of=res.as_of,
        )
    except CompanyNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


# ============================================================================
# Facility Directory, Details & Provenance Endpoints
# ============================================================================


@router.get("/facilities", response_model=list[CorporateFacilitySchema])
def list_facilities(
    q: Optional[str] = Query(None, description="Search query string"),
    country: Optional[str] = Query(None, description="Country filter"),
    as_of: Optional[str] = Query(None, description="Historical as-of date"),
    limit: int = Query(200, ge=1, le=1000),
) -> list[CorporateFacilitySchema]:
    """Search and filter corporate facilities."""
    svc = get_corporate_service()
    facs = svc.search_facilities(query=q, country_code=country, as_of=as_of, limit=limit)
    return [CorporateFacilitySchema(**_map_facility_to_schema(f)) for f in facs]


@router.get("/facilities/{facility_id}", response_model=CorporateFacilitySchema)
def get_facility_by_id(facility_id: str) -> CorporateFacilitySchema:
    """Retrieve full record for a specific corporate facility."""
    svc = get_corporate_service()
    try:
        fac = svc.get_facility_details(facility_id)
        return CorporateFacilitySchema(**_map_facility_to_schema(fac))
    except FacilityNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))
    except FacilityAccessDeniedError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err))
    except SourceEntitlementRevokedError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(err))


@router.get("/facilities/{facility_id}/sources", response_model=list[FacilityEvidenceClaimSchema])
def get_facility_evidence(facility_id: str) -> list[FacilityEvidenceClaimSchema]:
    """Retrieve exact citations and supporting evidence claims for a facility."""
    svc = get_corporate_service()
    try:
        claims = svc.get_facility_sources(facility_id)
        return [
            FacilityEvidenceClaimSchema(
                claim_id=c.claim_id,
                facility_id=c.facility_id,
                subject_entity_id=c.subject_entity_id,
                predicate=c.predicate,
                source_title=c.source_title,
                source_document_id=c.source_document_id,
                publisher=c.publisher,
                publication_date=c.publication_date.isoformat() if c.publication_date else "",
                exact_evidence_span=c.exact_evidence_span,
                document_url=c.document_url,
                licensing_policy=c.licensing_policy,
                verification_status=c.verification_status.value if hasattr(c.verification_status, "value") else str(c.verification_status),
            )
            for c in claims
        ]
    except FacilityNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.get("/facilities/{facility_id}/history", response_model=list[FacilityStatusHistorySchema])
def get_facility_status_history(facility_id: str) -> list[FacilityStatusHistorySchema]:
    """Retrieve historical timeline of operational status revisions."""
    svc = get_corporate_service()
    try:
        hist = svc.get_facility_history(facility_id)
        return [
            FacilityStatusHistorySchema(
                history_id=h.history_id,
                facility_id=h.facility_id,
                status=h.status.value if hasattr(h.status, "value") else str(h.status),
                valid_from=h.valid_from.isoformat() if h.valid_from else None,
                valid_to=h.valid_to.isoformat() if h.valid_to else None,
                source_manifest_id=h.source_manifest_id,
                verification_status=h.verification_status.value if hasattr(h.verification_status, "value") else str(h.verification_status),
                recorded_at=h.recorded_at.isoformat() if h.recorded_at else "",
            )
            for h in hist
        ]
    except FacilityNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))


@router.post("/facilities/spatial-query", response_model=list[CorporateFacilitySchema])
def spatial_query_facilities(request: FacilitySpatialQueryRequestSchema) -> list[CorporateFacilitySchema]:
    """Execute spatial search within geographic bounding box or country."""
    svc = get_corporate_service()
    bbox_tuple = tuple(request.bbox) if request.bbox and len(request.bbox) == 4 else None  # type: ignore

    types = [CorporateFacilityType(t) for t in request.facility_types] if request.facility_types else None
    statuses = [CorporateFacilityStatus(s) for s in request.statuses] if request.statuses else None

    facs = svc.search_facilities(
        query=request.query,
        facility_types=types,
        statuses=statuses,
        country_code=request.country_code,
        bbox=bbox_tuple,  # type: ignore
        as_of=request.as_of,
        limit=request.limit,
    )
    return [CorporateFacilitySchema(**_map_facility_to_schema(f)) for f in facs]


@router.post("/facilities/aggregate", response_model=dict[str, Any])
def aggregate_facilities(request: FacilityAggregateRequestSchema) -> dict[str, Any]:
    """Execute H3 hexagonal spatial aggregation of mapped corporate facilities."""
    svc = get_corporate_service()
    types = [CorporateFacilityType(t) for t in request.facility_types] if request.facility_types else None
    return svc.aggregate_facilities_h3(
        company_id=request.company_id,
        include_subsidiaries=request.include_subsidiaries,
        resolution=request.resolution,
        facility_types=types,
        as_of=request.as_of,
    )


@router.post("/facilities/corrections", response_model=FacilityCorrectionResponseSchema)
def submit_facility_correction(request: FacilityCorrectionRequestSchema) -> FacilityCorrectionResponseSchema:
    """Submit a user correction proposal for administrative review."""
    svc = get_corporate_service()
    try:
        corr = svc.submit_correction(
            facility_id=request.facility_id,
            user_id="usr_current_session",
            correction_type=request.correction_type,
            details=request.details,
        )
        return FacilityCorrectionResponseSchema(
            correction_id=corr.correction_id,
            facility_id=corr.facility_id,
            user_id=corr.user_id,
            correction_type=corr.correction_type,
            details=corr.details,
            status=corr.status,
            submitted_at=corr.submitted_at.isoformat(),
        )
    except FacilityNotFoundError as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(err))

