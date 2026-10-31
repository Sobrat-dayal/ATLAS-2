"""Hot State Store for Live Geospatial Observations (Stage 134).

Maintains low-latency in-memory state of active physical observations with
monotonic sequence numbering, snapshot construction, cursor-based delta sync,
bounding box filtering, and historical playback retrieval.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import AtlasGeoObservation, FreshnessState, LiveObservationCategory
from ..temporal.freshness import evaluate_freshness
from ..temporal.watermarks import WatermarkManager


class LiveHotStateStore:
    """Institutional hot state repository with watermark protection and sequence tracking."""

    def __init__(self) -> None:
        # Hot active observations: entity_id -> AtlasGeoObservation
        self._active_state: Dict[str, AtlasGeoObservation] = {}
        # Monotonic sequence counter for delta streaming
        self._sequence_counter: int = 1000
        # Watermark manager for out-of-order rejection
        self._watermarks = WatermarkManager()
        # Historical buffer for temporal playback: list of observations
        self._history: List[AtlasGeoObservation] = []

    @property
    def current_sequence(self) -> int:
        return self._sequence_counter

    def ingest_observation(
        self,
        obs: AtlasGeoObservation,
        allow_out_of_order_history: bool = True,
    ) -> Tuple[Optional[AtlasGeoObservation], bool]:
        """Ingest a physical observation.

        Returns:
            Tuple of (effective_observation, is_hot_updated).
            If the observation arrived out-of-order (older than watermark for this entity),
            is_hot_updated is False and hot active state is preserved at the newer position.
        """
        # Ensure UTC timezone
        if obs.observed_at.tzinfo is None:
            obs.observed_at = obs.observed_at.replace(tzinfo=timezone.utc)
        if obs.ingested_at.tzinfo is None:
            obs.ingested_at = obs.ingested_at.replace(tzinfo=timezone.utc)

        # Out-of-order verification
        is_newer = self._watermarks.check_observation(
            category=obs.category,
            entity_id=obs.entity_id,
            observed_at=obs.observed_at,
        )

        if not is_newer:
            # Older observation arrival: record in history if allowed, but NEVER overwrite hot state
            if allow_out_of_order_history:
                self._history.append(obs)
            return None, False

        # Valid monotonic forward progress
        self._watermarks.update_watermark(obs.category, obs.entity_id, obs.observed_at)
        self._sequence_counter += 1
        obs.sequence_number = self._sequence_counter

        # Evaluate freshness
        freshness_state, age_seconds = evaluate_freshness(obs.observed_at, obs.category)
        obs.freshness_state = freshness_state
        obs.freshness_age_seconds = age_seconds

        # Store in hot cache and history
        self._active_state[obs.entity_id] = obs
        self._history.append(obs)

        return obs, True

    def get_snapshot(
        self,
        categories: Optional[List[LiveObservationCategory]] = None,
        bbox: Optional[List[float]] = None,
        max_results: int = 1000,
        now_utc: Optional[datetime] = None,
    ) -> Tuple[List[AtlasGeoObservation], int]:
        """Retrieve full active snapshot with freshness re-evaluated."""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)

        results: List[AtlasGeoObservation] = []
        target_cats = set(categories) if categories else None

        for obs in self._active_state.values():
            if target_cats and obs.category not in target_cats:
                continue

            # Bounding box filter [min_lon, min_lat, max_lon, max_lat]
            if bbox and len(bbox) == 4:
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (min_lon <= obs.longitude <= max_lon and min_lat <= obs.latitude <= max_lat):
                    continue

            # Update freshness state
            freshness_state, age_seconds = evaluate_freshness(obs.observed_at, obs.category, now_utc=now_utc)
            obs_copy = obs.model_copy(update={"freshness_state": freshness_state, "freshness_age_seconds": age_seconds})
            results.append(obs_copy)

            if len(results) >= max_results:
                break

        return results, self._sequence_counter

    def get_deltas(
        self,
        since_sequence: int,
        categories: Optional[List[LiveObservationCategory]] = None,
        bbox: Optional[List[float]] = None,
        max_results: int = 1000,
    ) -> Tuple[List[AtlasGeoObservation], int]:
        """Retrieve deltas since a previous sequence cursor."""
        now_utc = datetime.now(timezone.utc)
        target_cats = set(categories) if categories else None
        deltas: List[AtlasGeoObservation] = []

        for obs in self._active_state.values():
            if obs.sequence_number <= since_sequence:
                continue
            if target_cats and obs.category not in target_cats:
                continue
            if bbox and len(bbox) == 4:
                min_lon, min_lat, max_lon, max_lat = bbox
                if not (min_lon <= obs.longitude <= max_lon and min_lat <= obs.latitude <= max_lat):
                    continue

            freshness_state, age_seconds = evaluate_freshness(obs.observed_at, obs.category, now_utc=now_utc)
            obs_copy = obs.model_copy(update={"freshness_state": freshness_state, "freshness_age_seconds": age_seconds})
            deltas.append(obs_copy)

            if len(deltas) >= max_results:
                break

        return deltas, self._sequence_counter

    def get_playback_snapshot(
        self,
        target_time_utc: datetime,
        window_seconds: float = 3600.0,
        categories: Optional[List[LiveObservationCategory]] = None,
    ) -> List[AtlasGeoObservation]:
        """Reconstruct the physical state known at target_time_utc."""
        if target_time_utc.tzinfo is None:
            target_time_utc = target_time_utc.replace(tzinfo=timezone.utc)

        target_cats = set(categories) if categories else None
        # Track most recent observation per entity on or before target_time_utc
        latest_per_entity: Dict[str, AtlasGeoObservation] = {}

        for obs in self._history:
            if target_cats and obs.category not in target_cats:
                continue
            obs_time = obs.observed_at
            if obs_time.tzinfo is None:
                obs_time = obs_time.replace(tzinfo=timezone.utc)

            if obs_time <= target_time_utc:
                age_at_target = (target_time_utc - obs_time).total_seconds()
                if age_at_target <= window_seconds:
                    existing = latest_per_entity.get(obs.entity_id)
                    if existing is None or obs_time > existing.observed_at:
                        latest_per_entity[obs.entity_id] = obs

        playback_results: List[AtlasGeoObservation] = []
        for obs in latest_per_entity.values():
            freshness_state, age_seconds = evaluate_freshness(
                obs.observed_at, obs.category, now_utc=target_time_utc
            )
            playback_results.append(
                obs.model_copy(
                    update={
                        "freshness_state": FreshnessState.HISTORICAL,
                        "freshness_age_seconds": age_seconds,
                    }
                )
            )

        return playback_results

    def clear(self) -> None:
        """Reset state."""
        self._active_state.clear()
        self._watermarks.clear()
        self._history.clear()
        self._sequence_counter = 1000

