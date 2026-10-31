"""Geographic location models and coordinate validation (Stage 132)."""

from __future__ import annotations

import math
from typing import Any

from atlas.maps.corporate.domain import GeographicPrecisionClass
from atlas.maps.corporate.errors import InvalidFacilityGeometryError, InvalidPrecisionClassError


def validate_coordinates(longitude: float | None, latitude: float | None) -> None:
    """Validate that coordinates adhere strictly to WGS84 EPSG:4326 boundaries."""
    if longitude is None or latitude is None:
        return

    if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
        raise InvalidFacilityGeometryError("Coordinates must be numeric floats", coordinates=(longitude, latitude))

    if math.isnan(longitude) or math.isnan(latitude) or math.isinf(longitude) or math.isinf(latitude):
        raise InvalidFacilityGeometryError("Coordinates cannot be NaN or Infinite", coordinates=(longitude, latitude))

    if not (-180.0 <= longitude <= 180.0):
        raise InvalidFacilityGeometryError(f"Longitude {longitude} out of bounds [-180, 180]", coordinates=(longitude, latitude))

    if not (-90.0 <= latitude <= 90.0):
        raise InvalidFacilityGeometryError(f"Latitude {latitude} out of bounds [-90, 90]", coordinates=(longitude, latitude))


def validate_polygon_geometry(coordinates: list[Any]) -> None:
    """Validate polygon ring structure for site boundaries."""
    if not isinstance(coordinates, list) or len(coordinates) == 0:
        raise InvalidFacilityGeometryError("Polygon coordinates must be non-empty list of rings")

    exterior_ring = coordinates[0]
    if not isinstance(exterior_ring, list) or len(exterior_ring) < 4:
        raise InvalidFacilityGeometryError("Polygon exterior ring must contain at least 4 positions")

    # First and last must match (closed polygon)
    if exterior_ring[0] != exterior_ring[-1]:
        raise InvalidFacilityGeometryError("Polygon ring must be closed (first and last coordinate must be equal)")

    for pt in exterior_ring:
        if not isinstance(pt, list) or len(pt) < 2:
            raise InvalidFacilityGeometryError("Polygon vertex must be [longitude, latitude] pair")
        validate_coordinates(pt[0], pt[1])


def enforce_precision_rules(
    precision: GeographicPrecisionClass,
    has_street_address: bool,
    has_exact_site_point: bool,
    is_city_only: bool,
) -> GeographicPrecisionClass:
    """Ensure precision classification is truthful and not artificially elevated.

    Guarantees:
    - If only city/locality is provided in source, precision cannot be VERIFIED_SITE_POINT.
    - Site point requires verified building/campus location.
    """
    if is_city_only and precision in (
        GeographicPrecisionClass.VERIFIED_SITE_POINT,
        GeographicPrecisionClass.VERIFIED_SITE_POLYGON,
        GeographicPrecisionClass.VERIFIED_STREET_ADDRESS,
    ):
        raise InvalidPrecisionClassError(
            precision.value,
            "Cannot assign site-level precision when only city/locality is documented.",
        )

    if precision == GeographicPrecisionClass.VERIFIED_SITE_POINT and not has_exact_site_point:
        if has_street_address:
            return GeographicPrecisionClass.GEOCODED_ADDRESS_APPROXIMATE
        return GeographicPrecisionClass.LOCALITY_CENTROID

    return precision

