"""H3 Spatial Density Calculations and Area Normalization (Stage 131).

Normalizes observation counts or metric totals by actual cell geodesic surface area (km²).
"""

from __future__ import annotations


def compute_density(value: float, cell_area_km2: float) -> float:
    """Computes area-normalized density (value / km²).

    Args:
        value: Numeric aggregate (e.g. record count, monetary sum).
        cell_area_km2: Surface area of the cell in square kilometers.

    Returns:
        Density in units/km². Returns 0.0 if area <= 0.
    """
    if cell_area_km2 <= 0.0:
        return 0.0
    return float(value) / float(cell_area_km2)
