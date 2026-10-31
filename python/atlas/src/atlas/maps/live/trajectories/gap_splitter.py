"""Trajectory Gap Splitting Engine (Stage 134).

Enforces the physical trajectory gap invariant: when flight or vessel observation
points are separated by prolonged communication blackouts, transponder reboots,
or oceanic coverage gaps, trajectories are split into distinct, honest segments
rather than interpolating fictitious straight lines across unobserved space.
"""

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..domain import LiveObservationCategory, TrajectorySegment


def _haversine_distance_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Calculate the great circle distance between two points on Earth in km."""
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def split_trajectory_points(
    points: List[Dict[str, Any]],
    category: LiveObservationCategory,
    entity_id: str,
    max_gap_seconds: Optional[float] = None,
    max_speed_kmh: Optional[float] = None,
) -> List[TrajectorySegment]:
    """Split observation history points into distinct physical trajectory segments.

    Args:
        points: List of dicts with 'longitude', 'latitude', optional 'altitude_m', and 'timestamp' (datetime or ISO str).
        category: Aircraft, Vessel, etc.
        entity_id: Transponder / MMSI / ID.
        max_gap_seconds: Max acceptable time gap before splitting.
        max_speed_kmh: Max plausible velocity before flagging anomalous jump.

    Returns:
        List of TrajectorySegment objects.
    """
    if not points:
        return []

    # Configure category-appropriate thresholds
    if max_gap_seconds is None:
        if category == LiveObservationCategory.AIRCRAFT:
            max_gap_seconds = 900.0   # 15 minutes
        elif category == LiveObservationCategory.VESSEL:
            max_gap_seconds = 7200.0  # 2 hours
        else:
            max_gap_seconds = 3600.0  # 1 hour

    if max_speed_kmh is None:
        if category == LiveObservationCategory.AIRCRAFT:
            max_speed_kmh = 1350.0    # Commercial supersonic jump threshold
        elif category == LiveObservationCategory.VESSEL:
            max_speed_kmh = 95.0      # Fast ferry / high-speed marine limit
        else:
            max_speed_kmh = 28000.0   # Low Earth Orbit speed

    # Sort points chronologically
    parsed_points = []
    for pt in points:
        ts = pt.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        parsed_points.append(
            {
                "lon": float(pt["longitude"]),
                "lat": float(pt["latitude"]),
                "alt": float(pt.get("altitude_m", 0.0) or 0.0),
                "time": ts,
            }
        )

    parsed_points.sort(key=lambda p: p["time"])

    segments: List[TrajectorySegment] = []
    curr_coords: List[List[float]] = []
    curr_times: List[datetime] = []
    has_gap_break = False
    gap_reason: Optional[str] = None
    segment_idx = 1

    for i, pt in enumerate(parsed_points):
        if i == 0:
            curr_coords.append([pt["lon"], pt["lat"], pt["alt"]])
            curr_times.append(pt["time"])
            continue

        prev_pt = parsed_points[i - 1]
        delta_sec = (pt["time"] - prev_pt["time"]).total_seconds()
        dist_km = _haversine_distance_km(prev_pt["lon"], prev_pt["lat"], pt["lon"], pt["lat"])
        speed_kmh = (dist_km / (delta_sec / 3600.0)) if delta_sec > 0 else 0.0

        is_split = False
        reason = None

        if delta_sec > max_gap_seconds:
            is_split = True
            reason = f"Tracking blackout: {delta_sec/60.0:.1f} min gap exceeds {max_gap_seconds/60.0:.0f} min threshold"
        elif speed_kmh > max_speed_kmh and delta_sec > 5.0:
            is_split = True
            reason = f"Implausible velocity jump: {speed_kmh:.1f} km/h exceeds physical limit"

        if is_split:
            # Finalize current segment
            if curr_coords:
                segments.append(
                    TrajectorySegment(
                        entity_id=entity_id,
                        category=category,
                        segment_id=f"{entity_id}-seg-{segment_idx}",
                        start_time=curr_times[0],
                        end_time=curr_times[-1],
                        point_count=len(curr_coords),
                        coordinates=curr_coords,
                        timestamps=curr_times,
                        has_gap_break=has_gap_break,
                        gap_reason=gap_reason,
                    )
                )
                segment_idx += 1

            # Start fresh segment
            curr_coords = [[pt["lon"], pt["lat"], pt["alt"]]]
            curr_times = [pt["time"]]
            has_gap_break = True
            gap_reason = reason
        else:
            curr_coords.append([pt["lon"], pt["lat"], pt["alt"]])
            curr_times.append(pt["time"])

    # Finalize last segment
    if curr_coords:
        segments.append(
            TrajectorySegment(
                entity_id=entity_id,
                category=category,
                segment_id=f"{entity_id}-seg-{segment_idx}",
                start_time=curr_times[0],
                end_time=curr_times[-1],
                point_count=len(curr_coords),
                coordinates=curr_coords,
                timestamps=curr_times,
                has_gap_break=has_gap_break,
                gap_reason=gap_reason,
            )
        )

    return segments

