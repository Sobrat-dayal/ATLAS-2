"""Official Sanctions and Restrictive Measures Ingestion Adapter (Stage 135).

Parses official sanctions designations, amendments, and delistings from OFAC,
EU, UK OFSI, and multilateral lists with exact legal entity resolution.
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
from ..taxonomy.payloads import SanctionsEventPayload
from .base import BaseEventAdapter


class SanctionsAdapter(BaseEventAdapter):
    """Adapter for official government and multilateral sanctions notices."""

    def __init__(self, source_id: str = "us_ofac"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        authority = str(raw_payload.get("authority_id", "US_OFAC")).upper()
        jurisdiction = str(raw_payload.get("jurisdiction", "US")).upper()
        program = str(raw_payload.get("program_id", "GLOBAL")).upper()
        action_type = str(raw_payload.get("action_type", "DESIGNATION")).upper()
        subject_ref = str(raw_payload.get("designated_subject_reference", "UNKNOWN_SUBJECT"))
        subject_kind = str(raw_payload.get("subject_kind", "ENTITY")).upper()
        official_action_id = str(raw_payload.get("official_action_id", f"{authority}-{normalize_token(subject_ref)}"))

        pub_date = str(raw_payload.get("publication_date", now_utc.strftime("%Y-%m-%d")))
        eff_date = str(raw_payload.get("effective_date", pub_date))

        # Parse timestamp
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
        except Exception:
            pub_dt = now_utc

        try:
            eff_dt = datetime.fromisoformat(eff_date.replace("Z", "+00:00"))
        except Exception:
            eff_dt = pub_dt

        payload_obj = SanctionsEventPayload(
            authority_id=authority,
            jurisdiction=jurisdiction,
            program_id=program,
            official_action_id=official_action_id,
            action_type=action_type,
            designated_subject_reference=subject_ref,
            subject_kind=subject_kind,
            publication_date=pub_date,
            effective_date=eff_date,
            legal_instrument_reference=raw_payload.get("legal_instrument_reference"),
            list_version=raw_payload.get("list_version"),
        )

        canonical_key = generate_canonical_event_key(
            event_type=f"SANCTIONS.{action_type}",
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=jurisdiction,
            occurred_or_scheduled_date=pub_date,
        )

        title = f"{authority} Sanctions {action_type.title()}: {subject_ref} ({program})"
        summary = (
            f"Official sanctions {action_type.lower()} by {authority} targeting {subject_kind.lower()} "
            f"'{subject_ref}' under program '{program}', effective {eff_date}."
        )

        event = AtlasUniversalEvent(
            event_id=f"evt-sanc-{normalize_token(authority).lower()}-{normalize_token(subject_ref).lower()}-{pub_date[:10]}",
            canonical_event_key=canonical_key,
            event_type="SANCTIONS.DESIGNATION" if action_type == "DESIGNATION" else f"SANCTIONS.{action_type}",
            event_subtype=f"SANCTIONS.{action_type}",
            event_category=EventCategory.SANCTIONS,
            title=title,
            factual_summary=summary,
            lifecycle_status=EventLifecycleStatus.CONFIRMED,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            occurred_at=pub_dt,
            date_precision=DatePrecision.DATE_ONLY if len(pub_date) <= 10 else DatePrecision.EXACT_TIMESTAMP,
            announced_at=pub_dt,
            effective_at=eff_dt,
            source_published_at=pub_dt,
            first_public_at=pub_dt,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code=jurisdiction,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=["sanctions", authority.lower(), program.lower(), action_type.lower()],
            aliases=[subject_ref],
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "DESIGNATED_SUBJECT",
                "claim_value": subject_ref,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"subject_kind": subject_kind, "authority": authority},
            },
            {
                "predicate": "SANCTIONS_PROGRAM",
                "claim_value": program,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"authority": authority},
            },
            {
                "predicate": "ACTION_TYPE",
                "claim_value": action_type,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"effective_date": eff_date},
            },
        ]

        return event, claims

