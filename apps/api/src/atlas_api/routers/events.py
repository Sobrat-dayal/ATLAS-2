"""FastAPI Router for ATLAS Universal Event Model Endpoints (Stage 135).

Prefix: /api/v1/events
Provides canonical financial, economic, corporate, regulatory, sanctions, geopolitical,
and physical-world event access with multi-clock temporal history, bitemporal as-of evaluation,
multi-source deduplication, evidence & claim resolution, and timeline streaming.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.events import (
    AtlasUniversalEvent,
    AtlasUniversalEventService,
    EventCategory,
    EventClaim,
    EventEvidence,
    EventLifecycleStatus,
    EventRevision,
    EventSourceRecord,
    EventVerificationStatus,
)
from atlas.events.errors import (
    EventDomainError,
    EventLookAheadViolationError,
    EventMergeSplitValidationError,
    EventNotFoundError,
    EventRetractedError,
    EventSourceNotAuthorizedError,
)
from atlas.events.identity.canonical import generate_canonical_event_key
from atlas.events.identity.deduplication import MatchConfidence
from atlas.events.search.query import EventSearchParams, EventSearchResult
from atlas.events.search.timeline import TimelineResponse

from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/events", tags=["events"])

# Singleton service instance with seed fixtures loaded
_events_service = AtlasUniversalEventService(populate_seed_data=True)


def get_events_service() -> AtlasUniversalEventService:
    """Dependency provider for the AtlasUniversalEventService."""
    return _events_service


# -------------------------------------------------------------
# Request & Response DTOs
# -------------------------------------------------------------
class AsOfQueryRequest(BaseModel):
    as_of_time: datetime
    event_id: Optional[str] = None
    tenant_id: Optional[str] = None


class MergeEventsRequest(BaseModel):
    target_event_id: str
    source_event_ids: List[str]
    reason: str


class SplitEventRequest(BaseModel):
    event_id: str
    sub_events_spec: List[Dict[str, Any]]
    reason: str


class RetractEventRequest(BaseModel):
    event_id: str
    reason: str


class DeduplicateCheckRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    source_event_id: Optional[str] = None
    country_or_jurisdiction: Optional[str] = None
    occurred_or_scheduled_date: Optional[str] = None


class DeduplicateCheckResponse(BaseModel):
    canonical_event_key: str
    match_found: bool
    matched_event_id: Optional[str] = None
    confidence: str
    match_reason: str


class ResolveReviewRequest(BaseModel):
    resolution: str  # CONFIRMED_MERGE or CONFIRMED_SEPARATE


# -------------------------------------------------------------
# Router Endpoints
# -------------------------------------------------------------
@router.get("/capabilities", response_model=Dict[str, Any])
def get_capabilities(
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> Dict[str, Any]:
    """Retrieve platform capabilities for the Universal Event Model."""
    return service.get_capabilities()


@router.get("/types", response_model=Dict[str, Any])
def get_event_types(
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> Dict[str, Any]:
    """Retrieve the taxonomy of canonical event categories and supported subtypes."""
    return {
        "categories": [c.value for c in EventCategory],
        "taxonomy": service.taxonomy.list_categories_with_subtypes(),
    }


@router.get("/sources", response_model=List[Dict[str, str]])
def get_sources(
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[Dict[str, str]]:
    """List registered event data providers and their licensing policies."""
    return service.sources.list_sources()


@router.get("/providers/status", response_model=List[Dict[str, str]])
def get_providers_status(
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[Dict[str, str]]:
    """List provider feed health, licensing policies, and retention statuses."""
    return service.sources.list_sources()


@router.get("/search", response_model=EventSearchResult)
def search_events_get(
    q: Optional[str] = Query(None, description="Free text search query"),
    category: Optional[List[str]] = Query(None, description="Event categories"),
    lifecycle: Optional[List[str]] = Query(None, description="Lifecycle status filters"),
    verification: Optional[List[str]] = Query(None, description="Verification status filters"),
    jurisdiction: Optional[List[str]] = Query(None, description="Jurisdiction/country code"),
    entity: Optional[List[str]] = Query(None, description="Subject entity / ticker"),
    clock: str = Query("occurred_at", description="Time clock used for sorting/range filtering"),
    start_date: Optional[datetime] = Query(None, description="Start date ISO timestamp"),
    end_date: Optional[datetime] = Query(None, description="End date ISO timestamp"),
    include_retracted: bool = Query(False, description="Whether to include retracted events"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> EventSearchResult:
    """Search and filter canonical events via GET query parameters."""
    cat_enums = [EventCategory(c) for c in category if c in EventCategory._value2member_map_] if category else None
    life_enums = [EventLifecycleStatus(l) for l in lifecycle if l in EventLifecycleStatus._value2member_map_] if lifecycle else None
    ver_enums = [EventVerificationStatus(v) for v in verification if v in EventVerificationStatus._value2member_map_] if verification else None

    params = EventSearchParams(
        query=q,
        categories=cat_enums,
        lifecycle_statuses=life_enums,
        verification_statuses=ver_enums,
        jurisdictions=jurisdiction,
        entities=entity,
        time_clock=clock,
        start_date=start_date,
        end_date=end_date,
        include_retracted=include_retracted,
        limit=limit,
        offset=offset,
    )
    return service.search_events(params)


@router.post("/query", response_model=EventSearchResult)
def query_events_post(
    params: EventSearchParams,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> EventSearchResult:
    """Rich structured search across the Universal Event database."""
    return service.search_events(params)


@router.get("/timeline", response_model=TimelineResponse)
def get_timeline(
    clock: str = Query("occurred_at", description="Timeline clock: occurred_at, announced_at, published_at, scheduled_for, effective_at"),
    ascending: bool = Query(False, description="Sort ascending chronologically"),
    limit: int = Query(100, ge=1, le=500),
    group_by_date: bool = Query(True, description="Group timeline items into date buckets"),
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> TimelineResponse:
    """Stream events ordered along a chosen temporal clock."""
    return service.get_timeline(
        clock=clock,
        ascending=ascending,
        limit=limit,
        group_by_date=group_by_date,
    )


@router.get("/upcoming", response_model=List[AtlasUniversalEvent])
def get_upcoming_events(
    limit: int = Query(50, ge=1, le=200),
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[AtlasUniversalEvent]:
    """Retrieve scheduled upcoming events (earnings, FOMC meetings, economic releases)."""
    return service.get_upcoming_schedule(limit=limit)


@router.get("/recent", response_model=List[AtlasUniversalEvent])
def get_recent_events(
    limit: int = Query(50, ge=1, le=200),
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[AtlasUniversalEvent]:
    """Retrieve recently verified historical events."""
    return service.get_recent_events(limit=limit)


@router.post("/as-of", response_model=List[AtlasUniversalEvent])
def as_of_query(
    body: AsOfQueryRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[AtlasUniversalEvent]:
    """Point-in-time historical evaluation enforcing Zero Look-Ahead Bias."""
    try:
        return service.as_of_query(
            as_of_time=body.as_of_time,
            event_id=body.event_id,
            tenant_id=body.tenant_id,
        )
    except EventLookAheadViolationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/deduplicate", response_model=DeduplicateCheckResponse)
def check_deduplication(
    body: DeduplicateCheckRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> DeduplicateCheckResponse:
    """Check candidate event deduplication without modifying persistent store."""
    canonical_key = generate_canonical_event_key(
        event_type=body.event_type,
        payload=body.payload,
        source_event_id=body.source_event_id,
        country_or_jurisdiction=body.country_or_jurisdiction,
        occurred_or_scheduled_date=body.occurred_or_scheduled_date,
    )

    all_events = list(service._events.values())
    match_id, confidence, match_reason = service.dedup_engine.find_matching_event(
        AtlasUniversalEvent(
            event_id="evt-candidate-check",
            canonical_event_key=canonical_key,
            event_type=body.event_type,
            event_subtype=body.event_type,
            event_category=EventCategory.OTHER_VERIFIED_EVENT,
            title="Candidate check",
            factual_summary="Candidate check",
            lifecycle_status=EventLifecycleStatus.REPORTED,
            verification_status=EventVerificationStatus.UNVERIFIED,
            first_ingested_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            primary_source_id="candidate_check",
            event_payload=body.payload,
        ),
        all_events,
    )

    return DeduplicateCheckResponse(
        canonical_event_key=canonical_key,
        match_found=bool(match_id),
        matched_event_id=match_id,
        confidence=confidence.value,
        match_reason=match_reason,
    )


@router.post("/merge", response_model=AtlasUniversalEvent)
def merge_events(
    body: MergeEventsRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> AtlasUniversalEvent:
    """Merge duplicate canonical events safely into the target event."""
    try:
        return service.merge_events(
            target_event_id=body.target_event_id,
            source_event_ids=body.source_event_ids,
            reason=body.reason,
            user_id="analyst",
        )
    except (EventNotFoundError, EventMergeSplitValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/split", response_model=List[AtlasUniversalEvent])
def split_event(
    body: SplitEventRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[AtlasUniversalEvent]:
    """Split a mistakenly merged canonical event into separate events."""
    try:
        return service.split_event(
            event_id=body.event_id,
            sub_events_spec=body.sub_events_spec,
            reason=body.reason,
            user_id="analyst",
        )
    except (EventNotFoundError, EventMergeSplitValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/retract", response_model=AtlasUniversalEvent)
def retract_event(
    body: RetractEventRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> AtlasUniversalEvent:
    """Formally retract and tombstone an erroneous or fraudulent event."""
    try:
        return service.retract_event(
            event_id=body.event_id,
            reason=body.reason,
            user_id="compliance_officer",
        )
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/review-queue", response_model=List[Any])
def get_review_queue(
    status: Optional[str] = Query(None, description="Review status filter: PENDING, RESOLVED"),
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[Any]:
    """List ambiguous match candidate events awaiting analyst review."""
    return service.get_review_items(status=status)


@router.post("/review-queue/{review_id}/resolve", response_model=Any)
def resolve_review_item(
    review_id: str,
    body: ResolveReviewRequest,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> Any:
    """Resolve an ambiguous candidate review item."""
    try:
        return service.resolve_review_item(
            review_id=review_id,
            resolution=body.resolution,
            user_id="analyst",
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{event_id}", response_model=AtlasUniversalEvent)
def get_event(
    event_id: str,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> AtlasUniversalEvent:
    """Retrieve full canonical event details by event_id."""
    try:
        return service.get_event(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{event_id}/evidence", response_model=List[EventEvidence])
def get_event_evidence(
    event_id: str,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[EventEvidence]:
    """Retrieve all supporting source documents and snippets for an event."""
    try:
        return service.get_evidence(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{event_id}/claims", response_model=List[EventClaim])
def get_event_claims(
    event_id: str,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[EventClaim]:
    """Retrieve granular factual claims and conflict evaluations for an event."""
    try:
        return service.get_claims(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{event_id}/revisions", response_model=List[EventRevision])
def get_event_revisions(
    event_id: str,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[EventRevision]:
    """Retrieve complete bitemporal revision history and audit log for an event."""
    try:
        return service.get_revisions(event_id)
    except EventNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{event_id}/sources", response_model=List[EventSourceRecord])
def get_event_sources(
    event_id: str,
    service: AtlasUniversalEventService = Depends(get_events_service),
) -> List[EventSourceRecord]:
    """Retrieve all external source records that provided evidence for an event."""
    evidence_list = service.get_evidence(event_id)
    records: List[EventSourceRecord] = []
    for ev in evidence_list:
        rec = service.sources.get_source_record(ev.source_record_id)
        if rec:
            records.append(rec)
    return records
