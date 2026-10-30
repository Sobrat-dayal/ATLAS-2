"""Coordinate Validation and Normalization for WGS84 and Web Mercator.

Enforces strict [longitude, latitude] semantics and bounds checks.
Prevents silent coordinate reversal mistakes.
"""

from __future__ import annotations

from typing import Sequence, Tuple

from atlas.maps.errors import MapCoordinatesInvalidError

WEB_MERCATOR_MAX_LATITUDE = 85.0511287798066
WEB_MERCATOR_MIN_LATITUDE = -85.0511287798066


def validate_coordinates(lon: float, lat: float) -> Tuple[float, float]:
    """Validates that longitude is in [-180, 180] and latitude is in [-90, 90].

    Raises MapCoordinatesInvalidError if invalid or detected reversed.
    Returns normalized (lon, lat).
    """
    if not isinstance(lon, (int, float)) or not isinstance(lat, (int, float)):
        raise MapCoordinatesInvalidError(
            float(lon) if isinstance(lon, (int, float)) else 0.0,
            float(lat) if isinstance(lat, (int, float)) else 0.0,
            "Coordinates must be numeric floating-point values",
        )

    # Check for possible coordinate reversal mistake (e.g. lat > 90 but <= 180)
    if abs(lat) > 90.0 and abs(lon) <= 90.0:
        raise MapCoordinatesInvalidError(
            lon,
            lat,
            f"Detected reversed latitude/longitude coordinates: lat={lat} exceeds [-90, 90] bounds",
        )

    if lon < -180.0 or lon > 180.0:
        raise MapCoordinatesInvalidError(
            lon, lat, "Longitude must be between -180.0 and 180.0 degrees"
        )

    if lat < -90.0 or lat > 90.0:
        raise MapCoordinatesInvalidError(
            lon, lat, "Latitude must be between -90.0 and 90.0 degrees"
        )

    return float(lon), float(lat)


def clamp_web_mercator_latitude(lat: float) -> float:
    """Clamps latitude to valid Web Mercator projection limits."""
    return max(WEB_MERCATOR_MIN_LATITUDE, min(WEB_MERCATOR_MAX_LATITUDE, lat))


def parse_coordinate_pair(pair: Sequence[float]) -> Tuple[float, float]:
    """Parses a 2-element sequence as [longitude, latitude]."""
    if len(pair) < 2:
        raise MapCoordinatesInvalidError(
            0.0, 0.0, "Coordinate pair must contain at least 2 numbers [lon, lat]"
        )
    return validate_coordinates(float(pair[0]), float(pair[1]))
