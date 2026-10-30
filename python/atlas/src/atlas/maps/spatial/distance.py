"""Geodesic Distance Calculations and Metric Spatial Predicates.

Enforces the CRITICAL UNIT RULE: Geographic degrees are NOT meters.
0.1 degrees is NOT 0.1 kilometers.
Calculates exact great-circle distance in meters using the Haversine equation.
"""

from __future__ import annotations

import math
from typing import Tuple

from atlas.maps.spatial.coordinates import validate_coordinates

EARTH_MEAN_RADIUS_METERS = 6371000.0


def calculate_distance_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculates great-circle distance between two geographic points in meters.

    Uses spherical law of cosines / Haversine formula over WGS84 mean earth radius.
    """
    v_lon1, v_lat1 = validate_coordinates(lon1, lat1)
    v_lon2, v_lat2 = validate_coordinates(lon2, lat2)

    phi1 = math.radians(v_lat1)
    phi2 = math.radians(v_lat2)
    delta_phi = math.radians(v_lat2 - v_lat1)
    delta_lambda = math.radians(v_lon2 - v_lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance_m = EARTH_MEAN_RADIUS_METERS * c
    return round(distance_m, 2)


def is_within_radius_meters(
    point_lon: float,
    point_lat: float,
    center_lon: float,
    center_lat: float,
    radius_meters: float,
) -> Tuple[bool, float]:
    """Returns (is_within, exact_distance_meters) for proximity queries."""
    if radius_meters <= 0:
        return False, 0.0

    dist = calculate_distance_meters(point_lon, point_lat, center_lon, center_lat)
    return dist <= radius_meters, dist

