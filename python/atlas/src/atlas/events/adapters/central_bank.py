"""Central Bank Policy Rate Decisions Adapter (Stage 135).

Parses central bank interest rate decisions, policy statements, and target ranges.
Enforces accurate basis-point mathematical evaluation and target range preservation.
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
from ..identity.canonical import generate_canonical_event_key
from ..taxonomy.payloads import CentralBankEventPayload
from .base import BaseEventAdapter


class CentralBankAdapter(BaseEventAdapter):
    """Adapter for official central bank monetary policy rate decisions."""

    def __init__(self, source_id: str = "federal_reserve"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)
        cb = str(raw_payload.get("central_bank_reference", "US_FED")).upper()
        jurisdiction = str(raw_payload.get("jurisdiction", "US")).upper()
        instrument = str(raw_payload.get("policy_instrument", "FED_FUNDS_TARGET_RATE"))

        dec_time = raw_payload.get("decision_time", now_utc)
        if isinstance(dec_time, str):
            dec_time = datetime.fromisoformat(dec_time.replace("Z", "+00:00"))

        eff_time = raw_payload.get("effective_time")
        if isinstance(eff_time, str):
            eff_time = datetime.fromisoformat(eff_time.replace("Z", "+00:00"))

        prev_rate = raw_payload.get("previous_rate")
        new_rate = raw_payload.get("new_rate")
        target_lower = raw_payload.get("target_range_lower")
        target_upper = raw_payload.get("target_range_upper")

        payload_obj = CentralBankEventPayload(
            central_bank_reference=cb,
            jurisdiction=jurisdiction,
            policy_instrument=instrument,
            decision_time=dec_time,
            effective_time=eff_time,
            previous_rate=prev_rate,
            new_rate=new_rate,
            target_range_lower=target_lower,
            target_range_upper=target_upper,
            rate_unit=str(raw_payload.get("rate_unit", "PERCENT")),
            statement_url=raw_payload.get("statement_url"),
        )
        payload_obj.compute_change_bps()

        canonical_key = generate_canonical_event_key(
            event_type="MONETARY_POLICY.RATE_DECISION",
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=jurisdiction,
            occurred_or_scheduled_date=dec_time.strftime("%Y-%m-%d"),
        )

        # Summary text formatting
        if target_lower is not None and target_upper is not None:
            rate_desc = f"target range {target_lower:.2f}% - {target_upper:.2f}%"
        elif new_rate is not None:
            rate_desc = f"policy rate to {new_rate:.2f}%"
            if payload_obj.change_bps is not None:
                sign = "+" if payload_obj.change_bps > 0 else ""
                rate_desc += f" ({sign}{payload_obj.change_bps:.0f} bps)"
        else:
            rate_desc = "monetary policy decision"

        event = AtlasUniversalEvent(
            event_id=f"evt-cb-{cb.lower()}-{dec_time.strftime('%Y%m%d')}",
            canonical_event_key=canonical_key,
            event_type="MONETARY_POLICY.RATE_DECISION",
            event_subtype="MONETARY_POLICY.RATE_DECISION",
            event_category=EventCategory.MONETARY_POLICY,
            title=f"{cb} Policy Rate Decision: {rate_desc}",
            factual_summary=f"Official monetary policy decision by {cb} setting {instrument} {rate_desc}.",
            lifecycle_status=EventLifecycleStatus.CONFIRMED,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            occurred_at=dec_time,
            source_published_at=dec_time,
            announced_at=dec_time,
            effective_at=eff_time or dec_time,
            date_precision=DatePrecision.EXACT_TIMESTAMP,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code=jurisdiction,
                jurisdiction=jurisdiction,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=[cb, "RATES", "CENTRAL_BANK"],
        )

        claims = []
        if new_rate is not None:
            claims.append(
                {
                    "predicate": "policy_rate:new_rate",
                    "claim_value": new_rate,
                    "value_type": "FLOAT",
                    "units": "PERCENT",
                }
            )
        if payload_obj.change_bps is not None:
            claims.append(
                {
                    "predicate": "policy_rate:change_bps",
                    "claim_value": payload_obj.change_bps,
                    "value_type": "FLOAT",
                    "units": "BPS",
                }
            )
        if target_lower is not None and target_upper is not None:
            claims.append(
                {
                    "predicate": "policy_rate:target_range",
                    "claim_value": {"lower": target_lower, "upper": target_upper},
                    "value_type": "DICT",
                    "units": "PERCENT",
                }
            )

        return event, claims
