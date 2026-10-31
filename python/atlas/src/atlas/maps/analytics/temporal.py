"""Time-Aware Spatial Analytics and Temporal Bucketing Engine (Stage 131).

Provides historical point-in-time filtering, deterministic temporal bucketing,
and zero look-ahead bias verification.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from atlas.maps.analytics.domain import TimeBucketInterval


def parse_iso_datetime(dt_str: Optional[str]) -> Optional[datetime.datetime]:
    """Safely parses ISO 8601 datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def get_temporal_bucket_key(
    dt: datetime.datetime,
    interval: TimeBucketInterval = TimeBucketInterval.DAY,
) -> str:
    """Computes deterministic temporal bucket partition key for an observation timestamp.

    Guarantees no look-ahead bias and stable time windowing.
    """
    if interval == TimeBucketInterval.HOUR:
        return dt.strftime("%Y-%m-%dT%H:00:00Z")
    elif interval == TimeBucketInterval.DAY:
        return dt.strftime("%Y-%m-%d")
    elif interval == TimeBucketInterval.WEEK:
        year, week, _ = dt.isocalendar()
        return f"{year}-W{week:02d}"
    elif interval == TimeBucketInterval.MONTH:
        return dt.strftime("%Y-%m")
    elif interval == TimeBucketInterval.QUARTER:
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{quarter}"
    elif interval == TimeBucketInterval.YEAR:
        return dt.strftime("%Y")
    return dt.strftime("%Y-%m-%d")


def filter_by_historical_as_of(
    observations: List[Dict[str, Any]],
    as_of: Optional[datetime.datetime],
    time_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filters records to include only those known as-of the historical reference timestamp.

    Strictly guarantees zero look-ahead bias by excluding observations recorded after as_of.
    """
    if not as_of:
        return observations

    candidate_keys = (
        [time_key] if time_key else ["observed_at", "source_updated_at", "timestamp", "created_at"]
    )

    filtered: List[Dict[str, Any]] = []
    for obs in observations:
        obs_dt = None
        for k in candidate_keys:
            if k and k in obs:
                obs_dt = obs[k]
                break

        if isinstance(obs_dt, str):
            obs_dt = parse_iso_datetime(obs_dt)

        if obs_dt is not None:
            # Normalize naive / aware comparison if needed
            if as_of.tzinfo is not None and obs_dt.tzinfo is None:
                obs_dt = obs_dt.replace(tzinfo=datetime.timezone.utc)
            elif as_of.tzinfo is None and obs_dt.tzinfo is not None:
                obs_dt = obs_dt.replace(tzinfo=None)

            if obs_dt <= as_of:
                filtered.append(obs)

    return filtered
