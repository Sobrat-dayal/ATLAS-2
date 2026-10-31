"""Live Geospatial Observation H3 Aggregation (Stage 134).

Aggregates high-volume live observations (aircraft, vessels, satellites, weather,
thermal detections) into H3 hexagonal indexing.
Reports both total observation count and distinct unique tracked entity count.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional
import h3

from ..domain import AtlasGeoObservation


def aggregate_live_observations_to_h3(
    observations: List[AtlasGeoObservation],
    resolution: int = 4,
) -> List[Dict[str, Any]]:
    """Aggregate live observations into H3 hexagonal cells.

    Args:
        observations: List of AtlasGeoObservation records.
        resolution: H3 resolution level (typically 3 to 7).

    Returns:
        List of dicts containing h3_cell, resolution, raw_observation_count,
        distinct_entity_count, dominant_category, categories_breakdown, and centroid.
    """
    if resolution < 0 or resolution > 15:
        raise ValueError(f"H3 resolution must be between 0 and 15, got {resolution}")

    cell_groups: Dict[str, List[AtlasGeoObservation]] = defaultdict(list)
    for obs in observations:
        try:
            cell_id = h3.latlng_to_cell(obs.latitude, obs.longitude, resolution)
            cell_groups[cell_id].append(obs)
        except Exception:
            continue

    aggregates: List[Dict[str, Any]] = []
    for cell_id, obs_list in cell_groups.items():
        distinct_entities = {obs.entity_id for obs in obs_list}
        cat_counts: Dict[str, int] = defaultdict(int)
        for obs in obs_list:
            cat_name = obs.category.value if hasattr(obs.category, "value") else str(obs.category)
            cat_counts[cat_name] += 1

        # Dominant category
        dom_cat = max(cat_counts.items(), key=lambda x: x[1])[0]

        # Centroid
        lat_c, lon_c = h3.cell_to_latlng(cell_id)

        aggregates.append(
            {
                "h3_cell": cell_id,
                "resolution": resolution,
                "raw_observation_count": len(obs_list),
                "distinct_entity_count": len(distinct_entities),
                "dominant_category": dom_cat,
                "categories_breakdown": dict(cat_counts),
                "centroid": [round(lon_c, 5), round(lat_c, 5)],
            }
        )

    aggregates.sort(key=lambda a: a["raw_observation_count"], reverse=True)
    return aggregates
