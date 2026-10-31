"""Company-to-Infrastructure Relationship and Asset Exposure Analytics (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List

from atlas.maps.infrastructure.capacity.units import convert_to_canonical_unit
from atlas.maps.infrastructure.domain import (
    EntityRole,
    InfrastructureAsset,
)


def compute_company_infrastructure_exposure(
    company_id: str,
    assets: List[InfrastructureAsset],
) -> Dict[str, Any]:
    """Analyze corporate infrastructure exposure distinguishing ownership, operations, and equity share (Fixture G)."""
    owned_assets: List[InfrastructureAsset] = []
    operated_assets: List[InfrastructureAsset] = []
    other_linked_assets: List[InfrastructureAsset] = []

    capacity_by_role: Dict[str, Dict[str, float]] = {
        EntityRole.OWNER.value: {},
        EntityRole.OPERATOR.value: {},
        "equity_weighted": {},
    }

    country_exposure: Dict[str, int] = {}
    sector_exposure: Dict[str, int] = {}

    for asset in assets:
        for link in asset.entity_links:
            if link.entity_id != company_id:
                continue

            # Role categorisation (Fixture G)
            if link.role == EntityRole.OWNER:
                owned_assets.append(asset)
            elif link.role == EntityRole.OPERATOR:
                operated_assets.append(asset)
            else:
                other_linked_assets.append(asset)

            country_exposure[asset.country] = country_exposure.get(asset.country, 0) + 1
            sector_exposure[asset.sector.value] = sector_exposure.get(asset.sector.value, 0) + 1

            # Capacity attribution
            ownership_pct = link.ownership_pct if link.ownership_pct is not None else (100.0 if link.role == EntityRole.OWNER else 0.0)

            for rec in asset.capacity_records:
                c_metric, val = convert_to_canonical_unit(rec.metric, rec.value)
                key = f"{c_metric.value}:{rec.basis.value}"

                role_bucket = capacity_by_role[link.role.value]
                role_bucket[key] = role_bucket.get(key, 0.0) + val

                # Equity weighted
                if ownership_pct > 0:
                    equity_val = val * (ownership_pct / 100.0)
                    capacity_by_role["equity_weighted"][key] = (
                        capacity_by_role["equity_weighted"].get(key, 0.0) + equity_val
                    )

    return {
        "company_id": company_id,
        "total_linked_assets": len(owned_assets) + len(operated_assets) + len(other_linked_assets),
        "owned_asset_count": len(owned_assets),
        "operated_asset_count": len(operated_assets),
        "other_linked_count": len(other_linked_assets),
        "sector_exposure": sector_exposure,
        "country_exposure": country_exposure,
        "capacity_by_role": capacity_by_role,
        "owned_assets": [a.to_dict() for a in owned_assets],
        "operated_assets": [a.to_dict() for a in operated_assets],
    }

