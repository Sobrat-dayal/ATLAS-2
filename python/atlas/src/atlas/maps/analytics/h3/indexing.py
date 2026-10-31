"""H3 Indexing and Coordinate Conversion (Stage 131).

Wraps H3 v4 core indexing functions with validation, type enforcement,
and lossless string preservation.
"""

from __future__ import annotations

from typing import Tuple

import h3

from atlas.maps.analytics.errors import InvalidH3CellError, InvalidH3ResolutionError


def lat_lng_to_cell(latitude: float, longitude: float, resolution: int) -> str:
    """Assigns WGS84 geographic coordinate to an H3 hexagon cell index string.

    Args:
        latitude: Latitude in degrees [-90.0, 90.0].
        longitude: Longitude in degrees [-180.0, 180.0].
        resolution: H3 resolution level [0, 15].

    Returns:
        Lossless canonical H3 cell index string (e.g. '87195da49ffffff').
    """
    if not (0 <= resolution <= 15):
        raise InvalidH3ResolutionError(resolution)

    # Validate coordinate bounds
    if not (-90.0 <= latitude <= 90.0) or not (-180.0 <= longitude <= 180.0):
        raise ValueError(f"Coordinates ({latitude}, {longitude}) are out of WGS84 bounds.")

    cell = h3.latlng_to_cell(latitude, longitude, resolution)
    return str(cell)


def cell_to_lat_lng(cell_id: str) -> Tuple[float, float]:
    """Returns the centroid latitude and longitude (lat, lng) for an H3 cell.

    Args:
        cell_id: Canonical H3 cell index string.

    Returns:
        Tuple of (latitude, longitude) in degrees.
    """
    validate_cell_id(cell_id)
    lat, lng = h3.cell_to_latlng(cell_id)
    return float(lat), float(lng)


def validate_cell_id(cell_id: str) -> None:
    """Validates that a string is a valid H3 cell index.

    Raises:
        InvalidH3CellError: If string is malformed or invalid.
    """
    if not cell_id or not isinstance(cell_id, str):
        raise InvalidH3CellError(str(cell_id), "Must be a non-empty string")

    try:
        if not h3.is_valid_cell(cell_id):
            raise InvalidH3CellError(cell_id, "h3.is_valid_cell returned False")
    except Exception as exc:
        raise InvalidH3CellError(cell_id, str(exc)) from exc


def get_cell_resolution(cell_id: str) -> int:
    """Returns the resolution level [0, 15] of an H3 cell."""
    validate_cell_id(cell_id)
    return int(h3.get_resolution(cell_id))


def is_pentagon(cell_id: str) -> bool:
    """Returns True if the cell is one of the 12 pentagonal cells at its resolution."""
    validate_cell_id(cell_id)
    return bool(h3.is_pentagon(cell_id))
