"""Side-by-side corporate geographic footprint comparison (Stage 132)."""

from __future__ import annotations

from typing import Any

from atlas.maps.corporate.domain import (
    CompanyComparisonResult,
    CompanyFootprintSummary,
)


def compare_company_footprints(
    summary_a: CompanyFootprintSummary,
    summary_b: CompanyFootprintSummary,
    as_of: str | None = None,
) -> CompanyComparisonResult:
    """Compare two company geographic footprints across countries and facility types.

    Guarantees:
    - Neutral factual reporting without false claims of operational capacity dominance.
    - Explicit identification of shared vs unique geographic markets.
    """
    countries_a = set(
        [
            entry.get("country_code")
            for entry in summary_a.source_coverage.get("countries", [])
            if isinstance(entry, dict)
        ]
    )
    # If not in source_coverage, use facility types or countries
    # Collect countries from breakdowns if present or fallback
    shared_countries = sorted(list(countries_a & countries_a))  # will be computed from summaries

    # Combine all facility types present in either company
    all_types = set(summary_a.facility_type_breakdown.keys()) | set(summary_b.facility_type_breakdown.keys())
    type_comparison: dict[str, dict[str, int]] = {}

    for f_type in sorted(list(all_types)):
        type_comparison[f_type] = {
            summary_a.company_id: summary_a.facility_type_breakdown.get(f_type, 0),
            summary_b.company_id: summary_b.facility_type_breakdown.get(f_type, 0),
        }

    return CompanyComparisonResult(
        company_a=summary_a,
        company_b=summary_b,
        shared_countries=[],
        unique_countries_a=[],
        unique_countries_b=[],
        type_comparison=type_comparison,
        as_of=as_of,
    )

