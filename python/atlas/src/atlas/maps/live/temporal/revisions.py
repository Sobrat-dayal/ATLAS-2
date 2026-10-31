"""Event Revision Deduplication and In-Place Upsert Engine (Stage 134).

Ensures that upstream event updates (such as revised earthquake magnitudes,
updated weather alert boundaries, or re-assessed wildfire perimeters) are
upserted as revisions of the existing canonical event, preserving audit history
without duplicating entities or inflating event counts.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import EarthquakeEvent, WeatherAlert


class EventRevisionManager:
    """Manages idempotent updates, revisions, and deduplication for event records."""

    def __init__(self) -> None:
        # Maps (provider_id, product_id, event_id) -> canonical event dict
        self._events: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def _make_key(self, provider_id: str, product_id: str, event_id: str) -> Tuple[str, str, str]:
        return (str(provider_id), str(product_id), str(event_id))

    def get_event(self, provider_id: str, product_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve canonical event if present."""
        return self._events.get(self._make_key(provider_id, product_id, event_id))

    def upsert_earthquake(
        self,
        provider_id: str,
        product_id: str,
        event: EarthquakeEvent,
    ) -> Tuple[EarthquakeEvent, bool]:
        """Upsert an earthquake event record.

        Returns:
            Tuple of (canonical_event, is_new_event).
            If existing, the record is updated in place with revision incremented and history recorded.
        """
        key = self._make_key(provider_id, product_id, event.event_id)
        existing = self._events.get(key)

        if existing is None:
            # First time seeing this earthquake
            event_dict = event.model_dump()
            event_dict["source_revision"] = 1
            event_dict["revision_history"] = [
                {
                    "revision": 1,
                    "updated_utc": event.updated_utc.isoformat(),
                    "magnitude": event.magnitude,
                    "depth_km": event.depth_km,
                    "status": event.status,
                }
            ]
            self._events[key] = event_dict
            return EarthquakeEvent(**event_dict), True

        # Existing record check
        # Check if incoming has newer updated_utc or different magnitude/status
        existing_updated = existing.get("updated_utc")
        if isinstance(existing_updated, str):
            existing_updated_dt = datetime.fromisoformat(existing_updated)
        else:
            existing_updated_dt = existing_updated

        incoming_updated = event.updated_utc
        if incoming_updated.tzinfo is None:
            incoming_updated = incoming_updated.replace(tzinfo=timezone.utc)
        if existing_updated_dt and existing_updated_dt.tzinfo is None:
            existing_updated_dt = existing_updated_dt.replace(tzinfo=timezone.utc)

        # Has anything changed?
        is_changed = (
            event.magnitude != existing.get("magnitude")
            or event.depth_km != existing.get("depth_km")
            or event.status != existing.get("status")
            or (existing_updated_dt and incoming_updated > existing_updated_dt)
        )

        if not is_changed:
            # Idempotent duplicate: return existing unmodified
            return EarthquakeEvent(**existing), False

        # Apply revision
        new_revision = existing.get("source_revision", 1) + 1
        history_entry = {
            "revision": new_revision,
            "updated_utc": incoming_updated.isoformat(),
            "magnitude": event.magnitude,
            "depth_km": event.depth_km,
            "status": event.status,
        }
        existing_history: List[Dict[str, Any]] = existing.get("revision_history", [])
        existing_history.append(history_entry)

        # Update in-place
        existing["magnitude"] = event.magnitude
        existing["depth_km"] = event.depth_km
        existing["status"] = event.status
        existing["title"] = event.title
        existing["updated_utc"] = incoming_updated
        existing["source_revision"] = new_revision
        existing["revision_history"] = existing_history

        return EarthquakeEvent(**existing), False

    def list_events(self) -> List[Dict[str, Any]]:
        """List all current event records."""
        return list(self._events.values())

    def clear(self) -> None:
        """Reset state."""
        self._events.clear()

