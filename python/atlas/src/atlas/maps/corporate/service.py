"""Corporate Geographic Intelligence Service (Stage 132).

Coordinates entity resolution, subsidiary graph traversal, facility querying,
precision evaluation, spatial search, H3 aggregation, and company comparison.
"""

from __future__ import annotations

import datetime
import time
from typing import Any, Optional

from atlas.maps.corporate.analytics.comparison import compare_company_footprints
from atlas.maps.corporate.analytics.concentration import compute_facility_concentration
from atlas.maps.corporate.analytics.footprint import compute_company_footprint_summary
from atlas.maps.corporate.analytics.h3_aggregation import aggregate_facilities_to_h3
from atlas.maps.corporate.authorization import enforce_facility_access, enforce_source_entitlement
from atlas.maps.corporate.domain import (
    CompanyComparisonResult,
    CompanyFootprintResponse,
    CompanyFootprintSummary,
    CorporateFacility,
    CorporateFacilityStatus,
    CorporateFacilityType,
    FacilityCorrection,
    FacilityEntityLink,
    FacilityEvidenceClaim,
    FacilityRelationshipType,
    FacilityStatusHistory,
    GeographicPrecisionClass,
    VerificationStatus,
)
from atlas.maps.corporate.entities.graph_traversal import traverse_subsidiaries
from atlas.maps.corporate.entities.resolver import CanonicalEntityResolver
from atlas.maps.corporate.errors import (
    CompanyNotFoundError,
    FacilityNotFoundError,
)
from atlas.maps.corporate.facilities.history import parse_as_of_timestamp
from atlas.maps.corporate.facilities.registry import CorporateFacilityRegistry
from atlas.maps.corporate.observability import log_footprint_query


