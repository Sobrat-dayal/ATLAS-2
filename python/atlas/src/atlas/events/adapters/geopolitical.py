"""Geopolitical Events Ingestion Adapter (Stage 135).

Parses official diplomatic declarations, treaty accessions/withdrawals, trade restrictions,
tariffs, and sovereign political actions.
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
from ..taxonomy.payloads import GeopoliticalEventPayload
from .base import BaseEventAdapter


class GeopoliticalAdapter(BaseEventAdapter):
    """Adapter for official geopolitical declarations, agreements, and restrictions."""

    def __init__(self, source_id: str = "state_department"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        actor = str(raw_payload.get("actor_jurisdiction", "US")).upper()
        target = raw_payload.get("target_jurisdiction")
        if target:
            target = str(target).upper()
        ev_type = str(raw_payload.get("event_type", "OFFICIAL_STATEMENT")).upper()
        speaker = raw_payload.get("statement_speaker")
        claim_type = str(raw_payload.get("claim_type", "OFFICIAL_STATEMENT"))
        summary = str(raw_payload.get("summary", f"Geopolitical action by {actor}"))
        treaty_name = raw_payload.get("treaty_or_accord_name")
        pub_date = raw_payload.get("publication_date", now_utc.strftime("%Y-%m-%d"))

        payload_obj = GeopoliticalEventPayload(
            actor_jurisdiction=actor,
            target_jurisdiction=target,
            event_type=ev_type,
            statement_speaker=speaker,
            claim_type=claim_type,
            summary=summary,
            treaty_or_accord_name=treaty_name,
        )

        canonical_key = generate_canonical_event_key(
            event_type=f"GEOPOLITICAL.{ev_type}",
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=actor,
            occurred_or_scheduled_date=pub_date,
        )

        pub_dt = now_utc
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
        except Exception:
            pass

        target_text = f" regarding {target}" if target else ""
        title = f"{actor} Geopolitical Action: {ev_type.replace('_', ' ').title()}{target_text}"

        event = AtlasUniversalEvent(
            event_id=f"evt-geo-{normalize_token(actor).lower()}-{normalize_token(ev_type).lower()}-{pub_dt.strftime('%Y%m%d')}",
            canonical_event_key=canonical_key,
            event_type="GEOPOLITICAL.ACTION",
            event_subtype=f"GEOPOLITICAL.{ev_type}",
            event_category=EventCategory.GEOPOLITICAL,
            title=title,
            factual_summary=summary,
            lifecycle_status=EventLifecycleStatus.CONFIRMED,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            occurred_at=pub_dt,
            date_precision=DatePrecision.DATE_ONLY if len(pub_date) <= 10 else DatePrecision.EXACT_TIMESTAMP,
            announced_at=pub_dt,
            source_published_at=pub_dt,
            first_public_at=pub_dt,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code=actor,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=["geopolitical", actor.lower(), ev_type.lower()],
            aliases=[treaty_name] if treaty_name else [],
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "ACTOR_JURISDICTION",
                "claim_value": actor,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            },
            {
                "predicate": "GEOPOLITICAL_ACTION",
                "claim_value": ev_type,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"speaker": speaker} if speaker else {},
            },
        ]
        if target:
            claims.append({
                "predicate": "TARGET_JURISDICTION",
                "claim_value": target,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            })

        return event, claims
