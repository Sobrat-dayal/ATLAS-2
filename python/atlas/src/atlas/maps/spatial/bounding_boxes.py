"""Bounding Box Calculations and Antimeridian Normalization.

Handles standard viewports as well as viewports crossing the International Date Line (180°).
"""

from __future__ import annotations

from typing import List, Sequence

from atlas.maps.domain import GeoBoundingBox
from atlas.maps.errors import MapBoundsInvalidError


def validate_bounding_box(west: float, south: float, east: float, north: float) -> GeoBoundingBox:
    """Validates bounding box coordinates.

    Supports wrapped viewports where west > east across the antimeridian.
    """
    if south < -90.0 or south > 90.0 or north < -90.0 or north > 90.0:
        raise MapBoundsInvalidError(
            west, south, east, north, "South and north latitudes must be between -90.0 and 90.0"
        )

    if south > north:
        raise MapBoundsInvalidError(
            west,
            south,
            east,
            north,
            f"South latitude ({south}) cannot be greater than north latitude ({north})",
        )

    if west < -180.0 or west > 180.0 or east < -180.0 or east > 180.0:
        raise MapBoundsInvalidError(
            west, south, east, north, "West and east longitudes must be between -180.0 and 180.0"
        )

    return GeoBoundingBox(
        west=float(west), south=float(south), east=float(east), north=float(north)
    )


def split_antimeridian_bbox(bbox: GeoBoundingBox) -> List[GeoBoundingBox]:
    """If bounding box crosses the 180° antimeridian (west > east), splits it into

    two normalized bounding boxes: [west, south, 180.0, north] and [-180.0, south, east, north].
    Otherwise returns a single bounding box in a list.
    """
    if not bbox.crosses_antimeridian():
        return [bbox]

    return [
        GeoBoundingBox(west=bbox.west, south=bbox.south, east=180.0, north=bbox.north),
        GeoBoundingBox(west=-180.0, south=bbox.south, east=bbox.east, north=bbox.north),
    ]


def point_in_bbox(lon: float, lat: float, bbox: GeoBoundingBox) -> bool:
    """Checks if a geographic point (lon, lat) falls inside the bounding box,

    correctly accounting for antimeridian crossing.
    """
    if lat < bbox.south or lat > bbox.north:
        return False

    if bbox.crosses_antimeridian():
        # Point is inside if lon >= west (eastern hemisphere segment) OR lon <= east (western hemisphere segment)
        return lon >= bbox.west or lon <= bbox.east
    else:
        return bbox.west <= lon <= bbox.east


def bboxes_intersect(a: GeoBoundingBox, b: GeoBoundingBox) -> bool:
    """Checks if two bounding boxes intersect, accounting for antimeridian crossing."""
    boxes_a = split_antimeridian_bbox(a)
    boxes_b = split_antimeridian_bbox(b)

    for sub_a in boxes_a:
        for sub_b in boxes_b:
            if not (
                sub_a.east < sub_b.west
                or sub_a.west > sub_b.east
                or sub_a.north < sub_b.south
                or sub_a.south > sub_b.north
            ):
                return True
    return False


def compute_envelope(coordinates: Sequence[Sequence[float]]) -> GeoBoundingBox:
    """Computes minimum bounding box enclosing a list of [lon, lat] coordinates."""
    if not coordinates:
        return GeoBoundingBox(west=-180.0, south=-90.0, east=180.0, north=90.0)

    lons = [float(c[0]) for c in coordinates]
    lats = [float(c[1]) for c in coordinates]

    west = max(-180.0, min(lons))
    east = min(180.0, max(lons))
    south = max(-90.0, min(lats))
    north = min(90.0, max(lats))

    return GeoBoundingBox(west=west, south=south, east=east, north=north)