class AtlasCorporateGeoService:
    """Master service providing verified corporate geography intelligence."""

    def __init__(
        self,
        resolver: CanonicalEntityResolver | None = None,
        registry: CorporateFacilityRegistry | None = None,
        corporate_edges: list[dict[str, Any]] | None = None,
    ) -> None:
        self.resolver = resolver or CanonicalEntityResolver()
        self.registry = registry or CorporateFacilityRegistry()
        self.corporate_edges = corporate_edges or []
        self._corrections: list[FacilityCorrection] = []

    def get_company_footprint(
        self,
        company_identifier: str,
        include_subsidiaries: bool = True,
        facility_types: list[CorporateFacilityType] | None = None,
        statuses: list[CorporateFacilityStatus] | None = None,
        country_code: str | None = None,
        as_of: str | None = None,
        tenant_id: str | None = None,
        limit: int = 1000,
    ) -> CompanyFootprintResponse:
        """Retrieve verified corporate geographic footprint for an entity."""
        start_t = time.perf_counter()
        entity_info = self.resolver.resolve(company_identifier)
        root_entity_id = str(entity_info.get("entity_id") or entity_info.get("company_id"))
        canonical_name = entity_info.get("canonical_name", "Unknown Corporate Entity")
        ticker = (entity_info.get("tickers") or [None])[0]

        as_of_dt = parse_as_of_timestamp(as_of)

        target_entity_ids: set[str]
        scope_str: str
        if include_subsidiaries:
            target_entity_ids = traverse_subsidiaries(
                root_entity_id=root_entity_id,
                edges=self.corporate_edges,
                max_depth=4,
                as_of=as_of_dt,
            )
            scope_str = "subsidiary_inclusive"
        else:
            target_entity_ids = {root_entity_id}
            scope_str = "direct"

        facilities = self.registry.query_facilities(
            entity_ids=target_entity_ids,
            facility_types=facility_types,
            statuses=statuses,
            country_code=country_code,
            as_of=as_of_dt,
            tenant_id=tenant_id,
            limit=limit,
        )

        summary = compute_company_footprint_summary(
            company_id=root_entity_id,
            canonical_name=canonical_name,
            ticker=ticker,
            facilities=facilities,
            root_entity_id=root_entity_id,
        )

        duration_ms = (time.perf_counter() - start_t) * 1000.0
        log_footprint_query(
            company_id=root_entity_id,
            facilities_count=len(facilities),
            distinct_count=summary.distinct_facilities,
            duration_ms=duration_ms,
            tenant_id=tenant_id,
        )

        return CompanyFootprintResponse(
            company_id=root_entity_id,
            canonical_entity_reference={
                "entity_id": root_entity_id,
                "canonical_name": canonical_name,
                "legal_name": entity_info.get("legal_name"),
                "ticker": ticker,
                "lei": entity_info.get("lei"),
                "cik": entity_info.get("cik"),
                "country_code": entity_info.get("primary_country_code"),
            },
            scope=scope_str,
            facilities=facilities,
            summary=summary,
            historical_as_of=as_of,
        )

    def get_facility_details(
        self,
        facility_id: str,
        tenant_id: str | None = None,
    ) -> CorporateFacility:
        """Retrieve full facility record with verified entity links and evidence claims."""
        facility = self.registry.get_facility(facility_id, tenant_id=tenant_id)
        enforce_facility_access(facility, tenant_id=tenant_id)

        # Check source entitlement
        if facility.source_manifest_id:
            enforce_source_entitlement(facility.source_manifest_id)

        return facility

    def get_facility_sources(
        self,
        facility_id: str,
        tenant_id: str | None = None,
    ) -> list[FacilityEvidenceClaim]:
        """Retrieve traceable evidence claims supporting a facility."""
        facility = self.get_facility_details(facility_id, tenant_id=tenant_id)
        return facility.evidence_claims

    def get_facility_history(
        self,
        facility_id: str,
        tenant_id: str | None = None,
    ) -> list[FacilityStatusHistory]:
        """Retrieve historical timeline of operational status revisions."""
        facility = self.get_facility_details(facility_id, tenant_id=tenant_id)
        return facility.status_history

    def search_facilities(
        self,
        query: str | None = None,
        facility_types: list[CorporateFacilityType] | None = None,
        statuses: list[CorporateFacilityStatus] | None = None,
        country_code: str | None = None,
        bbox: tuple[float, float, float, float] | None = None,
        as_of: str | None = None,
        tenant_id: str | None = None,
        limit: int = 200,
    ) -> list[CorporateFacility]:
        """Search corporate facilities matching query keywords or geographic bounds."""
        as_of_dt = parse_as_of_timestamp(as_of)
        all_facilities = self.registry.query_facilities(
            facility_types=facility_types,
            statuses=statuses,
            country_code=country_code,
            bbox=bbox,
            as_of=as_of_dt,
            tenant_id=tenant_id,
            limit=limit,
        )

        if not query:
            return all_facilities

        q = query.strip().lower()
        results: list[CorporateFacility] = []
        for fac in all_facilities:
            if (
                q in fac.canonical_name.lower()
                or (fac.locality and q in fac.locality.lower())
                or (fac.administrative_region and q in fac.administrative_region.lower())
                or (fac.address_text and q in fac.address_text.lower())
            ):
                results.append(fac)

        return results

    def compare_companies(
        self,
        company_a_id: str,
        company_b_id: str,
        include_subsidiaries: bool = True,
        as_of: str | None = None,
        tenant_id: str | None = None,
    ) -> CompanyComparisonResult:
        """Compare geographic footprints between two canonical corporate entities."""
        footprint_a = self.get_company_footprint(
            company_a_id,
            include_subsidiaries=include_subsidiaries,
            as_of=as_of,
            tenant_id=tenant_id,
        )
        footprint_b = self.get_company_footprint(
            company_b_id,
            include_subsidiaries=include_subsidiaries,
            as_of=as_of,
            tenant_id=tenant_id,
        )

        countries_a = {fac.country_code.upper() for fac in footprint_a.facilities if fac.country_code}
        countries_b = {fac.country_code.upper() for fac in footprint_b.facilities if fac.country_code}

        shared = sorted(list(countries_a & countries_b))
        unique_a = sorted(list(countries_a - countries_b))
        unique_b = sorted(list(countries_b - countries_a))

        comparison = compare_company_footprints(footprint_a.summary, footprint_b.summary, as_of=as_of)
        comparison.shared_countries = shared
        comparison.unique_countries_a = unique_a
        comparison.unique_countries_b = unique_b

        return comparison

    def aggregate_facilities_h3(
        self,
        company_id: str | None = None,
        include_subsidiaries: bool = True,
        resolution: int = 4,
        facility_types: list[CorporateFacilityType] | None = None,
        as_of: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """Compute H3 hexagonal spatial density for mapped facilities."""
        facilities: list[CorporateFacility]
        if company_id:
            footprint = self.get_company_footprint(
                company_id,
                include_subsidiaries=include_subsidiaries,
                facility_types=facility_types,
                as_of=as_of,
                tenant_id=tenant_id,
            )
            facilities = footprint.facilities
        else:
            as_of_dt = parse_as_of_timestamp(as_of)
            facilities = self.registry.query_facilities(
                facility_types=facility_types,
                as_of=as_of_dt,
                tenant_id=tenant_id,
                limit=10000,
            )

        return aggregate_facilities_to_h3(facilities, resolution=resolution)

    def submit_correction(
        self,
        facility_id: str,
        user_id: str,
        correction_type: str,
        details: str,
        tenant_id: str | None = None,
    ) -> FacilityCorrection:
        """Submit a user correction proposal for administrative review."""
        facility = self.registry.get_facility(facility_id, tenant_id=tenant_id)
        correction = FacilityCorrection(
            correction_id=f"corr_{len(self._corrections) + 1}",
            facility_id=facility.facility_id,
            user_id=user_id,
            tenant_id=tenant_id,
            correction_type=correction_type,
            details=details,
        )
        self._corrections.append(correction)
        return correction

