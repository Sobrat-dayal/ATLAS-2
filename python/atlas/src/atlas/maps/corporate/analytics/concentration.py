"""Geographic concentration analytics and Herfindahl-Hirschman index (Stage 132)."""

from __future__ import annotations

from typing import Any

from atlas.maps.corporate.domain import CorporateFacility


def compute_facility_concentration(facilities: list[CorporateFacility]) -> dict[str, Any]:
    """Compute geographic distribution and concentration metrics across countries and regions.

    Guarantees:
    - Accurate country percentage distribution based on distinct facilities.
    - Computes Herfindahl-Hirschman Index (HHI) for geographic diversification.
    - Never infers financial revenue exposure or workforce size from facility counts alone.
    """
    total = len(facilities)
    if total == 0:
        return {
            "total_facilities": 0,
            "countries_count": 0,
            "top_countries": [],
            "top_regions": [],
            "country_hhi": 0.0,
            "concentration_tier": "DIVERSIFIED",
        }

    country_counts: dict[str, int] = {}
    region_counts: dict[str, int] = {}

    for fac in facilities:
        c = fac.country_code.upper() if fac.country_code else "UNKNOWN"
        country_counts[c] = country_counts.get(c, 0) + 1

        if fac.administrative_region:
            r = f"{fac.administrative_region}, {c}"
            region_counts[r] = region_counts.get(r, 0) + 1

    top_countries = []
    hhi = 0.0
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True):
        share_pct = round((count / total) * 100.0, 2)
        hhi += (share_pct) ** 2
        top_countries.append({"country_code": country, "count": count, "share_pct": share_pct})

    top_regions = []
    for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        top_regions.append({
            "region": region,
            "count": count,
            "share_pct": round((count / total) * 100.0, 2),
        })

    # HHI Interpretation: < 1500 unconcentrated/diversified, 1500-2500 moderate, > 2500 concentrated
    hhi_score = round(hhi, 1)
    if hhi_score > 2500.0:
        tier = "HIGHLY_CONCENTRATED"
    elif hhi_score > 1500.0:
        tier = "MODERATELY_CONCENTRATED"
    else:
        tier = "GEOGRAPHICALLY_DIVERSIFIED"

    return {
        "total_facilities": total,
        "countries_count": len(country_counts),
        "top_countries": top_countries,
        "top_regions": top_regions,
        "country_hhi": hhi_score,
        "concentration_tier": tier,
    }

