"""Event Merge and Split Manager (Stage 135).

Provides non-destructive merging of duplicate canonical events and safe splitting
to correct erroneous merges with complete audit trail preservation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from ..domain import AtlasUniversalEvent
from ..errors import EventMergeSplitValidationError


class MergeAuditRecord(BaseModel):
    """Audit receipt for event merge or split operations."""
    audit_id: str
    operation: str  # "MERGE" or "SPLIT"
    primary_event_id: str
    secondary_event_id: str
    reason: str
    authorized_by: str
    timestamp_utc: datetime
    previous_aliases: List[str] = Field(default_factory=list)


class MergeSplitManager:
    """Manages transactional event merge and split operations."""

    def __init__(self) -> None:
        self._audit_log: List[MergeAuditRecord] = []

    def merge_events(
        self,
        primary: AtlasUniversalEvent,
        secondary: AtlasUniversalEvent,
        reason: str,
        authorized_by: str = "SYSTEM_DEDUPLICATION",
    ) -> Tuple[AtlasUniversalEvent, MergeAuditRecord]:
        """Merge a secondary duplicate event into the primary canonical event."""
        if primary.event_id == secondary.event_id:
            raise EventMergeSplitValidationError("Cannot merge an event into itself")

        if primary.event_category != secondary.event_category:
            raise EventMergeSplitValidationError(
                f"Cannot merge events across distinct categories: {primary.event_category} vs {secondary.event_category}"
            )

        now_utc = datetime.now(timezone.utc)
        prev_aliases = list(primary.aliases)

        # Collect aliases
        new_aliases = set(primary.aliases)
        new_aliases.add(secondary.event_id)
        new_aliases.add(secondary.canonical_event_key)
        new_aliases.update(secondary.aliases)
        primary.aliases = sorted(list(new_aliases))

        # Accumulate source count
        primary.source_count += secondary.source_count
        primary.updated_at = now_utc

        # Merge tags
        primary.tags = sorted(list(set(primary.tags + secondary.tags)))

        audit = MergeAuditRecord(
            audit_id=f"audit-merge-{primary.event_id}-{secondary.event_id}-{int(now_utc.timestamp())}",
            operation="MERGE",
            primary_event_id=primary.event_id,
            secondary_event_id=secondary.event_id,
            reason=reason,
            authorized_by=authorized_by,
            timestamp_utc=now_utc,
            previous_aliases=prev_aliases,
        )
        self._audit_log.append(audit)
        return primary, audit

    def split_event(
        self,
        primary: AtlasUniversalEvent,
        split_event_id: str,
        split_event_key: str,
        reason: str,
        authorized_by: str = "OPERATOR_SPLIT",
    ) -> Tuple[AtlasUniversalEvent, AtlasUniversalEvent, MergeAuditRecord]:
        """Split an erroneously merged entity out into its own canonical event."""
        if split_event_id not in primary.aliases and split_event_key not in primary.aliases:
            raise EventMergeSplitValidationError(f"Alias '{split_event_id}' not found in primary event aliases")

        now_utc = datetime.now(timezone.utc)
        prev_aliases = list(primary.aliases)

        # Remove from primary aliases
        primary.aliases = [a for a in primary.aliases if a not in (split_event_id, split_event_key)]
        primary.source_count = max(1, primary.source_count - 1)
        primary.updated_at = now_utc

        # Construct new canonical event for split entity
        split_event = AtlasUniversalEvent(
            event_id=split_event_id,
            canonical_event_key=split_event_key,
            event_type=primary.event_type,
            event_subtype=primary.event_subtype,
            event_category=primary.event_category,
            title=f"Separated Event: {primary.title}",
            factual_summary=primary.factual_summary,
            lifecycle_status=primary.lifecycle_status,
            verification_status=primary.verification_status,
            occurred_at=primary.occurred_at,
            date_precision=primary.date_precision,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            primary_source_id=primary.primary_source_id,
            event_payload=dict(primary.event_payload),
            source_count=1,
        )

        audit = MergeAuditRecord(
            audit_id=f"audit-split-{primary.event_id}-{split_event_id}-{int(now_utc.timestamp())}",
            operation="SPLIT",
            primary_event_id=primary.event_id,
            secondary_event_id=split_event_id,
            reason=reason,
            authorized_by=authorized_by,
            timestamp_utc=now_utc,
            previous_aliases=prev_aliases,
        )
        self._audit_log.append(audit)
        return primary, split_event, audit

    def get_audit_trail(self) -> List[MergeAuditRecord]:
        """Retrieve complete merge and split audit history."""
        return list(self._audit_log)
