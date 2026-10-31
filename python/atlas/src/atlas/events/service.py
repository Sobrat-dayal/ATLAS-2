"""Atlas Universal Event Domain Service (Stage 135).

Orchestrates canonical event ingestion, multi-clock temporal history, zero look-ahead as-of evaluation,
multi-source deduplication, evidence & claim resolution, and timeline streaming.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .adapters.base import BaseEventAdapter
from .adapters.central_bank import CentralBankAdapter
from .adapters.corporate_action import CorporateActionAdapter
from .adapters.earnings import EarningsAdapter
from .adapters.economic_release import EconomicReleaseAdapter
from .adapters.geopolitical import GeopoliticalAdapter
from .adapters.news import NewsEventAdapter
from .adapters.physical_world import PhysicalWorldAdapter
from .adapters.sanctions import SanctionsAdapter
from .domain import (
    AtlasUniversalEvent,
    DatePrecision,
    EventCategory,
    EventClaim,
    EventEvidence,
    EventLifecycleStatus,
    EventRevision,
    EventSourceRecord,
    EventVerificationStatus,
    EvidenceRole,
)
from .errors import (
    EventDomainError,
    EventNotFoundError,
    EventRetractedError,
    EventSourceNotAuthorizedError,
)
from .evidence.claims import EventClaimRegistry
from .evidence.review import EventReviewQueue, ReviewItem
from .evidence.sources import EventSourceRegistry
from .identity.canonical import generate_canonical_event_key
from .identity.deduplication import DeduplicationEngine, MatchConfidence
from .identity.merge_split import MergeSplitManager
from .search.query import EventSearchEngine, EventSearchParams, EventSearchResult
from .search.timeline import EventTimelineEngine, TimelineResponse
from .seed import build_stage135_fixtures
from .taxonomy.registry import EventTaxonomyRegistry
from .temporal.bitemporal import BitemporalEngine
from .temporal.revisions import RevisionManager


class AtlasUniversalEventService:
    """Master orchestrator for the Stage 135 Universal Event Model."""

    def __init__(self, populate_seed_data: bool = True):
        # 1. Core subsystems
        self.taxonomy = EventTaxonomyRegistry()
        self.dedup_engine = DeduplicationEngine()
        self.merge_split = MergeSplitManager()
        self.bitemporal = BitemporalEngine()
        self.revisions = RevisionManager()
        self.sources = EventSourceRegistry()
        self.claims = EventClaimRegistry()
        self.review_queue = EventReviewQueue()
        self.search = EventSearchEngine()
        self.timeline = EventTimelineEngine()

        # 2. Ingestion Adapters
        self.adapters: Dict[str, BaseEventAdapter] = {
            "earnings": EarningsAdapter(),
            "economic_release": EconomicReleaseAdapter(),
            "central_bank": CentralBankAdapter(),
            "sanctions": SanctionsAdapter(),
            "corporate_action": CorporateActionAdapter(),
            "geopolitical": GeopoliticalAdapter(),
            "news": NewsEventAdapter(),
            "physical_world": PhysicalWorldAdapter(),
        }

        # 3. In-memory data store
        self._events: Dict[str, AtlasUniversalEvent] = {}
        self._evidence: Dict[str, List[EventEvidence]] = {}

        if populate_seed_data:
            self._load_seed_fixtures()

    def _load_seed_fixtures(self) -> None:
        """Seed reference dataset covering Fixtures A through R."""
        evs, srcs, evis, clms, revs = build_stage135_fixtures()

        for s in srcs:
            self.sources.register_source(s)

        for e in evs:
            self._events[e.event_id] = e

        for ev in evis:
            self._evidence.setdefault(ev.event_id, []).append(ev)

        for c in clms:
            self.claims.record_claim(c)

        for r in revs:
            self.revisions.record_revision(r)

    def get_capabilities(self) -> Dict[str, Any]:
        """Return supported capabilities of the Universal Event platform."""
        return {
            "stage": 135,
            "version": "1.0.0",
            "categories": [c.value for c in EventCategory],
            "lifecycle_statuses": [s.value for s in EventLifecycleStatus],
            "verification_statuses": [v.value for v in EventVerificationStatus],
            "date_precisions": [p.value for p in DatePrecision],
            "supported_clocks": [
                "occurred_at",
                "announced_at",
                "source_published_at",
                "scheduled_for",
                "effective_at",
                "first_ingested_at",
            ],
            "bitemporal_support": True,
            "zero_lookahead_guarantee": True,
            "adapters": list(self.adapters.keys()),
            "total_canonical_events": len(self._events),
        }

    def get_event(self, event_id: str, tenant_id: Optional[str] = None) -> AtlasUniversalEvent:
        """Fetch single event by ID enforcing tenant isolation."""
        event = self._events.get(event_id)
        if not event:
            raise EventNotFoundError(f"Event with id '{event_id}' not found.")
        if tenant_id and event.tenant_id and event.tenant_id != tenant_id:
            raise EventNotFoundError(f"Event with id '{event_id}' not accessible to tenant.")
        return event

    def get_evidence(self, event_id: str) -> List[EventEvidence]:
        """Fetch evidence items attached to an event."""
        self.get_event(event_id)
        return self._evidence.get(event_id, [])

    def get_claims(self, event_id: str) -> List[EventClaim]:
        """Fetch granular source claims asserted for an event."""
        self.get_event(event_id)
        return self.claims.get_claims_for_event(event_id)

    def get_revisions(self, event_id: str) -> List[EventRevision]:
        """Fetch historical revision audit chain for an event."""
        self.get_event(event_id)
        return self.revisions.get_revisions_for_event(event_id)

    def search_events(self, params: EventSearchParams) -> EventSearchResult:
        """Filter events with full-text search, categories, and date ranges."""
        all_events = list(self._events.values())
        return self.search.filter_events(all_events, params)

    def get_timeline(
        self,
        clock: str = "occurred_at",
        ascending: bool = False,
        limit: int = 100,
        group_by_date: bool = True,
    ) -> TimelineResponse:
        """Stream events along chosen temporal axis."""
        all_events = list(self._events.values())
        return self.timeline.build_timeline(
            all_events,
            clock=clock,
            ascending=ascending,
            limit=limit,
            group_by_date=group_by_date,
        )

    def get_upcoming_schedule(self, limit: int = 50) -> List[AtlasUniversalEvent]:
        """Get upcoming scheduled economic, earnings, and regulatory events."""
        return self.timeline.get_upcoming_schedule(list(self._events.values()), limit=limit)

    def get_recent_events(self, limit: int = 50) -> List[AtlasUniversalEvent]:
        """Get recent verified historical events."""
        return self.timeline.get_recent_events(list(self._events.values()), limit=limit)

    def as_of_query(
        self,
        as_of_time: datetime,
        event_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasUniversalEvent]:
        """Evaluate events as known at as_of_time with zero look-ahead bias."""
        all_events = list(self._events.values())
        if event_id:
            event = self.get_event(event_id, tenant_id=tenant_id)
            revs = self.revisions.get_revisions_for_event(event_id)
            historical = self.bitemporal.as_of_event(event, revs, as_of_time)
            return [historical] if historical else []

        all_revs = self.revisions.get_all_revisions()
        return self.bitemporal.as_of_dataset(all_events, all_revs, as_of_time, tenant_id=tenant_id)

    def ingest_source_event(
        self,
        adapter_name: str,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, bool, MatchConfidence]:
        """Ingest event from an external source via typed adapter.
        
        Returns:
            (canonical_event, is_new_event, match_confidence)
        """
        adapter = self.adapters.get(adapter_name.lower())
        if not adapter:
            raise EventDomainError(f"Ingestion adapter '{adapter_name}' not registered.")

        if source_record:
            if not self.sources.is_source_authorized(source_record.source_id):
                raise EventSourceNotAuthorizedError(f"Source '{source_record.source_id}' is not authorized or licensed.")
            self.sources.register_source(source_record)

        parsed_event, extracted_claims = adapter.parse_source_payload(raw_payload, source_record)

        # Check deduplication against existing events
        existing_list = list(self._events.values())
        match_id, confidence, match_reason = self.dedup_engine.find_matching_event(parsed_event, existing_list)

        if match_id and confidence == MatchConfidence.EXACT_CANONICAL_KEY:
            # Match found! Attach evidence and claims to existing canonical event
            canonical = self._events[match_id]
            canonical.source_count += 1
            canonical.updated_at = datetime.now(timezone.utc)

            # Record evidence link
            if source_record:
                evidence_id = f"evi-{canonical.event_id}-{source_record.source_record_id}"
                ev = EventEvidence(
                    evidence_id=evidence_id,
                    event_id=canonical.event_id,
                    source_record_id=source_record.source_record_id,
                    evidence_role=EvidenceRole.CORROBORATING_SOURCE,
                    verification_status=parsed_event.verification_status,
                    snippet=raw_payload.get("summary") or parsed_event.factual_summary,
                    recorded_at=datetime.now(timezone.utc),
                )
                self._evidence.setdefault(canonical.event_id, []).append(ev)

            # Record claims
            for c_dict in extracted_claims:
                claim_id = f"clm-{canonical.event_id}-{len(self.claims.get_claims_for_event(canonical.event_id)) + 1}"
                clm = EventClaim(
                    claim_id=claim_id,
                    event_id=canonical.event_id,
                    source_record_id=source_record.source_record_id if source_record else "inline",
                    predicate=c_dict["predicate"],
                    claim_value=c_dict["claim_value"],
                    value_type=c_dict.get("value_type", "STRING"),
                    units=c_dict.get("units"),
                    qualifiers=c_dict.get("qualifiers", {}),
                    extracted_at=datetime.now(timezone.utc),
                    verification_status=parsed_event.verification_status,
                )
                self.claims.record_claim(clm)

            return canonical, False, confidence

        elif match_id and confidence == MatchConfidence.AMBIGUOUS:
            # Route to review queue without blindly merging or duplicating
            self.review_queue.submit_review(
                event_a_id=match_id,
                event_b_id=parsed_event.event_id,
                reason=f"Ambiguous match confidence: {match_reason}",
                context={"candidate_event": parsed_event.model_dump()},
            )

        # Register as a new canonical event
        self._events[parsed_event.event_id] = parsed_event

        if source_record:
            evidence_id = f"evi-{parsed_event.event_id}-{source_record.source_record_id}"
            ev = EventEvidence(
                evidence_id=evidence_id,
                event_id=parsed_event.event_id,
                source_record_id=source_record.source_record_id,
                evidence_role=EvidenceRole.PRIMARY_SOURCE,
                verification_status=parsed_event.verification_status,
                snippet=parsed_event.factual_summary,
                recorded_at=datetime.now(timezone.utc),
            )
            self._evidence.setdefault(parsed_event.event_id, []).append(ev)

        for c_dict in extracted_claims:
            claim_id = f"clm-{parsed_event.event_id}-{len(self.claims.get_claims_for_event(parsed_event.event_id)) + 1}"
            clm = EventClaim(
                claim_id=claim_id,
                event_id=parsed_event.event_id,
                source_record_id=source_record.source_record_id if source_record else "inline",
                predicate=c_dict["predicate"],
                claim_value=c_dict["claim_value"],
                value_type=c_dict.get("value_type", "STRING"),
                units=c_dict.get("units"),
                qualifiers=c_dict.get("qualifiers", {}),
                extracted_at=datetime.now(timezone.utc),
                verification_status=parsed_event.verification_status,
            )
            self.claims.record_claim(clm)

        return parsed_event, True, MatchConfidence.DISTINCT

    def merge_events(
        self,
        target_event_id: str,
        source_event_ids: List[str],
        reason: str,
        user_id: str,
    ) -> AtlasUniversalEvent:
        """Merge duplicate canonical events safely into target_event_id."""
        target = self.get_event(target_event_id)
        source_events = [self.get_event(sid) for sid in source_event_ids]

        merged, audit = self.merge_split.merge_events(target, source_events, reason=reason, user_id=user_id)

        # Migrate evidence and claims
        for sid in source_event_ids:
            if sid in self._evidence:
                ev_list = self._evidence.pop(sid)
                for ev in ev_list:
                    ev.event_id = target_event_id
                self._evidence.setdefault(target_event_id, []).extend(ev_list)

            self.claims.migrate_claims_to_event(sid, target_event_id)
            # Remove source event from active set
            self._events.pop(sid, None)

        self._events[target_event_id] = merged
        return merged

    def split_event(
        self,
        event_id: str,
        sub_events_spec: List[Dict[str, Any]],
        reason: str,
        user_id: str,
    ) -> List[AtlasUniversalEvent]:
        """Split a mistakenly unified event into distinct valid canonical events."""
        original = self.get_event(event_id)
        new_events = self.merge_split.split_event(original, sub_events_spec, reason=reason, user_id=user_id)

        # Remove original event
        self._events.pop(event_id, None)

        # Register split events
        for ne in new_events:
            self._events[ne.event_id] = ne

        return new_events

    def retract_event(self, event_id: str, reason: str, user_id: str) -> AtlasUniversalEvent:
        """Formally retract and tombstone a discredited or erroneous event."""
        event = self.get_event(event_id)
        now_utc = datetime.now(timezone.utc)

        rev = self.revisions.retract_event(event, reason=reason, recorded_at=now_utc)
        event.is_retracted = True
        event.retraction_reason = reason
        event.lifecycle_status = EventLifecycleStatus.RETRACTED
        event.verification_status = EventVerificationStatus.REJECTED
        event.updated_at = now_utc
        event.current_revision_number += 1

        return event

    def get_review_items(self, status: Optional[str] = None) -> List[ReviewItem]:
        """List ambiguous match review items."""
        return self.review_queue.list_reviews(status=status)

    def resolve_review_item(self, review_id: str, resolution: str, user_id: str) -> ReviewItem:
        """Resolve a review item (CONFIRMED_MERGE or CONFIRMED_SEPARATE)."""
        return self.review_queue.resolve_review(review_id, resolution=resolution, user_id=user_id)
