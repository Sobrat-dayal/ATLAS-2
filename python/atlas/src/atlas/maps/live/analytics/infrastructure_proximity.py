"""Infrastructure Proximity Correlation Engine (Stage 134).

Correlates real-time physical observations (earthquake epicenters, active fire detections,
severe weather alert perimeters) with Stage 133 verified critical infrastructure assets.

Strict Invariant: Geographic proximity alone NEVER asserts physical damage or disruption.
All matches carry UNVERIFIED_PROXIMITY_ONLY status and required institutional disclaimers.
"""

import math
from typing import Any, Dict, List, Optional

from ..domain import InfrastructureProximityMatch, LiveObservationCategory


def _haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate Great Circle distance in kilometers."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * (math.sin(dlon / 2.0) ** 2)
    )
    return r * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def _point_in_polygon(lon: float, lat: float, polygon_coords: List[List[float]]) -> bool:
    """Ray casting algorithm to determine if a point is inside a polygon."""
    num_points = len(polygon_coords)
    inside = False
    p1x, p1y = polygon_coords[0][0], polygon_coords[0][1]
    for i in range(1, num_points + 1):
        p2x, p2y = polygon_coords[i % num_points][0], polygon_coords[i % num_points][1]
        if lat > min(p1y, p2y):
            if lat <= max(p1y, p2y):
                if lon <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lon <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def correlate_infrastructure_proximity(
    facilities: List[Dict[str, Any]],
    event: Dict[str, Any],
    max_radius_km: float = 100.0,
) -> List[InfrastructureProximityMatch]:
    """Correlate physical infrastructure facilities with a live physical event.

    Args:
        facilities: List of Stage 133 infrastructure records with 'facility_id', 'facility_name',
                   'sector', 'longitude', 'latitude'.
        event: Dict representing the live observation with 'observation_id', 'category', 'entity_id',
               'longitude', 'latitude', optional 'geometry', optional 'severity' / 'magnitude'.
        max_radius_km: Maximum radius in km to evaluate proximity.

    Returns:
        List of InfrastructureProximityMatch records.
    """
    matches: List[InfrastructureProximityMatch] = []
    e_lon = float(event["longitude"])
    e_lat = float(event["latitude"])
    e_cat = event.get("category", LiveObservationCategory.EARTHQUAKE)
    if isinstance(e_cat, str):
        try:
            e_cat = LiveObservationCategory(e_cat)
        except ValueError:
            e_cat = LiveObservationCategory.NATURAL_EVENT

    obs_id = str(event.get("observation_id", event.get("entity_id", "obs-001")))
    entity_id = str(event.get("entity_id", obs_id))
    severity = str(event.get("severity") or event.get("magnitude") or "ALERT")

    # Check for polygon geometry (e.g. weather CAP alert polygon)
    poly_coords: Optional[List[List[float]]] = None
    geom = event.get("geometry")
    if geom and geom.get("type") == "Polygon" and geom.get("coordinates"):
        poly_coords = geom["coordinates"][0]

    for fac in facilities:
        f_lon = float(fac["longitude"])
        f_lat = float(fac["latitude"])
        dist_km = _haversine_km(f_lon, f_lat, e_lon, e_lat)

        inside_poly = False
        if poly_coords:
            inside_poly = _point_in_polygon(f_lon, f_lat, poly_coords)

        # Match if within radius or inside alert perimeter
        if dist_km <= max_radius_km or inside_poly:
            matches.append(
                InfrastructureProximityMatch(
                    facility_id=str(fac.get("facility_id", fac.get("id"))),
                    facility_name=str(fac.get("facility_name", fac.get("name", "Unknown Facility"))),
                    facility_sector=str(fac.get("sector", "ENERGY")),
                    facility_coordinates=[f_lon, f_lat],
                    observation_id=obs_id,
                    observation_category=e_cat,
                    event_entity_id=entity_id,
                    distance_km=round(dist_km, 2),
                    inside_alert_perimeter=inside_poly,
                    severity=severity,
                    damage_assessment="UNVERIFIED_PROXIMITY_ONLY",
                    damage_confirmed=False,
                    disclaimer=(
                        "Spatial proximity does not constitute physical damage, structural failure, "
                        "or operational outage. On-site telemetry or official inspection required."
                    ),
                )
            )

    matches.sort(key=lambda m: m.distance_km)
    return matches

