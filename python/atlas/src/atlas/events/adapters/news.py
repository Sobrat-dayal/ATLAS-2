"""News and Media Candidate Extraction Adapter (Stage 135).

Extracts candidate events from financial news articles, wire releases, and media reports.
CRITICAL INVARIANT (Fixture K):
Articles and rumors remain unverified candidate events (SOURCE_REPORTED or UNVERIFIED)
and are NEVER automatically confirmed as official corporate actions or regulatory events
solely based on news headlines.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasUniversalEvent,
    DatePrecision,
    EventCategory,
    EventGeographicScope,
    EventLifecycleStatus,
    EventSourceRecord,
    EventVerificationStatus,
    GeographicScopeType,
)
from ..identity.canonical import generate_canonical_event_key, normalize_token
from .base import BaseEventAdapter


class NewsEventAdapter(BaseEventAdapter):
    """Adapter for extracting candidate events from news articles while preserving source grounding."""

    def __init__(self, source_id: str = "reuters_wire"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        headline = str(raw_payload.get("headline", raw_payload.get("title", "News Bulletin")))
        body = str(raw_payload.get("body", raw_payload.get("summary", "")))
        publisher = str(raw_payload.get("publisher", self.source_id)).upper()
        pub_date_str = raw_payload.get("published_at", now_utc.isoformat())

        pub_dt = now_utc
        try:
            pub_dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
        except Exception:
            pass

        is_rumor = bool(raw_payload.get("is_rumor", False)) or any(
            token in headline.upper() for token in ["REPORTEDLY", "SOURCES SAY", "RUMORED", "TALKS", "CONSIDERING", "SPECULATING"]
        )

        category_str = raw_payload.get("implied_category", "NEWS_REPORTED")
        if is_rumor:
            verification_status = EventVerificationStatus.UNVERIFIED
            lifecycle_status = EventLifecycleStatus.REPORTED
            subtype = "NEWS.CANDIDATE_RUMOR"
        else:
            verification_status = EventVerificationStatus.SOURCE_REPORTED
            lifecycle_status = EventLifecycleStatus.REPORTED
            subtype = "NEWS.MEDIA_REPORT"

        entity_ref = raw_payload.get("subject_entity", "GENERAL")
        canonical_key = generate_canonical_event_key(
            event_type="NEWS.REPORTED",
            payload={"entity": entity_ref, "headline": headline, "publisher": publisher},
            country_or_jurisdiction=raw_payload.get("country", "GLOBAL"),
            occurred_or_scheduled_date=pub_dt.strftime("%Y-%m-%d"),
        )

        event = AtlasUniversalEvent(
            event_id=f"evt-news-{normalize_token(publisher).lower()}-{pub_dt.strftime('%Y%m%d%H%M')}-{abs(hash(headline)) % 10000}",
            canonical_event_key=canonical_key,
            event_type="NEWS.REPORTED",
            event_subtype=subtype,
            event_category=EventCategory.NEWS_REPORTED,
            title=f"Reported: {headline}",
            factual_summary=f"Media report published by {publisher}: {headline}. Candidate status: {'UNVERIFIED RUMOR' if is_rumor else 'MEDIA REPORTED'}.",
            lifecycle_status=lifecycle_status,
            verification_status=verification_status,
            occurred_at=pub_dt,
            date_precision=DatePrecision.EXACT_TIMESTAMP,
            announced_at=pub_dt,
            source_published_at=pub_dt,
            first_public_at=pub_dt,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.GLOBAL,
                country_code=raw_payload.get("country"),
            ),
            primary_source_id=self.source_id,
            event_payload={
                "headline": headline,
                "publisher": publisher,
                "is_rumor": is_rumor,
                "url": raw_payload.get("url"),
                "subject_entity": entity_ref,
            },
            source_count=1,
            tags=["news", publisher.lower()] + (["rumor", "unverified"] if is_rumor else []),
            aliases=[entity_ref] if entity_ref != "GENERAL" else [],
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "MEDIA_REPORT_HEADLINE",
                "claim_value": headline,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"publisher": publisher, "is_rumor": is_rumor},
            }
        ]
        if entity_ref != "GENERAL":
            claims.append({
                "predicate": "REPORTED_SUBJECT_ENTITY",
                "claim_value": entity_ref,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"status": "UNVERIFIED" if is_rumor else "REPORTED"},
            })

        return event, claims
