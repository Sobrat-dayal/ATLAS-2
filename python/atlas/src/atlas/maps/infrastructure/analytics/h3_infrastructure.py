"""H3 Geospatial Aggregation for Infrastructure Intelligence (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.indexing import lat_lng_to_cell
from atlas.maps.infrastructure.capacity.units import convert_to_canonical_unit
from atlas.maps.infrastructure.domain import (
    InfrastructureAsset,
    InfrastructureAssetType,
)
from atlas.maps.infrastructure.errors import EntitlementRevokedError


def aggregate_infrastructure_to_h3(
    assets: List[InfrastructureAsset],
    resolution: int = 7,
    revoked_sources: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Aggregate infrastructure assets to H3 hexagonal cells with distinct facility counting (Fixture I).

    Enforces:
    - Facility Count vs Unit Count distinction (no count inflation).
    - Safe capacity rollup per metric.
    - True geographic density per km².
    - Revocation of derived aggregates when source entitlement is revoked (Fixture N).
    """
    unit_types = {
        InfrastructureAssetType.GENERATING_UNIT,
        InfrastructureAssetType.BERTH,
        InfrastructureAssetType.RUNWAY,
        InfrastructureAssetType.PIPELINE_SEGMENT,
    }

    revoked = revoked_sources or set()
    cells_map: Dict[str, Dict[str, Any]] = {}

    for asset in assets:
        if asset.source_id in revoked:
            raise EntitlementRevokedError(asset.source_id)

        cell_id = lat_lng_to_cell(asset.latitude, asset.longitude, resolution)
        if cell_id not in cells_map:
            cells_map[cell_id] = {
                "cell_id": cell_id,
                "resolution": resolution,
                "facility_count": 0,
                "unit_count": 0,
                "total_records": 0,
                "capacities": {},
                "sectors": set(),
                "asset_ids": [],
            }

        data = cells_map[cell_id]
        data["total_records"] += 1
        data["sectors"].add(asset.sector.value)
        data["asset_ids"].append(asset.asset_id)

        # Separate facility and unit count (Fixture I)
        if asset.parent_asset_id is not None or asset.asset_type in unit_types:
            data["unit_count"] += 1
        else:
            data["facility_count"] += 1

        # Accumulate capacity
        for rec in asset.capacity_records:
            c_metric, val = convert_to_canonical_unit(rec.metric, rec.value)
            key = f"{c_metric.value}:{rec.basis.value}"
            data["capacities"][key] = data["capacities"].get(key, 0.0) + val

    results: List[Dict[str, Any]] = []
    for cell_id, data in cells_map.items():
        cell_area = get_cell_area_km2(cell_id)
        # Density is distinct facilities per square kilometer
        density = data["facility_count"] / cell_area if cell_area > 0 else 0.0

        results.append(
            {
                "cell_id": cell_id,
                "resolution": resolution,
                "facility_count": data["facility_count"],
                "unit_count": data["unit_count"],
                "total_records": data["total_records"],
                "density_per_km2": round(density, 4),
                "cell_area_km2": round(cell_area, 4),
                "capacities": data["capacities"],
                "sectors": sorted(list(data["sectors"])),
                "asset_ids": data["asset_ids"],
            }
        )

    return sorted(results, key=lambda c: c["facility_count"], reverse=True)

