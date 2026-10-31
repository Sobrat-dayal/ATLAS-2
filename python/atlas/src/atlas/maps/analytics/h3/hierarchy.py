"""H3 Hierarchical Traversal and Mathematically Correct Aggregation (Stage 131).

Provides parent/child navigation and guarantees statistical correctness:
- Sums/Counts: Additive accumulation.
- Weighted Means: Total weighted sum / Total weight (rejects unweighted mean-of-means).
- Distinct Counts: Union of discrete identifiers (rejects double-counting).
"""

from __future__ import annotations

from typing import List, Optional, Set

import h3

from atlas.maps.analytics.domain import AtlasH3Aggregate, SpatialAggregationMethod
from atlas.maps.analytics.errors import InvalidH3ResolutionError
from atlas.maps.analytics.h3.cell_area import get_cell_area_km2
from atlas.maps.analytics.h3.density import compute_density
from atlas.maps.analytics.h3.indexing import get_cell_resolution, validate_cell_id


def cell_to_parent(cell_id: str, parent_resolution: int) -> str:
    """Returns the parent H3 cell at the requested coarser resolution."""
    validate_cell_id(cell_id)
    current_res = get_cell_resolution(cell_id)
    if parent_resolution > current_res:
        raise InvalidH3ResolutionError(
            parent_resolution,
            min_res=0,
            max_res=current_res,
        )
    return str(h3.cell_to_parent(cell_id, parent_resolution))


def cell_to_children(cell_id: str, child_resolution: int) -> List[str]:
    """Returns all child H3 cells at the requested finer resolution."""
    validate_cell_id(cell_id)
    current_res = get_cell_resolution(cell_id)
    if child_resolution < current_res:
        raise InvalidH3ResolutionError(
            child_resolution,
            min_res=current_res,
            max_res=15,
        )
    return [str(c) for c in h3.cell_to_children(cell_id, child_resolution)]


def rollup_child_aggregates(
    parent_cell_id: str,
    child_aggregates: List[AtlasH3Aggregate],
    aggregation_method: SpatialAggregationMethod,
    metric_id: str,
    unit: str = "",
    min_contributors: int = 5,
    distinct_entity_ids: Optional[Set[str]] = None,
) -> AtlasH3Aggregate:
    """Rolls up child cell aggregates into a parent cell aggregate with mathematical correctness.

    Ensures:
    - Count: Sum of child record counts.
    - Sum: Sum of child sum values.
    - Mean / Weighted Mean:
        Parent Mean = sum(child_weight_i * child_value_i) / sum(child_weight_i)
        Where child_weight is non_null_count or valid_weight_sum.
        NEVER takes average of child averages without weight normalization.
    - Distinct Count: Size of distinct entity union (if provided).
    - Density: Final metric / parent cell area (km²).
    """
    validate_cell_id(parent_cell_id)
    parent_res = get_cell_resolution(parent_cell_id)
    parent_area = get_cell_area_km2(parent_cell_id)

    total_records = sum(c.record_count for c in child_aggregates)
    total_non_null = sum(c.non_null_count for c in child_aggregates)

    final_value = 0.0
    final_weight_sum: Optional[float] = None

    if aggregation_method == SpatialAggregationMethod.COUNT:
        final_value = float(total_records)

    elif aggregation_method == SpatialAggregationMethod.SUM:
        final_value = sum(c.value for c in child_aggregates)

    elif aggregation_method == SpatialAggregationMethod.MEAN:
        # Correct calculation: sum(c.value * c.non_null_count) / sum(c.non_null_count)
        if total_non_null > 0:
            weighted_sum = sum(c.value * c.non_null_count for c in child_aggregates)
            final_value = weighted_sum / total_non_null
        else:
            final_value = 0.0

    elif aggregation_method == SpatialAggregationMethod.WEIGHTED_MEAN:
        # Child aggregates must have valid_weight_sum
        total_weight = sum((c.valid_weight_sum or c.non_null_count) for c in child_aggregates)
        if total_weight > 0:
            weighted_sum = sum(
                (c.value * (c.valid_weight_sum or c.non_null_count)) for c in child_aggregates
            )
            final_value = weighted_sum / total_weight
            final_weight_sum = total_weight
        else:
            final_value = 0.0

    elif aggregation_method == SpatialAggregationMethod.DISTINCT_COUNT:
        if distinct_entity_ids is not None:
            final_value = float(len(distinct_entity_ids))
        else:
            # Fallback if raw sets not available: lower bound max or sum if disjoint
            final_value = float(
                max((c.distinct_count or 0) for c in child_aggregates) if child_aggregates else 0
            )

    elif aggregation_method == SpatialAggregationMethod.DENSITY:
        final_value = compute_density(float(total_records), parent_area)

    # Calculate density
    density_val = compute_density(final_value, parent_area)

    # Privacy suppression check
    distinct_cnt = len(distinct_entity_ids) if distinct_entity_ids is not None else total_non_null
    is_suppressed = distinct_cnt < min_contributors

    return AtlasH3Aggregate(
        h3_cell_id=parent_cell_id,
        h3_resolution=parent_res,
        metric_id=metric_id,
        aggregation_method=aggregation_method,
        value=final_value,
        record_count=total_records,
        non_null_count=total_non_null,
        distinct_count=distinct_cnt,
        valid_weight_sum=final_weight_sum,
        cell_area_km2=parent_area,
        density=density_val,
        unit=unit,
        is_suppressed=is_suppressed,
    )
