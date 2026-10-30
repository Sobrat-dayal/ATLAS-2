"""Vector Tile Coordinate Mathematics and Tile Envelope Computation.

Converts standard XYZ tile coordinates to Web Mercator and WGS84 bounding envelopes.
Implements the equivalent of PostGIS ST_TileEnvelope(z, x, y).
"""

from __future__ import annotations

from typing import Tuple

from atlas.maps.domain import GeoBoundingBox
from atlas.maps.errors import MapTileCoordinatesInvalidError
from atlas.maps.spatial.projections import (
    ORIGIN_SHIFT,
    epsg3857_to_epsg4326,
)

MIN_ZOOM = 0
MAX_ZOOM = 22


def validate_tile_xyz(z: int, x: int, y: int) -> Tuple[int, int, int]:
    """Validates zoom level z and tile indices x, y.

    Raises MapTileCoordinatesInvalidError if out of bounds.
    """
    if not isinstance(z, int) or not isinstance(x, int) or not isinstance(y, int):
        raise MapTileCoordinatesInvalidError(z, x, y, "Tile coordinates must be integers")

    if z < MIN_ZOOM or z > MAX_ZOOM:
        raise MapTileCoordinatesInvalidError(
            z, x, y, f"Zoom level z={z} outside allowed range [{MIN_ZOOM}, {MAX_ZOOM}]"
        )

    max_idx = (1 << z) - 1
    if x < 0 or x > max_idx:
        raise MapTileCoordinatesInvalidError(
            z, x, y, f"Tile x={x} outside allowed range [0, {max_idx}] for zoom {z}"
        )

    if y < 0 or y > max_idx:
        raise MapTileCoordinatesInvalidError(
            z, x, y, f"Tile y={y} outside allowed range [0, {max_idx}] for zoom {z}"
        )

    return z, x, y


def tile_bounds_epsg3857(z: int, x: int, y: int) -> Tuple[float, float, float, float]:
    """Computes tile envelope in EPSG:3857 meters: (min_x, min_y, max_x, max_y).

    Matches PostGIS ST_TileEnvelope(z, x, y).
    """
    validate_tile_xyz(z, x, y)
    num_tiles = 1 << z
    tile_span = (2.0 * ORIGIN_SHIFT) / num_tiles

    min_x = -ORIGIN_SHIFT + (x * tile_span)
    max_x = -ORIGIN_SHIFT + ((x + 1) * tile_span)
    max_y = ORIGIN_SHIFT - (y * tile_span)
    min_y = ORIGIN_SHIFT - ((y + 1) * tile_span)

    return min_x, min_y, max_x, max_y


def tile_bounds_epsg4326(z: int, x: int, y: int) -> GeoBoundingBox:
    """Computes tile envelope in WGS84 degrees: [west, south, east, north]."""
    min_x, min_y, max_x, max_y = tile_bounds_epsg3857(z, x, y)
    west, south = epsg3857_to_epsg4326(min_x, min_y)
    east, north = epsg3857_to_epsg4326(max_x, max_y)
    return GeoBoundingBox(west=west, south=south, east=east, north=north)
