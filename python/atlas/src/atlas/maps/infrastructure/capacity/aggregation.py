"""Safe Hierarchical Capacity Aggregation for ATLAS Infrastructure (Stage 133)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from atlas.maps.infrastructure.capacity.units import (
    assert_compatible_dimensions,
    convert_to_canonical_unit,
)
from atlas.maps.infrastructure.domain import (
    CapacityBasis,
    CapacityMetric,
    InfrastructureAsset,
    InfrastructureCapacityRecord,
)
from atlas.maps.infrastructure.errors import IncompatibleCapacityUnitError


def aggregate_asset_capacities(
    records: List[InfrastructureCapacityRecord],
) -> Dict[Tuple[str, str], float]:
    """Aggregate capacity records safely, grouping strictly by (metric, basis).

    Enforces dimensional consistency and never blends disparate bases (e.g. Nameplate vs Net).
    """
    aggregated: Dict[Tuple[str, str], float] = {}

    for record in records:
        canonical_metric, normalized_value = convert_to_canonical_unit(record.metric, record.value)
        key = (canonical_metric.value, record.basis.value)
        aggregated[key] = aggregated.get(key, 0.0) + normalized_value

    return aggregated


def add_capacity_records(
    rec_a: InfrastructureCapacityRecord, rec_b: InfrastructureCapacityRecord
) -> InfrastructureCapacityRecord:
    """Add two capacity records with strict dimensional and basis verification."""
    assert_compatible_dimensions(rec_a.metric, rec_b.metric)

    if rec_a.basis != rec_b.basis:
        raise IncompatibleCapacityUnitError(
            f"{rec_a.metric.value} ({rec_a.basis.value})",
            f"{rec_b.metric.value} ({rec_b.basis.value})",
            "Cannot add capacities with different reporting bases.",
        )

    canonical_metric_a, val_a = convert_to_canonical_unit(rec_a.metric, rec_a.value)
    _, val_b = convert_to_canonical_unit(rec_b.metric, rec_b.value)

    return InfrastructureCapacityRecord(
        metric=canonical_metric_a,
        value=val_a + val_b,
        basis=rec_a.basis,
        unit_str=canonical_metric_a.value,
        reporting_year=max(filter(None, [rec_a.reporting_year, rec_b.reporting_year]), default=None),
        evidence_source="AGGREGATED",
    )


def rollup_plant_units_capacity(
    plant: InfrastructureAsset,
    units: List[InfrastructureAsset],
    metric: CapacityMetric = CapacityMetric.POWER_MW,
    basis: CapacityBasis = CapacityBasis.NAMEPLATE,
) -> Dict[str, Any]:
    """Roll up plant and generator unit capacities with duplicate prevention (Fixture A).

    Returns:
        {
            "plant_reported_capacity": Optional[float],
            "units_summed_capacity": float,
            "unit_count": int,
            "deduplicated_effective_capacity": float,
            "has_reconciliation_gap": bool
        }
    """
    plant_reported = None
    for rec in plant.capacity_records:
        if rec.metric == metric and rec.basis == basis:
            plant_reported = rec.value
            break

    unit_sum = 0.0
    for unit in units:
        for rec in unit.capacity_records:
            if rec.metric == metric and rec.basis == basis:
                unit_sum += rec.value

    # Deduplicated capacity: use plant reported if present; otherwise unit sum. Never add both!
    effective = plant_reported if plant_reported is not None else unit_sum
    gap = False
    if plant_reported is not None and abs(plant_reported - unit_sum) > 0.001 and len(units) > 0:
        gap = True

    return {
        "plant_reported_capacity": plant_reported,
        "units_summed_capacity": unit_sum,
        "unit_count": len(units),
        "deduplicated_effective_capacity": effective,
        "has_reconciliation_gap": gap,
    }


def aggregate_fleet_capacity(
    assets: List[InfrastructureAsset],
    metric: CapacityMetric,
    basis: CapacityBasis = CapacityBasis.NAMEPLATE,
) -> float:
    """Aggregate capacity across a fleet of assets while excluding child units to prevent double counting."""
    parent_ids = {a.parent_asset_id for a in assets if a.parent_asset_id is not None}
    total = 0.0

    for asset in assets:
        # If this is a child unit and its parent is also in the asset set, skip the unit to avoid double counting
        if asset.parent_asset_id is not None and any(a.asset_id == asset.parent_asset_id for a in assets):
            continue

        for rec in asset.capacity_records:
            if rec.basis == basis:
                c_metric, val = convert_to_canonical_unit(rec.metric, rec.value)
                c_target, _ = convert_to_canonical_unit(metric, 1.0)
                if c_metric == c_target:
                    total += val

    return total
