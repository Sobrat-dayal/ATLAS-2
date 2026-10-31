"""Watermark and Out-of-Order Observation Protection (Stage 134).

Ensures that older delayed physical observations (e.g. late network packets or
out-of-order satellite downlink batches) never overwrite a newer verified
instantaneous state in the live hot cache.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from ..domain import LiveObservationCategory


class WatermarkManager:
    """Tracks physical measurement watermarks per entity."""

    def __init__(self) -> None:
        # Maps (category, entity_id) -> latest observed_at timestamp
        self._watermarks: Dict[Tuple[str, str], datetime] = {}

    def _make_key(self, category: LiveObservationCategory, entity_id: str) -> Tuple[str, str]:
        return (str(category.value if hasattr(category, "value") else category), str(entity_id))

    def get_watermark(self, category: LiveObservationCategory, entity_id: str) -> Optional[datetime]:
        """Retrieve the latest observed watermark for an entity."""
        return self._watermarks.get(self._make_key(category, entity_id))

    def check_observation(
        self,
        category: LiveObservationCategory,
        entity_id: str,
        observed_at: datetime,
    ) -> bool:
        """Check if an observation is newer than or equal to current watermark.

        Returns:
            True if the observation is current or new (valid to update hot state).
            False if it is out-of-order (older than watermark; drop or log to history only).
        """
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)

        key = self._make_key(category, entity_id)
        current_wm = self._watermarks.get(key)
        if current_wm is None:
            return True
        if current_wm.tzinfo is None:
            current_wm = current_wm.replace(tzinfo=timezone.utc)

        return observed_at >= current_wm

    def update_watermark(
        self,
        category: LiveObservationCategory,
        entity_id: str,
        observed_at: datetime,
    ) -> bool:
        """Attempt to update watermark for an entity.

        Returns:
            True if watermark was updated.
            False if incoming observation was older (watermark unchanged).
        """
        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)

        key = self._make_key(category, entity_id)
        current_wm = self._watermarks.get(key)
        if current_wm is None or observed_at >= current_wm:
            self._watermarks[key] = observed_at
            return True
        return False

    def clear(self) -> None:
        """Reset all watermarks."""
        self._watermarks.clear()

