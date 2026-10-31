"""Bitemporal History and Historical As-Of Query Engine (Stage 135).

Distinguishes:
- Valid Time: When an event or state applied in the real world.
- Knowledge/System Time: When ATLAS or the source learned and recorded it.

Strict Invariant: Zero Look-Ahead Bias!
Historical as-of queries must never silently incorporate future publications,
revisions, corrections, or retractions that occurred after the requested knowledge time.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..domain import AtlasUniversalEvent, EventLifecycleStatus, EventRevision, EventVerificationStatus


class BitemporalEngine:
    """Evaluates event knowledge state as-of any historical point in time."""

    def __init__(self, revision_store: Optional[Dict[str, List[EventRevision]]] = None) -> None:
        # Maps event_id -> ordered list of EventRevision
        self._revision_store: Dict[str, List[EventRevision]] = revision_store or {}

    def set_revisions(self, event_id: str, revisions: List[EventRevision]) -> None:
        """Register revision history for an event."""
        self._revision_store[event_id] = sorted(revisions, key=lambda r: r.revision_number)

    def as_of_event(
        self,
        event: AtlasUniversalEvent,
        revisions: List[EventRevision],
        as_of_time: datetime,
    ) -> Optional[AtlasUniversalEvent]:
        """Evaluate a single event as known at as_of_time.
        
        Returns None if the event was not yet ingested/known at as_of_time.
        """
        if as_of_time.tzinfo is None:
            as_of_time = as_of_time.replace(tzinfo=timezone.utc)

        ev_ingested = event.first_ingested_at
        if ev_ingested.tzinfo is None:
            ev_ingested = ev_ingested.replace(tzinfo=timezone.utc)

        # Zero Look-Ahead Bias: Event did not exist in system knowledge yet
        if ev_ingested > as_of_time:
            return None

        # Deep clone event
        snapshot = event.model_copy(deep=True)

        # Sort and filter revisions known on or before as_of_time
        sorted_revs = sorted(revisions, key=lambda r: r.revision_number)
        applicable_revs = [
            r for r in sorted_revs
            if (r.recorded_at if r.recorded_at.tzinfo else r.recorded_at.replace(tzinfo=timezone.utc)) <= as_of_time
        ]

        if applicable_revs:
            latest_rev = applicable_revs[-1]
            snapshot.current_revision_number = latest_rev.revision_number

            # Apply fields active as of this revision
            for field_name, val in latest_rev.changed_fields.items():
                if field_name == "event_payload" and isinstance(val, dict):
                    snapshot.event_payload.update(val)
                elif hasattr(snapshot, field_name):
                    setattr(snapshot, field_name, val)
                else:
                    snapshot.event_payload[field_name] = val

        # Handle retractions that occurred AFTER as_of_time
        if snapshot.is_retracted:
            future_retraction = any(
                (r.recorded_at if r.recorded_at.tzinfo else r.recorded_at.replace(tzinfo=timezone.utc)) > as_of_time
                and "RETRACT" in r.reason.upper()
                for r in sorted_revs
            )
            if future_retraction:
                snapshot.is_retracted = False
                snapshot.retraction_reason = None
                if snapshot.lifecycle_status == EventLifecycleStatus.RETRACTED:
                    snapshot.lifecycle_status = EventLifecycleStatus.OCCURRED
                    snapshot.verification_status = EventVerificationStatus.OFFICIALLY_CONFIRMED

        return snapshot

    def as_of_dataset(
        self,
        events: List[AtlasUniversalEvent],
        all_revisions: List[EventRevision],
        as_of_time: datetime,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasUniversalEvent]:
        """Evaluate an entire dataset as of as_of_time."""
        revs_by_event: Dict[str, List[EventRevision]] = {}
        for r in all_revisions:
            revs_by_event.setdefault(r.event_id, []).append(r)

        results: List[AtlasUniversalEvent] = []
        for e in events:
            if tenant_id and e.tenant_id and e.tenant_id != tenant_id:
                continue
            ev_revs = revs_by_event.get(e.event_id, [])
            snap = self.as_of_event(e, ev_revs, as_of_time)
            if snap is not None:
                results.append(snap)

        return results

    def query_as_of(
        self,
        events: List[AtlasUniversalEvent],
        as_of_utc: datetime,
    ) -> List[AtlasUniversalEvent]:
        """Compatibility wrapper."""
        all_revs = [r for rev_list in self._revision_store.values() for r in rev_list]
        return self.as_of_dataset(events, all_revs, as_of_utc)
