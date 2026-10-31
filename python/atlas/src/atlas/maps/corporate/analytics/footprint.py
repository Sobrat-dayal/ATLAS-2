"""Company geographic footprint calculation and statistical aggregation (Stage 132)."""

from __future__ import annotations

from typing import Any

from atlas.maps.corporate.domain import (
    CompanyFootprintSummary,
    CorporateFacility,
    GeographicPrecisionClass,
)


def compute_company_footprint_summary(
    company_id: str,
    canonical_name: str,
    ticker: str | None,
    facilities: list[CorporateFacility],
    root_entity_id: str,
) -> CompanyFootprintSummary:
    """Compute verified geographic footprint metrics.

    Guarantees:
    - Distinct facility counting: each unique facility_id is counted exactly once.
    - Accurately classifies direct vs subsidiary associations.
    - Reports unresolved coordinates truthfully.
    """
    distinct_facility_ids = set()
    countries = set()
    type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    direct_count = 0
    subsidiary_count = 0
    unresolved_count = 0
    sources = set()

    for fac in facilities:
        distinct_facility_ids.add(fac.facility_id)

        if fac.country_code:
            countries.add(fac.country_code.upper())

        # Type breakdown
        t_key = fac.facility_type.value
        type_counts[t_key] = type_counts.get(t_key, 0) + 1

        # Status breakdown
        s_key = fac.facility_status.value
        status_counts[s_key] = status_counts.get(s_key, 0) + 1

        # Precision / location check
        if (
            fac.longitude is None
            or fac.latitude is None
            or fac.precision_class == GeographicPrecisionClass.LOCATION_UNRESOLVED
        ):
            unresolved_count += 1

        # Source manifest
        if fac.source_manifest_id:
            sources.add(fac.source_manifest_id)

        # Direct vs subsidiary association
        is_direct = fac.primary_entity_id == root_entity_id or any(
            link.legal_entity_id == root_entity_id or link.company_id == root_entity_id
            for link in fac.links
        )
        if is_direct:
            direct_count += 1
        else:
            subsidiary_count += 1

    return CompanyFootprintSummary(
        company_id=company_id,
        canonical_name=canonical_name,
        ticker=ticker,
        total_facilities=len(facilities),
        distinct_facilities=len(distinct_facility_ids),
        countries_count=len(countries),
        facility_type_breakdown=type_counts,
        status_breakdown=status_counts,
        direct_facilities_count=direct_count,
        subsidiary_facilities_count=subsidiary_count,
        unresolved_locations_count=unresolved_count,
        source_coverage={
            "sources_count": len(sources),
            "sources_list": sorted(list(sources)),
            "coverage_disclaimer": "Metrics represent verified records from authorized disclosures; unknown locations are not assumed zero.",
        },
    )

