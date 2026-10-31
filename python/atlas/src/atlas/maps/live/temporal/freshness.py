"""Institutional Freshness Evaluation Engine (Stage 134).

Evaluates physical observation freshness strictly against the physical measurement
clock (observed_at), never against the ingestion receipt or client WebSocket arrival clock.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from ..domain import FreshnessPolicy, FreshnessState, LiveObservationCategory


DEFAULT_POLICIES: Dict[LiveObservationCategory, FreshnessPolicy] = {
    LiveObservationCategory.AIRCRAFT: FreshnessPolicy(
        category=LiveObservationCategory.AIRCRAFT,
        nominal_latency_seconds=10.0,
        stale_threshold_seconds=120.0,      # 2 minutes without update -> STALE
        expired_threshold_seconds=900.0,    # 15 minutes without update -> EXPIRED
    ),
    LiveObservationCategory.VESSEL: FreshnessPolicy(
        category=LiveObservationCategory.VESSEL,
        nominal_latency_seconds=60.0,
        stale_threshold_seconds=600.0,      # 10 minutes -> STALE
        expired_threshold_seconds=7200.0,   # 2 hours -> EXPIRED
    ),
    LiveObservationCategory.SATELLITE: FreshnessPolicy(
        category=LiveObservationCategory.SATELLITE,
        nominal_latency_seconds=1.0,
        stale_threshold_seconds=60.0,       # 1 minute -> STALE
        expired_threshold_seconds=300.0,    # 5 minutes -> EXPIRED
    ),
    LiveObservationCategory.WEATHER_OBSERVATION: FreshnessPolicy(
        category=LiveObservationCategory.WEATHER_OBSERVATION,
        nominal_latency_seconds=300.0,      # 5 minutes
        stale_threshold_seconds=3600.0,     # 1 hour -> STALE
        expired_threshold_seconds=86400.0,  # 24 hours -> EXPIRED
    ),
    LiveObservationCategory.WEATHER_FORECAST: FreshnessPolicy(
        category=LiveObservationCategory.WEATHER_FORECAST,
        nominal_latency_seconds=3600.0,
        stale_threshold_seconds=21600.0,    # 6 hours
        expired_threshold_seconds=86400.0,
    ),
    LiveObservationCategory.WEATHER_ALERT: FreshnessPolicy(
        category=LiveObservationCategory.WEATHER_ALERT,
        nominal_latency_seconds=60.0,
        stale_threshold_seconds=14400.0,    # 4 hours
        expired_threshold_seconds=86400.0,  # 24 hours (or expires_utc)
    ),
    LiveObservationCategory.EARTHQUAKE: FreshnessPolicy(
        category=LiveObservationCategory.EARTHQUAKE,
        nominal_latency_seconds=180.0,      # 3 minutes
        stale_threshold_seconds=86400.0,    # 24 hours
        expired_threshold_seconds=604800.0, # 7 days
    ),
    LiveObservationCategory.ACTIVE_FIRE: FreshnessPolicy(
        category=LiveObservationCategory.ACTIVE_FIRE,
        nominal_latency_seconds=10800.0,    # 3 hours (satellite orbit pass latency)
        stale_threshold_seconds=43200.0,    # 12 hours
        expired_threshold_seconds=86400.0,  # 24 hours
    ),
    LiveObservationCategory.NATURAL_EVENT: FreshnessPolicy(
        category=LiveObservationCategory.NATURAL_EVENT,
        nominal_latency_seconds=3600.0,
        stale_threshold_seconds=86400.0,
        expired_threshold_seconds=604800.0,
    ),
}


def evaluate_freshness(
    observed_at: datetime,
    category: LiveObservationCategory,
    now_utc: Optional[datetime] = None,
    custom_policy: Optional[FreshnessPolicy] = None,
    expires_utc: Optional[datetime] = None,
) -> Tuple[FreshnessState, float]:
    """Compute institutional freshness state and age in seconds.

    Invariant: Age is strictly calculated from observed_at, never from receipt_at.
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    elif now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(tzinfo=timezone.utc)

    age_seconds = max(0.0, (now_utc - observed_at).total_seconds())

    # Check alert expiration date if applicable
    if expires_utc is not None:
        if expires_utc.tzinfo is None:
            expires_utc = expires_utc.replace(tzinfo=timezone.utc)
        if now_utc > expires_utc:
            return FreshnessState.EXPIRED, age_seconds

    policy = custom_policy or DEFAULT_POLICIES.get(category)
    if not policy:
        # Fallback generic policy
        if age_seconds < 120.0:
            return FreshnessState.CURRENT, age_seconds
        elif age_seconds < 600.0:
            return FreshnessState.DELAYED, age_seconds
        elif age_seconds < 3600.0:
            return FreshnessState.STALE, age_seconds
        else:
            return FreshnessState.EXPIRED, age_seconds

    if age_seconds <= policy.nominal_latency_seconds:
        return FreshnessState.CURRENT, age_seconds
    elif age_seconds <= policy.stale_threshold_seconds:
        return FreshnessState.DELAYED, age_seconds
    elif age_seconds <= policy.expired_threshold_seconds:
        return FreshnessState.STALE, age_seconds
    else:
        return FreshnessState.EXPIRED, age_seconds
