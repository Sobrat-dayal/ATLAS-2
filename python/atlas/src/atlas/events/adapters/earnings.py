"""Corporate Earnings Ingestion Adapter (Stage 135).

Parses corporate earnings schedule disclosures and actual earnings report publications.
Enforces strict distinction between scheduled announcements and actual released metrics.
"""

import uuid
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
from ..taxonomy.payloads import EarningsEventPayload
from .base import BaseEventAdapter


class EarningsAdapter(BaseEventAdapter):
    """Adapter for corporate earnings filings and schedule events."""

    def __init__(self, source_id: str = "sec_edgar"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)
        issuer = str(raw_payload.get("issuer_reference", raw_payload.get("ticker", "UNKNOWN"))).upper()
        fiscal_year = int(raw_payload.get("fiscal_year", now_utc.year))
        fiscal_quarter = int(raw_payload.get("fiscal_quarter", 1))
        period_str = f"Q{fiscal_quarter}"

        is_scheduled_only = bool(raw_payload.get("is_scheduled", False))
        metrics = raw_payload.get("reported_metrics", {})

        payload_obj = EarningsEventPayload(
            issuer_reference=issuer,
            fiscal_period=f"{fiscal_year}-{period_str}",
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            period_end=str(raw_payload.get("period_end", f"{fiscal_year}-12-31")),
            release_datetime=raw_payload.get("release_datetime"),
            reporting_currency=raw_payload.get("reporting_currency", "USD"),
            reported_metrics=metrics,
            consensus_metrics=raw_payload.get("consensus_metrics"),
            surprise_metrics=raw_payload.get("surprise_metrics"),
            audit_status=raw_payload.get("audit_status", "UNAUDITED"),
        )

        canonical_key = generate_canonical_event_key(
            event_type="FINANCIAL.EARNINGS_RELEASE",
            payload=payload_obj.model_dump(),
        )

        lifecycle = (
            EventLifecycleStatus.SCHEDULED
            if is_scheduled_only
            else EventLifecycleStatus.CONFIRMED
        )
        verification = (
            EventVerificationStatus.OFFICIALLY_CONFIRMED
            if source_record and "sec" in source_record.source_id.lower()
            else EventVerificationStatus.SOURCE_REPORTED
        )

        rel_time = raw_payload.get("release_datetime")
        if isinstance(rel_time, str):
            rel_time = datetime.fromisoformat(rel_time.replace("Z", "+00:00"))

        event = AtlasUniversalEvent(
            event_id=f"evt-earn-{issuer.lower()}-{fiscal_year}q{fiscal_quarter}",
            canonical_event_key=canonical_key,
            event_type="FINANCIAL.EARNINGS_RELEASE",
            event_subtype="FINANCIAL.EARNINGS_RELEASE",
            event_category=EventCategory.FINANCIAL,
            title=f"{issuer} Q{fiscal_quarter} {fiscal_year} Earnings {'Scheduled' if is_scheduled_only else 'Report'}",
            factual_summary=f"Corporate earnings release for {issuer} covering fiscal period {fiscal_year} Q{fiscal_quarter}.",
            lifecycle_status=lifecycle,
            verification_status=verification,
            occurred_at=rel_time if not is_scheduled_only else None,
            scheduled_for=rel_time if is_scheduled_only else None,
            announced_at=rel_time or now_utc,
            date_precision=DatePrecision.EXACT_TIMESTAMP if rel_time else DatePrecision.DATE_ONLY,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code="US",
                jurisdiction="US-SEC",
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=[issuer, "EARNINGS", f"Q{fiscal_quarter}"],
        )

        # Extract claims
        claims = []
        for metric_name, val in metrics.items():
            claims.append(
                {
                    "predicate": f"metric:{metric_name}",
                    "claim_value": val,
                    "value_type": "FLOAT",
                    "units": payload_obj.reporting_currency,
                }
            )

        return event, claims
