"""H3 Cell Boundary Generation and GeoJSON Geometry Construction (Stage 131).

Converts H3 cell boundary vertices to GeoJSON compliant [lon, lat] coordinate rings.
Properly handles pentagons (5 vertices) and antimeridian wrapping (-180° / +180°).
"""

from __future__ import annotations

from typing import Any, Dict, List

import h3

from atlas.maps.analytics.h3.indexing import validate_cell_id


def cell_to_geojson_boundary(cell_id: str, split_antimeridian: bool = False) -> List[List[float]]:
    """Generates GeoJSON exterior ring coordinates for an H3 cell.

    H3 returns vertices as ((lat0, lng0), (lat1, lng1), ...).
    GeoJSON requires coordinates formatted as [[lng0, lat0], [lng1, lat1], ..., [lng0, lat0]].

    Args:
        cell_id: Valid H3 cell identifier.
        split_antimeridian: Whether to normalize antimeridian crossing coordinates.

    Returns:
        Closed ring list of [longitude, latitude] coordinates.
    """
    validate_cell_id(cell_id)
    raw_vertices = h3.cell_to_boundary(cell_id)

    coords: List[List[float]] = []
    has_positive = False
    has_negative = False

    for lat, lng in raw_vertices:
        lon_val = float(lng)
        lat_val = float(lat)
        if lon_val > 90.0:
            has_positive = True
        elif lon_val < -90.0:
            has_negative = True
        coords.append([lon_val, lat_val])

    # If the cell crosses the International Date Line (has vertices near +180 and -180),
    # normalize longitudes to prevent world-spanning artifact triangles.
    if has_positive and has_negative:
        # Wrap negative longitudes to > 180 or shift to standard range
        for pt in coords:
            if pt[0] < 0:
                pt[0] += 360.0

    # GeoJSON LinearRing must be closed (first coordinate equals last coordinate)
    if coords and coords[0] != coords[-1]:
        coords.append(coords[0])

    return coords


def cell_to_geojson_feature(cell_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Wraps an H3 cell boundary into a GeoJSON Feature dictionary."""
    ring = cell_to_geojson_boundary(cell_id)
    return {
        "type": "Feature",
        "id": cell_id,
        "geometry": {
            "type": "Polygon",
            "coordinates": [ring],
        },
        "properties": {
            **properties,
            "h3_cell_id": cell_id,
            "is_pentagon": bool(h3.is_pentagon(cell_id)),
            "resolution": int(h3.get_resolution(cell_id)),
        },
    }
