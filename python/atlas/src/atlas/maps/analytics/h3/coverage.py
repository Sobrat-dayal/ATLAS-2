"""H3 Polygon Covering and Spatial Boundary Resolution (Stage 131).

Converts geographic polygon bounds into covering H3 cells.
Explicitly clarifies centroid containment semantics vs exact geometric intersection.
"""

from __future__ import annotations

from typing import List, Set, Tuple

import h3

from atlas.maps.analytics.errors import InvalidH3ResolutionError


def polygon_to_cells(
    geojson_coordinates: List[List[float]],
    resolution: int,
) -> Set[str]:
    """Generates covering H3 cells for a GeoJSON polygon ring.

    Args:
        geojson_coordinates: List of [longitude, latitude] coordinates (GeoJSON order).
        resolution: H3 resolution level [0, 15].

    Returns:
        Set of H3 cell index strings whose centroids fall within the polygon.

    Note:
        Standard H3 polygon covering uses centroid containment semantics:
        A cell is included if its center point lies within the polygon boundary.
        This is an approximate covering and does not guarantee that 100% of the cell
        surface lies strictly inside the polygon.
    """
    if not (0 <= resolution <= 15):
        raise InvalidH3ResolutionError(resolution)

    if len(geojson_coordinates) < 3:
        return set()

    # Convert GeoJSON [lon, lat] to H3 (lat, lon) tuples
    lat_lng_ring: List[Tuple[float, float]] = []
    for pt in geojson_coordinates:
        lon = float(pt[0])
        lat = float(pt[1])
        lat_lng_ring.append((lat, lon))

    poly = h3.LatLngPoly(lat_lng_ring)
    cells = h3.polygon_to_cells(poly, resolution)
    return {str(c) for c in cells}
