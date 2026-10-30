"""Geodetic and Earth-Centered Cartesian (ECEF) Coordinate Conversions (Stage 130).

Implements rigorous WGS84 coordinate transformations, Bowring's algorithm for
sub-millimeter geodetic precision, angle conversions, and coordinate validation.
"""

from __future__ import annotations

import math

from atlas.maps.globe.errors import GlobeCameraInvalidError

# WGS84 Ellipsoid Standard Constants
WGS84_A: float = 6378137.0  # Semi-major axis in meters
WGS84_F: float = 1.0 / 298.257223563  # Flattening
WGS84_B: float = WGS84_A * (1.0 - WGS84_F)  # Semi-minor axis (approx 6356752.314245)
WGS84_E2: float = 2.0 * WGS84_F - WGS84_F * WGS84_F  # First eccentricity squared (e^2)
WGS84_E_PRIME2: float = (WGS84_A * WGS84_A - WGS84_B * WGS84_B) / (
    WGS84_B * WGS84_B
)  # Second eccentricity squared


def degrees_to_radians(degrees: float) -> float:
    """Explicit conversion from degrees to radians."""
    if not math.isfinite(degrees):
        raise GlobeCameraInvalidError("Angle in degrees must be a finite float")
    return math.radians(degrees)


def radians_to_degrees(radians: float) -> float:
    """Explicit conversion from radians to degrees."""
    if not math.isfinite(radians):
        raise GlobeCameraInvalidError("Angle in radians must be a finite float")
    return math.degrees(radians)


def validate_globe_coordinates(
    longitude: float, latitude: float, height_meters: float = 0.0
) -> None:
    """Validate that coordinates conform to WGS84 bounds."""
    if not math.isfinite(longitude) or not (-180.0 <= longitude <= 180.0):
        raise GlobeCameraInvalidError(
            f"Longitude must be finite and within [-180.0, 180.0], got {longitude}"
        )
    if not math.isfinite(latitude) or not (-90.0 <= latitude <= 90.0):
        raise GlobeCameraInvalidError(
            f"Latitude must be finite and within [-90.0, 90.0], got {latitude}"
        )
    if not math.isfinite(height_meters):
        raise GlobeCameraInvalidError(
            f"Height must be a finite float in meters, got {height_meters}"
        )


def geodetic_to_cartesian(
    longitude_deg: float,
    latitude_deg: float,
    height_meters: float = 0.0,
) -> tuple[float, float, float]:
    """Convert WGS84 geodetic coordinates (longitude, latitude, height) to Earth-Centered Earth-Fixed (ECEF) Cartesian (X, Y, Z) coordinates in meters.

    Returns:
        (x, y, z) in meters.
    """
    validate_globe_coordinates(longitude_deg, latitude_deg, height_meters)

    lam = math.radians(longitude_deg)
    phi = math.radians(latitude_deg)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    sin_lam = math.sin(lam)
    cos_lam = math.cos(lam)

    # Radius of curvature in the prime vertical N(phi)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_phi * sin_phi)

    x = (n + height_meters) * cos_phi * cos_lam
    y = (n + height_meters) * cos_phi * sin_lam
    z = (n * (1.0 - WGS84_E2) + height_meters) * sin_phi

    return (x, y, z)


def cartesian_to_geodetic(x: float, y: float, z: float) -> tuple[float, float, float]:
    """Convert Earth-Centered Earth-Fixed (ECEF) Cartesian (X, Y, Z) in meters to WGS84 geodetic coordinates (longitude, latitude, height).

    Uses Bowring's closed-form formulation with sub-millimeter precision.

    Returns:
        (longitude_deg, latitude_deg, height_meters)
    """
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise GlobeCameraInvalidError("Cartesian coordinates must be finite floats")

    p = math.hypot(x, y)

    # Polar singularities (p near 0)
    if p < 1e-7:
        lon_deg = 0.0
        lat_deg = 90.0 if z >= 0 else -90.0
        height_m = abs(z) - WGS84_B
        return (lon_deg, lat_deg, height_m)

    theta = math.atan2(z * WGS84_A, p * WGS84_B)
    sin_theta = math.sin(theta)
    cos_theta = math.cos(theta)

    phi = math.atan2(
        z + WGS84_E_PRIME2 * WGS84_B * (sin_theta**3),
        p - WGS84_E2 * WGS84_A * (cos_theta**3),
    )
    lam = math.atan2(y, x)

    sin_phi = math.sin(phi)
    cos_phi = math.cos(phi)
    n = WGS84_A / math.sqrt(1.0 - WGS84_E2 * sin_phi * sin_phi)

    # For high latitudes, calculate height using z to avoid division by near-zero cos(phi)
    if abs(cos_phi) > 1e-4:
        height_m = (p / cos_phi) - n
    else:
        height_m = (abs(z) / abs(sin_phi)) - (n * (1.0 - WGS84_E2))

    lon_deg = math.degrees(lam)
    lat_deg = math.degrees(phi)

    return (lon_deg, lat_deg, height_m)
