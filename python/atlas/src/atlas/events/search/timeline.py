"""Unified Multi-Clock Event Timeline (Stage 135).

Provides chronological multi-clock event streaming, upcoming scheduled schedules,
and recent historical event streams without look-ahead bias.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ..domain import AtlasUniversalEvent, EventLifecycleStatus


class TimelineBucket(BaseModel):
    """A day or time bucket for grouped timeline display."""
    bucket_date: str  # YYYY-MM-DD
    event_count: int
    events: List[AtlasUniversalEvent]


class TimelineResponse(BaseModel):
    """Timeline feed response."""
    clock_used: str
    total_events: int
    buckets: List[TimelineBucket]
    events: List[AtlasUniversalEvent]


class EventTimelineEngine:
    """Arranges canonical events along multiple temporal axes."""

    def build_timeline(
        self,
        events: List[AtlasUniversalEvent],
        clock: str = "occurred_at",
        ascending: bool = False,
        limit: int = 100,
        group_by_date: bool = True,
    ) -> TimelineResponse:
        """Sort events by chosen clock and optionally partition into date buckets."""
        now_utc = datetime.now(timezone.utc)

        # 1. Filter out retracted events from standard timeline
        active_events = [e for e in events if not e.is_retracted]

        # 2. Extract clock key for sorting
        def sort_key(e: AtlasUniversalEvent):
            t = self._get_clock(e, clock)
            return t or datetime.min.replace(tzinfo=timezone.utc)

        sorted_events = sorted(active_events, key=sort_key, reverse=not ascending)
        limited_events = sorted_events[:limit]

        buckets: List[TimelineBucket] = []
        if group_by_date:
            bucket_map: Dict[str, List[AtlasUniversalEvent]] = {}
            for e in limited_events:
                t = self._get_clock(e, clock)
                date_str = t.strftime("%Y-%m-%d") if t else "UNDATED"
                bucket_map.setdefault(date_str, []).append(e)

            for d_str, ev_list in bucket_map.items():
                buckets.append(
                    TimelineBucket(
                        bucket_date=d_str,
                        event_count=len(ev_list),
                        events=ev_list,
                    )
                )

        return TimelineResponse(
            clock_used=clock,
            total_events=len(limited_events),
            buckets=buckets,
            events=limited_events,
        )

    def get_upcoming_schedule(
        self,
        events: List[AtlasUniversalEvent],
        limit: int = 50,
    ) -> List[AtlasUniversalEvent]:
        """Get scheduled upcoming events (earnings releases, FOMC meetings, economic data)."""
        now_utc = datetime.now(timezone.utc)
        upcoming = []

        for e in events:
            if e.is_retracted:
                continue
            if e.lifecycle_status in [EventLifecycleStatus.SCHEDULED, EventLifecycleStatus.PROPOSED]:
                upcoming.append(e)
            elif e.scheduled_for and e.scheduled_for > now_utc:
                upcoming.append(e)

        # Sort ascending by scheduled_for
        upcoming.sort(key=lambda x: x.scheduled_for or x.occurred_at or datetime.max.replace(tzinfo=timezone.utc))
        return upcoming[:limit]

    def get_recent_events(
        self,
        events: List[AtlasUniversalEvent],
        limit: int = 50,
    ) -> List[AtlasUniversalEvent]:
        """Get recently occurred or announced events."""
        now_utc = datetime.now(timezone.utc)
        recent = []

        for e in events:
            if e.is_retracted:
                continue
            t = e.occurred_at or e.source_published_at or e.announced_at
            if t and t <= now_utc:
                recent.append(e)

        recent.sort(
            key=lambda x: x.occurred_at or x.source_published_at or x.announced_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return recent[:limit]

    def _get_clock(self, e: AtlasUniversalEvent, clock: str) -> Optional[datetime]:
        clock_lower = clock.lower()
        if "occurred" in clock_lower:
            return e.occurred_at or e.announced_at or e.source_published_at
        elif "published" in clock_lower:
            return e.source_published_at or e.occurred_at
        elif "scheduled" in clock_lower:
            return e.scheduled_for or e.occurred_at
        elif "announced" in clock_lower:
            return e.announced_at or e.occurred_at
        elif "effective" in clock_lower:
            return e.effective_at or e.occurred_at
        return e.occurred_at or e.source_published_at or e.first_ingested_at

