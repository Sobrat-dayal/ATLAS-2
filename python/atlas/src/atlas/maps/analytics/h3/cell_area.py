"""H3 Cell Area Calculation and Geodetic Area Measurement (Stage 131).

Calculates exact geodesic area for an H3 cell index using h3.cell_area(unit='km^2').
Recognizes that H3 cells are not equal-area across the Earth (due to icosahedron projection distortions).
"""

from __future__ import annotations

import h3

from atlas.maps.analytics.h3.indexing import validate_cell_id


def get_cell_area_km2(cell_id: str) -> float:
    """Calculates the exact geodetic surface area of an H3 cell in square kilometers (km²).

    Args:
        cell_id: Canonical H3 cell string.

    Returns:
        Surface area in square kilometers.
    """
    validate_cell_id(cell_id)
    area = h3.cell_area(cell_id, unit="km^2")
    return float(area)
