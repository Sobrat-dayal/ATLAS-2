"""Event Revision and Retraction Manager (Stage 135).

Manages non-destructive event revisions, economic data restatements,
seismic magnitude refinements, and formal event retractions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import AtlasUniversalEvent, EventLifecycleStatus, EventRevision


class RevisionManager:
    """Manages revisions, corrections, and retractions for canonical events."""

    def __init__(self) -> None:
        # Maps event_id -> list of EventRevision records
        self._revisions: Dict[str, List[EventRevision]] = {}

    def get_revisions(self, event_id: str) -> List[EventRevision]:
        """Retrieve revision audit trail for an event."""
        return list(self._revisions.get(event_id, []))

    def get_revisions_for_event(self, event_id: str) -> List[EventRevision]:
        """Alias for get_revisions."""
        return self.get_revisions(event_id)

    def record_revision(self, revision: EventRevision) -> None:
        """Record an explicit historical revision record."""
        if revision.event_id not in self._revisions:
            self._revisions[revision.event_id] = []
        self._revisions[revision.event_id].append(revision)

    def get_all_revisions(self) -> List[EventRevision]:
        """Retrieve all revision records across all events."""
        all_revs: List[EventRevision] = []
        for r_list in self._revisions.values():
            all_revs.extend(r_list)
        return all_revs

    def apply_revision(
        self,
        event: AtlasUniversalEvent,
        changed_fields: Dict[str, Any],
        reason: str,
        published_at: Optional[datetime] = None,
    ) -> Tuple[AtlasUniversalEvent, EventRevision]:
        """Apply an in-place update to an existing event, recording audit snapshot."""
        now_utc = datetime.now(timezone.utc)
        prev_rev_id = f"rev-{event.event_id}-{event.current_revision_number}"

        # Capture old values of changed fields for historical bitemporal rewind
        old_fields_snapshot: Dict[str, Any] = {}
        for k in changed_fields.keys():
            if hasattr(event, k):
                old_fields_snapshot[k] = getattr(event, k)
            elif k in event.event_payload:
                old_fields_snapshot[k] = event.event_payload[k]

        # Apply new values
        for k, v in changed_fields.items():
            if hasattr(event, k):
                setattr(event, k, v)
            else:
                event.event_payload[k] = v

        event.current_revision_number += 1
        event.updated_at = now_utc
        new_rev_id = f"rev-{event.event_id}-{event.current_revision_number}"

        revision_record = EventRevision(
            event_revision_id=new_rev_id,
            event_id=event.event_id,
            revision_number=event.current_revision_number,
            changed_fields=old_fields_snapshot,
            previous_revision_id=prev_rev_id,
            reason=reason,
            recorded_at=now_utc,
            published_at=published_at or now_utc,
        )

        if event.event_id not in self._revisions:
            self._revisions[event.event_id] = []
        self._revisions[event.event_id].append(revision_record)

        return event, revision_record

    def retract_event(
        self,
        event: AtlasUniversalEvent,
        reason: str,
        published_at: Optional[datetime] = None,
    ) -> Tuple[AtlasUniversalEvent, EventRevision]:
        """Retract an event following an official provider withdrawal or false report."""
        return self.apply_revision(
            event=event,
            changed_fields={
                "is_retracted": True,
                "retraction_reason": reason,
                "lifecycle_status": EventLifecycleStatus.RETRACTED,
            },
            reason=f"RETRACTED: {reason}",
            published_at=published_at,
        )
