"""Infrastructure Asset Hierarchy and Duplicate Counting Prevention (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Set

from atlas.maps.infrastructure.domain import (
    InfrastructureAsset,
    InfrastructureAssetType,
    InfrastructureSector,
)


def count_distinct_infrastructure_assets(assets: List[InfrastructureAsset]) -> Dict[str, int]:
    """Count distinct facilities/plants versus operational sub-units without inflation (Fixture I).

    Returns:
        {
            "facility_count": int,  # Parent facilities / standalone assets
            "unit_count": int,      # Child generating units or sub-components
            "total_records": int
        }
    """
    unit_types = {
        InfrastructureAssetType.GENERATING_UNIT,
        InfrastructureAssetType.BERTH,
        InfrastructureAssetType.RUNWAY,
        InfrastructureAssetType.PIPELINE_SEGMENT,
    }

    facilities = 0
    units = 0

    for asset in assets:
        if asset.parent_asset_id is not None or asset.asset_type in unit_types:
            units += 1
        else:
            facilities += 1

    return {
        "facility_count": facilities,
        "unit_count": units,
        "total_records": len(assets),
    }


def resolve_asset_hierarchy(
    parent: InfrastructureAsset,
    all_assets: List[InfrastructureAsset],
) -> Dict[str, Any]:
    """Resolve full parent-child hierarchy tree for an asset."""
    children = [a for a in all_assets if a.parent_asset_id == parent.asset_id]
    return {
        "parent": parent,
        "children": children,
        "child_count": len(children),
    }
