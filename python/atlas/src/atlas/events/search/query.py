"""Universal Event Search Engine (Stage 135).

Provides high-performance, permission-aware filtering, multi-parameter matching,
and full-text search across canonical events.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..domain import (
    AtlasUniversalEvent,
    EventCategory,
    EventLifecycleStatus,
    EventVerificationStatus,
)


class EventSearchParams(BaseModel):
    """Parameters for querying canonical events."""
    query: Optional[str] = None
    categories: Optional[List[EventCategory]] = None
    event_types: Optional[List[str]] = None
    lifecycle_statuses: Optional[List[EventLifecycleStatus]] = None
    verification_statuses: Optional[List[EventVerificationStatus]] = None
    jurisdictions: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    time_clock: str = "occurred_at"  # occurred_at, announced_at, published_at, scheduled_for, effective_at
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_retracted: bool = False
    tenant_id: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class EventSearchResult(BaseModel):
    """Response envelope for search results."""
    total_count: int
    returned_count: int
    offset: int
    limit: int
    events: List[AtlasUniversalEvent]


class EventSearchEngine:
    """In-memory and indexed search provider for universal events."""

    def filter_events(
        self,
        events: List[AtlasUniversalEvent],
        params: EventSearchParams,
    ) -> EventSearchResult:
        """Filter and search a list of events using provided criteria."""
        filtered = []

        q_lower = params.query.strip().lower() if params.query else None
        entity_filters = [e.upper() for e in params.entities] if params.entities else None
        jurisdiction_filters = [j.upper() for j in params.jurisdictions] if params.jurisdictions else None
        type_filters = [t.upper() for t in params.event_types] if params.event_types else None

        for evt in events:
            # 1. Multi-tenant isolation check
            if params.tenant_id and evt.tenant_id and evt.tenant_id != params.tenant_id:
                continue

            # 2. Retraction check
            if not params.include_retracted and evt.is_retracted:
                continue

            # 3. Category match
            if params.categories and evt.event_category not in params.categories:
                continue

            # 4. Lifecycle match
            if params.lifecycle_statuses and evt.lifecycle_status not in params.lifecycle_statuses:
                continue

            # 5. Verification match
            if params.verification_statuses and evt.verification_status not in params.verification_statuses:
                continue

            # 6. Event Type match
            if type_filters:
                match_type = any(
                    tf in evt.event_type.upper() or tf in evt.event_subtype.upper()
                    for tf in type_filters
                )
                if not match_type:
                    continue

            # 7. Jurisdiction match
            if jurisdiction_filters:
                scope = evt.geographic_scope
                if not (scope.country_code and scope.country_code.upper() in jurisdiction_filters):
                    continue

            # 8. Entity match
            if entity_filters:
                evt_entities = [a.upper() for a in evt.aliases]
                payload_str = str(evt.event_payload).upper()
                match_ent = any(
                    ent in evt_entities or ent in payload_str or ent in evt.title.upper()
                    for ent in entity_filters
                )
                if not match_ent:
                    continue

            # 9. Temporal Range Check based on specified clock
            clock_dt = self._extract_clock_time(evt, params.time_clock)
            if params.start_date:
                if not clock_dt or clock_dt < params.start_date:
                    continue
            if params.end_date:
                if not clock_dt or clock_dt > params.end_date:
                    continue

            # 10. Free-text search match
            if q_lower:
                searchable_text = (
                    f"{evt.title} {evt.factual_summary} {evt.canonical_event_key} "
                    f"{' '.join(evt.tags)} {' '.join(evt.aliases)}"
                ).lower()
                if q_lower not in searchable_text:
                    continue

            filtered.append(evt)

        total = len(filtered)
        paginated = filtered[params.offset : params.offset + params.limit]

        return EventSearchResult(
            total_count=total,
            returned_count=len(paginated),
            offset=params.offset,
            limit=params.limit,
            events=paginated,
        )

    def _extract_clock_time(self, event: AtlasUniversalEvent, clock: str) -> Optional[datetime]:
        """Extract datetime corresponding to requested time clock."""
        clock_lower = clock.lower()
        if "occurred" in clock_lower:
            return event.occurred_at or event.announced_at or event.source_published_at
        elif "announced" in clock_lower:
            return event.announced_at or event.occurred_at
        elif "published" in clock_lower:
            return event.source_published_at or event.announced_at or event.occurred_at
        elif "scheduled" in clock_lower:
            return event.scheduled_for or event.occurred_at
        elif "effective" in clock_lower:
            return event.effective_at or event.occurred_at
        elif "ingested" in clock_lower:
            return event.first_ingested_at
        return event.occurred_at or event.source_published_at or event.first_ingested_at

