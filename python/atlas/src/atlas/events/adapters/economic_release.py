"""Economic Release Ingestion Adapter (Stage 135).

Parses macroeconomic indicators, labor reports, GDP, and inflation releases.
Preserves official statistical data vintages (initial vs revised values) for bitemporal history.
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
from ..taxonomy.payloads import EconomicReleasePayload
from .base import BaseEventAdapter


class EconomicReleaseAdapter(BaseEventAdapter):
    """Adapter for official macroeconomic data releases and statistical revisions."""

    def __init__(self, source_id: str = "fred_stlouis"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)
        indicator_id = str(raw_payload.get("indicator_id", "CPI")).upper()
        country = str(raw_payload.get("country_region", "US")).upper()
        reporting_period = str(raw_payload.get("reporting_period", "2026-Q3"))
        vintage = str(raw_payload.get("revision_vintage", "INITIAL")).upper()
        reported_val = float(raw_payload.get("reported_value", 0.0))
        units = str(raw_payload.get("units", "PERCENT"))

        rel_time = raw_payload.get("release_time", now_utc)
        if isinstance(rel_time, str):
            rel_time = datetime.fromisoformat(rel_time.replace("Z", "+00:00"))

        payload_obj = EconomicReleasePayload(
            indicator_id=indicator_id,
            indicator_name=str(raw_payload.get("indicator_name", indicator_id)),
            country_region=country,
            reporting_period=reporting_period,
            reference_period=str(raw_payload.get("reference_period", reporting_period)),
            release_time=rel_time,
            reported_value=reported_val,
            units=units,
            seasonal_adjustment=str(raw_payload.get("seasonal_adjustment", "SA")),
            revision_vintage=vintage,
            previous_value=raw_payload.get("previous_value"),
            consensus_expectation=raw_payload.get("consensus_expectation"),
        )

        canonical_key = generate_canonical_event_key(
            event_type=f"ECONOMIC.{indicator_id}_RELEASE",
            payload=payload_obj.model_dump(),
            country_or_jurisdiction=country,
            occurred_or_scheduled_date=reporting_period,
        )

        event = AtlasUniversalEvent(
            event_id=f"evt-econ-{country.lower()}-{indicator_id.lower()}-{reporting_period.lower()}-{vintage.lower()}",
            canonical_event_key=canonical_key,
            event_type=f"ECONOMIC.{indicator_id}_RELEASE",
            event_subtype=f"ECONOMIC.{indicator_id}_RELEASE",
            event_category=EventCategory.ECONOMIC,
            title=f"{country} {payload_obj.indicator_name} ({reporting_period}) [{vintage}]",
            factual_summary=f"Official statistical release of {payload_obj.indicator_name} for {country} reporting period {reporting_period}: {reported_val} {units}.",
            lifecycle_status=EventLifecycleStatus.CONFIRMED,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            occurred_at=rel_time,
            source_published_at=rel_time,
            announced_at=rel_time,
            date_precision=DatePrecision.EXACT_TIMESTAMP,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COUNTRY,
                country_code=country,
                jurisdiction=country,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=[country, indicator_id, "MACRO", vintage],
        )

        claims = [
            {
                "predicate": f"indicator:{indicator_id}:reported_value",
                "claim_value": reported_val,
                "value_type": "FLOAT",
                "units": units,
                "qualifiers": {"vintage": vintage, "reporting_period": reporting_period},
            }
        ]

        return event, claims

