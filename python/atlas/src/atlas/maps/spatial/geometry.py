"""Geometry Validation, Self-Intersection Detection, and Topological Tests.

Supports Point, LineString, Polygon, MultiPoint, MultiLineString, and MultiPolygon.
Strictly rejects invalid or self-intersecting geometries without silent corruption.
"""

from __future__ import annotations

from typing import Any, Sequence

from atlas.maps.domain import GeoBoundingBox, GeometryType
from atlas.maps.errors import MapDatasetGeometryInvalidError
from atlas.maps.spatial.coordinates import validate_coordinates


def _ccw(a: Sequence[float], b: Sequence[float], c: Sequence[float]) -> float:
    """Returns counter-clockwise orientation cross product."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _segments_intersect(
    p1: Sequence[float], p2: Sequence[float], p3: Sequence[float], p4: Sequence[float]
) -> bool:
    """Tests if line segment p1-p2 strictly intersects segment p3-p4."""
    # Fast bounding box rejection
    if max(p1[0], p2[0]) < min(p3[0], p4[0]) or max(p3[0], p4[0]) < min(p1[0], p2[0]):
        return False
    if max(p1[1], p2[1]) < min(p3[1], p4[1]) or max(p3[1], p4[1]) < min(p1[1], p2[1]):
        return False

    d1 = _ccw(p3, p4, p1)
    d2 = _ccw(p3, p4, p2)
    d3 = _ccw(p1, p2, p3)
    d4 = _ccw(p1, p2, p4)

    # Strictly opposite signs indicates crossing
    return ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and (
        (d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)
    )


def validate_ring(ring: Sequence[Sequence[float]], dataset_id: str = "dataset") -> None:
    """Validates a polygon linear ring:

    - Minimum 4 coordinates (3 distinct vertices + closing point).
    - Closed: ring[0] == ring[-1].
    - Coordinate bounds.
    - No self-intersecting non-adjacent edges.
    """
    if len(ring) < 4:
        raise MapDatasetGeometryInvalidError(
            dataset_id, f"Polygon ring must contain at least 4 coordinates, got {len(ring)}"
        )

    # Validate each coordinate
    for coord in ring:
        validate_coordinates(coord[0], coord[1])

    # Check closure
    first = ring[0]
    last = ring[-1]
    if abs(first[0] - last[0]) > 1e-9 or abs(first[1] - last[1]) > 1e-9:
        raise MapDatasetGeometryInvalidError(
            dataset_id,
            f"Polygon ring is not closed: start [{first[0]}, {first[1]}] != end [{last[0]}, {last[1]}]",
        )

    # Check self-intersection among non-adjacent edges
    n = len(ring) - 1  # number of distinct edges
    for i in range(n):
        p1 = ring[i]
        p2 = ring[i + 1]
        for j in range(i + 2, n):
            # Skip adjacent edge at wrap-around
            if i == 0 and j == n - 1:
                continue
            p3 = ring[j]
            p4 = ring[j + 1]
            if _segments_intersect(p1, p2, p3, p4):
                raise MapDatasetGeometryInvalidError(
                    dataset_id,
                    f"Self-intersecting polygon detected: edge {i} intersects edge {j}",
                )


def validate_geometry(
    geometry_type: GeometryType, coordinates: Any, dataset_id: str = "dataset"
) -> GeoBoundingBox:
    """Validates geometry coordinates according to its GeometryType.

    Returns the computed bounding box.
    """
    if geometry_type == GeometryType.POINT:
        if not isinstance(coordinates, (list, tuple)) or len(coordinates) < 2:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "Point requires [lon, lat] coordinates"
            )
        lon, lat = validate_coordinates(coordinates[0], coordinates[1])
        return GeoBoundingBox(west=lon, south=lat, east=lon, north=lat)

    elif geometry_type == GeometryType.MULTIPOINT:
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "MultiPoint requires non-empty list of [lon, lat]"
            )
        lons, lats = [], []
        for pt in coordinates:
            lon, lat = validate_coordinates(pt[0], pt[1])
            lons.append(lon)
            lats.append(lat)
        return GeoBoundingBox(west=min(lons), south=min(lats), east=max(lons), north=max(lats))

    elif geometry_type == GeometryType.LINESTRING:
        if not isinstance(coordinates, list) or len(coordinates) < 2:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "LineString requires at least 2 points"
            )
        lons, lats = [], []
        for pt in coordinates:
            lon, lat = validate_coordinates(pt[0], pt[1])
            lons.append(lon)
            lats.append(lat)
        return GeoBoundingBox(west=min(lons), south=min(lats), east=max(lons), north=max(lats))

    elif geometry_type == GeometryType.MULTILINESTRING:
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "MultiLineString requires non-empty list of lines"
            )
        lons, lats = [], []
        for line in coordinates:
            if not isinstance(line, list) or len(line) < 2:
                raise MapDatasetGeometryInvalidError(
                    dataset_id, "Line in MultiLineString requires at least 2 points"
                )
            for pt in line:
                lon, lat = validate_coordinates(pt[0], pt[1])
                lons.append(lon)
                lats.append(lat)
        return GeoBoundingBox(west=min(lons), south=min(lats), east=max(lons), north=max(lats))

    elif geometry_type == GeometryType.POLYGON:
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "Polygon requires at least an exterior ring"
            )
        lons, lats = [], []
        for ring in coordinates:
            validate_ring(ring, dataset_id=dataset_id)
            for pt in ring:
                lons.append(pt[0])
                lats.append(pt[1])
        return GeoBoundingBox(west=min(lons), south=min(lats), east=max(lons), north=max(lats))

    elif geometry_type == GeometryType.MULTIPOLYGON:
        if not isinstance(coordinates, list) or len(coordinates) == 0:
            raise MapDatasetGeometryInvalidError(
                dataset_id, "MultiPolygon requires at least one polygon"
            )
        lons, lats = [], []
        for poly in coordinates:
            for ring in poly:
                validate_ring(ring, dataset_id=dataset_id)
                for pt in ring:
                    lons.append(pt[0])
                    lats.append(pt[1])
        return GeoBoundingBox(west=min(lons), south=min(lats), east=max(lons), north=max(lats))

    raise MapDatasetGeometryInvalidError(dataset_id, f"Unsupported geometry type: {geometry_type}")


def point_in_polygon(lon: float, lat: float, exterior_ring: Sequence[Sequence[float]]) -> bool:
    """Ray casting algorithm to test if (lon, lat) is inside a polygon ring."""
    inside = False
    n = len(exterior_ring)
    if n < 4:
        return False

    j = n - 1
    for i in range(n):
        xi, yi = exterior_ring[i][0], exterior_ring[i][1]
        xj, yj = exterior_ring[j][0], exterior_ring[j][1]

        intersect = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi
        )
        if intersect:
            inside = not inside
        j = i

    return inside
