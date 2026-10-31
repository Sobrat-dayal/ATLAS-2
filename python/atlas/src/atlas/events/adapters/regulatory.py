"""Regulatory Actions Ingestion Adapter (Stage 135).

Parses regulatory rule proposals, official adoptions, policy guidance, and
enforcement orders from financial and trade regulators (SEC, CFTC, FCA, ESMA, etc.).
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
from ..taxonomy.payloads import RegulatoryEventPayload
from .base import BaseEventAdapter


class RegulatoryAdapter(BaseEventAdapter):
    """Adapter for official regulatory rulemaking and enforcement notices."""

    def __init__(self, source_id: str = "us_sec"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        agency = str(raw_payload.get("agency", "US_SEC")).upper()
        jurisdiction = str(raw_payload.get("jurisdiction", "US")).upper()
        action_type = str(raw_payload.get("action_type", "RULE_PROPOSAL")).upper()
        matter_ref = str(raw_payload.get("rule_or_matter_reference", "RELEASE-001"))
        status = str(raw_payload.get("status", "ACTIVE"))
        summary = str(raw_payload.get("summary", f"{agency} regulatory action {matter_ref}"))
        eff_date = raw_payload.get("effective_date")
        comment_deadline = raw_payload.get("public_comment_deadline")
        pub_date = raw_payload.get("publication_date", now_utc.strftime("%Y-%m-%d"))

        # Lifecycle mapping
        if "PROPOSAL" in action_type:
            lifecycle = EventLifecycleStatus.PROPOSED
            subtype = "REGULATORY.RULE_PROPOSAL"
        elif "ADOPTION" in action_type:
            lifecycle = EventLifecycleStatus.CONFIRMED
            subtype = "REGULATORY.RULE_ADOPTION"
        elif "ENFORCEMENT" in action_type:
            lifecycle = EventLifecycleStatus.OCCURRED
            subtype = "REGULATORY.ENFORCEMENT_ACTION"
        elif "INVESTIGATION" in action_type:
            lifecycle = EventLifecycleStatus.ANNOUNCED
            subtype = "REGULATORY.INVESTIGATION"
        else:
            lifecycle = EventLifecycleStatus.REPORTED
            subtype = f"REGULATORY.{action_type}"

        payload_obj = RegulatoryEventPayload(
            agency=agency,
            jurisdiction=jurisdiction,
            action_type=action_type,
            rule_or_matter_reference=matter_ref,
            status=status,
            summary=summary,
            effective_date=eff_date,
            public_comment_deadline=comment_deadline,
        )

        canonical_key = generate_canonical_event_key(
            event_type=subtype,
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=jurisdiction,
            occurred_or_scheduled_date=pub_date,
        )

        pub_dt = now_utc
        try:
            pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
        except Exception:
            pass

        title = f"{agency} {action_type.replace('_', ' ').title()}: {matter_ref}"

        event = AtlasUniversalEvent(
            event_id=f"evt-reg-{normalize_token(agency).lower()}-{normalize_token(matter_ref).lower()}-{pub_dt.strftime('%Y%m%d')}",
            canonical_event_key=canonical_key,
            event_type="REGULATORY.ACTION",
            event_subtype=subtype,
            event_category=EventCategory.REGULATORY,
            title=title,
            factual_summary=summary,
            lifecycle_status=lifecycle,
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
                country_code=jurisdiction,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=["regulatory", agency.lower(), action_type.lower()],
            aliases=[matter_ref],
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "REGULATORY_AGENCY",
                "claim_value": agency,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"jurisdiction": jurisdiction},
            },
            {
                "predicate": "RULE_REFERENCE",
                "claim_value": matter_ref,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"action_type": action_type},
            },
        ]
        if eff_date:
            claims.append({
                "predicate": "EFFECTIVE_DATE",
                "claim_value": eff_date,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            })

        return event, claims
