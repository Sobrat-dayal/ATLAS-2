"""Corporate Actions Ingestion Adapter (Stage 135).

Parses corporate actions including mergers, acquisitions, regulatory/shareholder approvals,
closing/completion, dividends, buybacks, and splits.
Enforces distinct milestone preservation (Announced vs Approved vs Completed).
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
from ..taxonomy.payloads import CorporateActionEventPayload
from .base import BaseEventAdapter


class CorporateActionAdapter(BaseEventAdapter):
    """Adapter for corporate events such as mergers, dividends, buybacks, and restructurings."""

    def __init__(self, source_id: str = "sec_edgar"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        issuer = str(raw_payload.get("issuer_reference", "UNKNOWN_ISSUER")).upper()
        action_type = str(raw_payload.get("action_type", "MERGER_ANNOUNCED")).upper()
        target = raw_payload.get("target_reference")
        if target:
            target = str(target).upper()

        deal_val_amt = raw_payload.get("deal_value_amount")
        if deal_val_amt is not None:
            deal_val_amt = float(deal_val_amt)
        deal_val_curr = raw_payload.get("deal_value_currency", "USD")

        decl_date = raw_payload.get("declaration_date")
        rec_date = raw_payload.get("record_date")
        ex_date = raw_payload.get("ex_date")
        pay_date = raw_payload.get("payment_date")
        ratio = raw_payload.get("ratio")

        # Map action_type to lifecycle status
        if "ANNOUNCED" in action_type:
            lifecycle = EventLifecycleStatus.ANNOUNCED
            subtype = "CORPORATE.M_AND_A.ANNOUNCED"
        elif "APPROVED" in action_type:
            lifecycle = EventLifecycleStatus.CONFIRMED
            subtype = "CORPORATE.M_AND_A.APPROVED"
        elif "COMPLETED" in action_type:
            lifecycle = EventLifecycleStatus.OCCURRED
            subtype = "CORPORATE.M_AND_A.COMPLETED"
        elif "DIVIDEND" in action_type:
            lifecycle = EventLifecycleStatus.ANNOUNCED
            subtype = "CORPORATE.DIVIDEND"
        elif "BUYBACK" in action_type:
            lifecycle = EventLifecycleStatus.ANNOUNCED
            subtype = "CORPORATE.BUYBACK"
        elif "SPLIT" in action_type:
            lifecycle = EventLifecycleStatus.ANNOUNCED
            subtype = "CORPORATE.SPLIT"
        else:
            lifecycle = EventLifecycleStatus.REPORTED
            subtype = f"CORPORATE.{action_type}"

        payload_obj = CorporateActionEventPayload(
            issuer_reference=issuer,
            action_type=action_type,
            target_reference=target,
            deal_value_currency=deal_val_curr,
            deal_value_amount=deal_val_amt,
            declaration_date=decl_date,
            record_date=rec_date,
            ex_date=ex_date,
            payment_date=pay_date,
            ratio=ratio,
        )

        canonical_key = generate_canonical_event_key(
            event_type=subtype,
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=raw_payload.get("country", "US"),
            occurred_or_scheduled_date=decl_date or rec_date or now_utc.strftime("%Y-%m-%d"),
        )

        # Title & Summary
        target_str = f" Target: {target}" if target else ""
        amt_str = f" ({deal_val_curr} {deal_val_amt:,.0f})" if deal_val_amt else ""
        title = f"{issuer} {action_type.replace('_', ' ').title()}{target_str}{amt_str}"
        summary = (
            f"Corporate action for {issuer}: {action_type.replace('_', ' ').title()}"
            f"{target_str}{amt_str}."
        )

        event_dt = now_utc
        if decl_date:
            try:
                event_dt = datetime.fromisoformat(decl_date.replace("Z", "+00:00"))
            except Exception:
                pass

        event = AtlasUniversalEvent(
            event_id=f"evt-corp-{normalize_token(issuer).lower()}-{normalize_token(action_type).lower()}-{event_dt.strftime('%Y%m%d')}",
            canonical_event_key=canonical_key,
            event_type="CORPORATE.ACTION",
            event_subtype=subtype,
            event_category=EventCategory.CORPORATE,
            title=title,
            factual_summary=summary,
            lifecycle_status=lifecycle,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED if "sec" in self.source_id.lower() else EventVerificationStatus.SOURCE_REPORTED,
            occurred_at=event_dt,
            date_precision=DatePrecision.DATE_ONLY if decl_date and len(decl_date) <= 10 else DatePrecision.EXACT_TIMESTAMP,
            announced_at=event_dt,
            source_published_at=event_dt,
            first_public_at=event_dt,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code=str(raw_payload.get("country", "US")),
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=["corporate", action_type.lower(), issuer.lower()],
            aliases=[issuer] + ([target] if target else []),
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "ISSUER",
                "claim_value": issuer,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            },
            {
                "predicate": "CORPORATE_ACTION_TYPE",
                "claim_value": action_type,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            },
        ]
        if target:
            claims.append({
                "predicate": "TARGET_ENTITY",
                "claim_value": target,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {},
            })
        if deal_val_amt:
            claims.append({
                "predicate": "DEAL_VALUE",
                "claim_value": deal_val_amt,
                "value_type": "FLOAT",
                "units": deal_val_curr,
                "qualifiers": {},
            })

        return event, claims
