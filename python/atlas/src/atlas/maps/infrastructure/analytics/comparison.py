"""Side-by-Side Infrastructure Asset Comparison Engine (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List

from atlas.maps.infrastructure.domain import (
    CapacityMetric,
    InfrastructureAsset,
)


def compare_infrastructure_assets(
    assets: List[InfrastructureAsset],
) -> Dict[str, Any]:
    """Compare multiple infrastructure assets preserving metric bases and precision (Fixtures F, H, K)."""
    comparison_cards: List[Dict[str, Any]] = []

    for asset in assets:
        capacities = []
        for rec in asset.capacity_records:
            capacities.append(
                {
                    "metric": rec.metric.value,
                    "value": rec.value,
                    "basis": rec.basis.value,
                    "unit": rec.unit_str,
                    "year": rec.reporting_year,
                }
            )

        card = {
            "asset_id": asset.asset_id,
            "name": asset.name,
            "sector": asset.sector.value,
            "asset_type": asset.asset_type.value,
            "country": asset.country,
            "region": asset.region,
            "status": asset.status.value,
            "precision": asset.precision.value,
            "is_approximate_route": asset.is_approximate_route,
            "capacities": capacities if capacities else [{"metric": "throughput", "value": None, "display": "Not available"}],
            "entity_links": [
                {
                    "entity_id": l.entity_id,
                    "entity_name": l.entity_name,
                    "role": l.role.value,
                    "ownership_pct": l.ownership_pct,
                }
                for l in asset.entity_links
            ],
            "source_id": asset.source_id,
        }
        comparison_cards.append(card)

    # Check for basis differences across assets sharing the same metric (Fixture F)
    basis_discrepancies: List[Dict[str, Any]] = []
    if len(assets) >= 2:
        for metric in CapacityMetric:
            bases_found = set()
            for asset in assets:
                for rec in asset.capacity_records:
                    if rec.metric == metric:
                        bases_found.add(rec.basis.value)
            if len(bases_found) > 1:
                basis_discrepancies.append(
                    {
                        "metric": metric.value,
                        "differing_bases": sorted(list(bases_found)),
                        "warning": "Assets report different capacity bases (e.g. Nameplate vs Net). Direct numeric ranking without adjustment is invalid.",
                    }
                )

    return {
        "asset_count": len(assets),
        "assets": comparison_cards,
        "basis_discrepancies": basis_discrepancies,
    }
