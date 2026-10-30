"""ATLAS Spatial Mathematics and Geometry Module."""

from atlas.maps.spatial.bounding_boxes import (
    bboxes_intersect,
    compute_envelope,
    point_in_bbox,
    split_antimeridian_bbox,
    validate_bounding_box,
)
from atlas.maps.spatial.coordinates import (
    WEB_MERCATOR_MAX_LATITUDE,
    WEB_MERCATOR_MIN_LATITUDE,
    clamp_web_mercator_latitude,
    parse_coordinate_pair,
    validate_coordinates,
)
from atlas.maps.spatial.distance import (
    EARTH_MEAN_RADIUS_METERS,
    calculate_distance_meters,
    is_within_radius_meters,
)
from atlas.maps.spatial.geometry import (
    point_in_polygon,
    validate_geometry,
    validate_ring,
)
from atlas.maps.spatial.projections import (
    epsg3857_to_epsg4326,
    epsg4326_to_epsg3857,
)

__all__ = [
    "WEB_MERCATOR_MAX_LATITUDE",
    "WEB_MERCATOR_MIN_LATITUDE",
    "validate_coordinates",
    "clamp_web_mercator_latitude",
    "parse_coordinate_pair",
    "epsg4326_to_epsg3857",
    "epsg3857_to_epsg4326",
    "EARTH_MEAN_RADIUS_METERS",
    "calculate_distance_meters",
    "is_within_radius_meters",
    "validate_bounding_box",
    "split_antimeridian_bbox",
    "point_in_bbox",
    "bboxes_intersect",
    "compute_envelope",
    "validate_ring",
    "validate_geometry",
    "point_in_polygon",
]
