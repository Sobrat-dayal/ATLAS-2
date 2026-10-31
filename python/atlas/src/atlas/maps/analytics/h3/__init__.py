"""ATLAS H3 Hierarchical Spatial Analytics Engine (Stage 131)."""

from .boundaries import cell_to_geojson_boundary, cell_to_geojson_feature
from .cell_area import get_cell_area_km2
from .coverage import polygon_to_cells
from .density import compute_density
from .hierarchy import cell_to_children, cell_to_parent, rollup_child_aggregates
from .indexing import (
    cell_to_lat_lng,
    get_cell_resolution,
    is_pentagon,
    lat_lng_to_cell,
    validate_cell_id,
)

__all__ = [
    "cell_to_geojson_boundary",
    "cell_to_geojson_feature",
    "get_cell_area_km2",
    "polygon_to_cells",
    "compute_density",
    "cell_to_children",
    "cell_to_parent",
    "rollup_child_aggregates",
    "cell_to_lat_lng",
    "get_cell_resolution",
    "is_pentagon",
    "lat_lng_to_cell",
    "validate_cell_id",
]
