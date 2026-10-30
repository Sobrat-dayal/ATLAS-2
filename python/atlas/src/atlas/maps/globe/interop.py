"""2D/3D Camera Interoperability Engine for ATLAS Maps (Stage 130).

Implements rigorous, bidirectional conversion between 2D MapLibre cameras
(center, zoom, bearing, pitch) and 3D Cesium globe cameras (lon, lat, height, heading, pitch, roll).
"""

from __future__ import annotations

import math

from atlas.maps.domain import GeoCameraState
from atlas.maps.globe.domain import AtlasGlobeCamera
from atlas.maps.spatial.coordinates import (
    WEB_MERCATOR_MAX_LATITUDE,
    WEB_MERCATOR_MIN_LATITUDE,
)

EQUATORIAL_CIRCUMFERENCE_METERS: float = 40075016.686  # 2 * pi * WGS84_A


def normalize_longitude(longitude: float) -> float:
    """Normalize longitude to [-180, 180]."""
    lon = (longitude + 180.0) % 360.0 - 180.0
    if lon == -180.0 and longitude > 0:
        return 180.0
    return lon


def maplibre_to_cesium_camera(
    center_lon: float,
    center_lat: float,
    zoom: float,
    bearing_deg: float = 0.0,
    pitch_deg: float = 0.0,
) -> AtlasGlobeCamera:
    """Convert a 2D MapLibre camera state into an equivalent 3D Cesium globe camera.

    Args:
        center_lon: Longitude in degrees [-180, 180]
        center_lat: Latitude in degrees [-85.0511, 85.0511]
        zoom: MapLibre zoom level [0, 22]
        bearing_deg: Bearing clockwise from north [0, 360)
        pitch_deg: MapLibre pitch from vertical [0, 60] (0 = looking nadir)

    Returns:
        AtlasGlobeCamera with equivalent geographic focus and orientation.
    """
    lon = normalize_longitude(center_lon)
    lat = max(-90.0, min(90.0, center_lat))

    # Calculate camera height in meters from zoom level and latitude
    cos_lat = max(math.cos(math.radians(lat)), 0.05)
    # Height approximation based on viewport scale at equator
    height_meters = (EQUATORIAL_CIRCUMFERENCE_METERS * cos_lat) / (2.0**zoom)
    # Clamp height to sane bounds [100 meters, 25,000,000 meters]
    clamped_height = max(100.0, min(25000000.0, height_meters))

    # Convert bearing to Cesium heading radians [0, 2pi)
    heading_rad = math.radians(bearing_deg % 360.0)

    # Convert MapLibre pitch (0 = straight down) to Cesium pitch (-pi/2 = straight down)
    clamped_pitch_deg = max(0.0, min(85.0, pitch_deg))
    cesium_pitch_rad = -math.pi / 2 + math.radians(clamped_pitch_deg)

    return AtlasGlobeCamera(
        longitude=lon,
        latitude=lat,
        height_meters=clamped_height,
        heading_radians=heading_rad,
        pitch_radians=cesium_pitch_rad,
        roll_radians=0.0,
    )


def cesium_to_maplibre_camera(
    camera: AtlasGlobeCamera,
) -> GeoCameraState:
    """Convert a 3D Cesium globe camera into an equivalent 2D MapLibre camera state.

    Safely handles horizon tilt, space-directed rays, polar regions, and Web Mercator limits.

    Returns:
        GeoCameraState containing (center, zoom, pitch, bearing).
    """
    lon = normalize_longitude(camera.longitude)
    # Clamp to Web Mercator latitude bounds to avoid MapLibre projection singularity
    lat = max(WEB_MERCATOR_MIN_LATITUDE, min(WEB_MERCATOR_MAX_LATITUDE, camera.latitude))

    cos_lat = max(math.cos(math.radians(lat)), 0.05)
    effective_height = max(100.0, camera.height_meters)

    # Invert zoom equation: zoom = log2((Circumference * cos(lat)) / height)
    raw_zoom = math.log2((EQUATORIAL_CIRCUMFERENCE_METERS * cos_lat) / effective_height)
    clamped_zoom = max(0.0, min(22.0, round(raw_zoom, 2)))

    # Heading radians to bearing degrees
    bearing_deg = round(math.degrees(camera.heading_radians) % 360.0, 2)

    # Cesium pitch (-pi/2 is nadir, 0 is horizon) to MapLibre pitch (0 is nadir, 60 is angled)
    # If pitch > 0 (camera tilted up into space), fallback to nadir (0)
    effective_pitch_rad = min(0.0, camera.pitch_radians)
    converted_pitch_deg = math.degrees(effective_pitch_rad + math.pi / 2)
    clamped_pitch_deg = max(0.0, min(60.0, round(converted_pitch_deg, 2)))

    return GeoCameraState(
        longitude=round(lon, 6),
        latitude=round(lat, 6),
        zoom=clamped_zoom,
        pitch=clamped_pitch_deg,
        bearing=bearing_deg,
    )
