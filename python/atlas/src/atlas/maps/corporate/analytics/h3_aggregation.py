"""Precision-aware H3 hexagon aggregation for corporate facilities (Stage 132).

Guarantees:
- Distinct facility counting: each unique facility_id is counted at most once per cell.
- Approximate locality/city centroids are excluded from high-resolution site cells (resolution >= 6).
- Unresolved coordinates are omitted from spatial cells and tracked in summary metadata.
"""

from __future__ import annotations

from typing import Any

from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.indexing import lat_lng_to_cell
from atlas.maps.corporate.domain import CorporateFacility, GeographicPrecisionClass


def aggregate_facilities_to_h3(
    facilities: list[CorporateFacility],
    resolution: int = 4,
    exclude_approximate_from_high_res: bool = True,
) -> dict[str, Any]:
    """Aggregate corporate facilities into H3 hexagonal partitions."""
    cell_to_facilities: dict[str, set[str]] = {}
    cell_to_entities: dict[str, set[str]] = {}
    unresolved_count = 0
    suppressed_approximate_count = 0

    # Low precision classifications that must not appear in high-res site cells
    low_precision_classes = {
        GeographicPrecisionClass.LOCALITY_CENTROID,
        GeographicPrecisionClass.ADMINISTRATIVE_REGION_ONLY,
        GeographicPrecisionClass.COUNTRY_ONLY,
        GeographicPrecisionClass.LOCATION_UNRESOLVED,
    }

    for fac in facilities:
        if fac.longitude is None or fac.latitude is None:
            unresolved_count += 1
            continue

        if fac.precision_class == GeographicPrecisionClass.LOCATION_UNRESOLVED:
            unresolved_count += 1
            continue

        # Precision gate: do not place city/region centroids into high-res site grids
        if resolution >= 6 and exclude_approximate_from_high_res and fac.precision_class in low_precision_classes:
            suppressed_approximate_count += 1
            continue

        cell_id = lat_lng_to_cell(fac.latitude, fac.longitude, resolution)
        cell_to_facilities.setdefault(cell_id, set()).add(fac.facility_id)

        # Collect distinct corporate entities
        ent_id = fac.primary_entity_id
        if ent_id:
            cell_to_entities.setdefault(cell_id, set()).add(ent_id)
        for link in fac.links:
            if link.legal_entity_id:
                cell_to_entities.setdefault(cell_id, set()).add(link.legal_entity_id)

    aggregates = []

    for cell_id, fac_ids in cell_to_facilities.items():
        distinct_count = len(fac_ids)
        entities_count = len(cell_to_entities.get(cell_id, set()))
        try:
            area_km2 = get_cell_area_km2(cell_id)
        except Exception:
            area_km2 = 1.0
        density = round(distinct_count / area_km2, 4) if area_km2 > 0 else 0.0

        aggregates.append({
            "h3_cell_id": cell_id,
            "resolution": resolution,
            "value": distinct_count,
            "distinct_facilities_count": distinct_count,
            "distinct_entities_count": entities_count,
            "density_per_km2": density,
            "cell_area_km2": round(area_km2, 4),
            "facility_ids": sorted(list(fac_ids)),
        })

    # Sort descending by facility count
    aggregates.sort(key=lambda x: x["value"], reverse=True)

    return {
        "resolution": resolution,
        "total_cells": len(aggregates),
        "total_mapped_facilities": sum(a["distinct_facilities_count"] for a in aggregates),
        "unresolved_locations_count": unresolved_count,
        "suppressed_approximate_count": suppressed_approximate_count,
        "aggregates": aggregates,
    }
