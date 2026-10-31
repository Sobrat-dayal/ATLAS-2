"""Regional Physical Infrastructure Aggregation and Summaries (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List

from atlas.maps.infrastructure.capacity.units import convert_to_canonical_unit
from atlas.maps.infrastructure.domain import (
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureSector,
    InfrastructureStatus,
)


def compute_regional_infrastructure_summary(
    assets: List[InfrastructureAsset],
    region_name: str = "Target Region",
) -> Dict[str, Any]:
    """Compute institutional regional infrastructure profile."""
    unit_types = {
        InfrastructureAssetType.GENERATING_UNIT,
        InfrastructureAssetType.BERTH,
        InfrastructureAssetType.RUNWAY,
        InfrastructureAssetType.PIPELINE_SEGMENT,
    }

    sector_counts: Dict[str, int] = {s.value: 0 for s in InfrastructureSector}
    status_counts: Dict[str, int] = {s.value: 0 for s in InfrastructureStatus}
    capacity_by_sector: Dict[str, Dict[str, float]] = {s.value: {} for s in InfrastructureSector}
    source_manifest: Dict[str, int] = {}

    facility_count = 0
    unit_count = 0

    for asset in assets:
        sec = asset.sector.value
        stat = asset.status.value

        sector_counts[sec] = sector_counts.get(sec, 0) + 1
        status_counts[stat] = status_counts.get(stat, 0) + 1
        source_manifest[asset.source_id] = source_manifest.get(asset.source_id, 0) + 1

        if asset.parent_asset_id is not None or asset.asset_type in unit_types:
            unit_count += 1
        else:
            facility_count += 1

        for rec in asset.capacity_records:
            c_metric, val = convert_to_canonical_unit(rec.metric, rec.value)
            key = f"{c_metric.value}:{rec.basis.value}"
            sec_caps = capacity_by_sector[sec]
            sec_caps[key] = sec_caps.get(key, 0.0) + val

    return {
        "region_name": region_name,
        "total_assets": len(assets),
        "facility_count": facility_count,
        "unit_count": unit_count,
        "sector_breakdown": sector_counts,
        "status_breakdown": status_counts,
        "capacity_by_sector": capacity_by_sector,
        "source_coverage": {
            "distinct_sources": len(source_manifest),
            "source_record_counts": source_manifest,
        },
    }
