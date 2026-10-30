"""Geographic Projection Transformations between WGS84 (EPSG:4326) and Web Mercator (EPSG:3857).

Performs exact mathematical transformations without lossy approximations.
"""

from __future__ import annotations

import math
from typing import Tuple

from atlas.maps.spatial.coordinates import (
    clamp_web_mercator_latitude,
    validate_coordinates,
)

EARTH_RADIUS_EQUATORIAL_METERS = 6378137.0  # WGS84 semi-major axis
ORIGIN_SHIFT = math.pi * EARTH_RADIUS_EQUATORIAL_METERS


def epsg4326_to_epsg3857(lon: float, lat: float) -> Tuple[float, float]:
    """Converts WGS84 geographic coordinates (longitude, latitude in degrees)

    to Web Mercator planar coordinates (x, y in meters).
    """
    valid_lon, valid_lat = validate_coordinates(lon, lat)
    clamped_lat = clamp_web_mercator_latitude(valid_lat)

    x = valid_lon * ORIGIN_SHIFT / 180.0
    y = math.log(math.tan((90.0 + clamped_lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * ORIGIN_SHIFT / 180.0

    return x, y


def epsg3857_to_epsg4326(x: float, y: float) -> Tuple[float, float]:
    """Converts Web Mercator planar coordinates (x, y in meters)

    to WGS84 geographic coordinates (longitude, latitude in degrees).
    """
    lon = (x / ORIGIN_SHIFT) * 180.0
    lat = (y / ORIGIN_SHIFT) * 180.0
    lat = 180.0 / math.pi * (2.0 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)

    # Clamping and precision formatting
    lon = max(-180.0, min(180.0, lon))
    lat = max(-90.0, min(90.0, lat))

    return lon, lat

