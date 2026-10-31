"""Physical World and Natural Disasters Ingestion Adapter (Stage 135).

Bridges Stage 134 physical-world real-time observations (USGS earthquakes,
FIRMS thermal hotspots, NWS severe weather alerts) into the Universal Event Model.

CRITICAL INVARIANTS:
1. Fixture I: Earthquake updates with the same USGS ID (e.g. revised magnitude M5.2 -> M5.4)
   update the canonical event in-place without generating a duplicate earthquake.
2. Fixture J: Separate earthquakes with different USGS IDs remain distinct events
   and must never be merged by fuzzy proximity or timestamp heuristics.
3. Fixture R: Stage 134 observation IDs bridge transparently without fabricating damage speculation.
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
from ..taxonomy.payloads import PhysicalDisasterEventPayload
from .base import BaseEventAdapter


class PhysicalWorldAdapter(BaseEventAdapter):
    """Adapter for natural disasters and Stage 134 live physical-world observations."""

    def __init__(self, source_id: str = "usgs_earthquakes"):
        super().__init__(source_id)

    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        now_utc = datetime.now(timezone.utc)

        disaster_type = str(raw_payload.get("disaster_type", "EARTHQUAKE")).upper()
        source_event_id = str(raw_payload.get("source_event_id", raw_payload.get("id", "UNKNOWN_SOURCE_ID")))
        mag_or_sev = str(raw_payload.get("magnitude_or_severity", raw_payload.get("magnitude", "0.0")))
        depth_km = raw_payload.get("depth_km")
        if depth_km is not None:
            depth_km = float(depth_km)
        frp_mw = raw_payload.get("frp_mw")
        if frp_mw is not None:
            frp_mw = float(frp_mw)
        tsunami_flag = bool(raw_payload.get("tsunami_flag", False))
        stage134_id = raw_payload.get("stage134_observation_id")

        # Coordinates
        latitude = raw_payload.get("latitude")
        longitude = raw_payload.get("longitude")
        place_name = raw_payload.get("place", raw_payload.get("location_description", "Unknown Location"))
        country_code = raw_payload.get("country_code", "GLOBAL")

        # Time
        time_val = raw_payload.get("time", raw_payload.get("occurred_at", now_utc))
        if isinstance(time_val, str):
            try:
                occ_dt = datetime.fromisoformat(time_val.replace("Z", "+00:00"))
            except Exception:
                occ_dt = now_utc
        elif isinstance(time_val, (int, float)):
            # Epoch milliseconds
            occ_dt = datetime.fromtimestamp(time_val / 1000.0, tz=timezone.utc)
        elif isinstance(time_val, datetime):
            occ_dt = time_val
        else:
            occ_dt = now_utc

        payload_obj = PhysicalDisasterEventPayload(
            disaster_type=disaster_type,
            magnitude_or_severity=mag_or_sev,
            depth_km=depth_km,
            frp_mw=frp_mw,
            source_event_id=source_event_id,
            tsunami_flag=tsunami_flag,
            stage134_observation_id=stage134_id,
        )

        canonical_key = generate_canonical_event_key(
            event_type=f"NATURAL_DISASTER.{disaster_type}",
            payload=payload_obj.model_dump(),
            source_event_id=source_event_id,
            country_or_jurisdiction=country_code,
            occurred_or_scheduled_date=occ_dt.strftime("%Y-%m-%d"),
        )

        if disaster_type == "EARTHQUAKE":
            title = f"M{mag_or_sev} Earthquake - {place_name}"
            summary = (
                f"USGS Earthquake {source_event_id} of magnitude {mag_or_sev} occurred near {place_name} "
                f"at depth {depth_km or 0.0:.1f} km."
            )
            event_subtype = "NATURAL_DISASTER.EARTHQUAKE"
        elif disaster_type == "WILDFIRE":
            title = f"Thermal Hotspot / Wildfire - {place_name}"
            summary = (
                f"Satellite-detected thermal hotspot {source_event_id} at {place_name} "
                f"with fire radiative power {frp_mw or 0.0:.1f} MW."
            )
            event_subtype = "NATURAL_DISASTER.WILDFIRE"
        else:
            title = f"{disaster_type.title()} Event - {place_name}"
            summary = f"Severe physical event {source_event_id} ({disaster_type}) observed near {place_name}."
            event_subtype = f"NATURAL_DISASTER.{disaster_type}"

        event = AtlasUniversalEvent(
            event_id=f"evt-phys-{normalize_token(source_event_id).lower()}",
            canonical_event_key=canonical_key,
            event_type="NATURAL_DISASTER.OBSERVED",
            event_subtype=event_subtype,
            event_category=EventCategory.NATURAL_DISASTER,
            title=title,
            factual_summary=summary,
            lifecycle_status=EventLifecycleStatus.OCCURRED,
            verification_status=EventVerificationStatus.OFFICIALLY_CONFIRMED,
            occurred_at=occ_dt,
            date_precision=DatePrecision.EXACT_TIMESTAMP,
            announced_at=occ_dt,
            source_published_at=occ_dt,
            first_public_at=occ_dt,
            first_ingested_at=now_utc,
            updated_at=now_utc,
            geographic_scope=EventGeographicScope(
                scope_type=GeographicScopeType.COORDINATES if latitude is not None and longitude is not None else GeographicScopeType.GLOBAL,
                country_code=country_code,
                latitude=float(latitude) if latitude is not None else None,
                longitude=float(longitude) if longitude is not None else None,
                location_name=place_name,
            ),
            primary_source_id=self.source_id,
            event_payload=payload_obj.model_dump(),
            source_count=1,
            tags=["natural_disaster", disaster_type.lower(), "physical_world"],
            aliases=[source_event_id],
        )

        claims: List[Dict[str, Any]] = [
            {
                "predicate": "SOURCE_EVENT_ID",
                "claim_value": source_event_id,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"source": self.source_id},
            },
            {
                "predicate": "MAGNITUDE_OR_SEVERITY",
                "claim_value": mag_or_sev,
                "value_type": "STRING",
                "units": "M" if disaster_type == "EARTHQUAKE" else "SEV",
                "qualifiers": {},
            },
        ]
        if depth_km is not None:
            claims.append({
                "predicate": "HYPOCENTER_DEPTH",
                "claim_value": depth_km,
                "value_type": "FLOAT",
                "units": "KM",
                "qualifiers": {},
            })
        if stage134_id:
            claims.append({
                "predicate": "STAGE134_BRIDGE_ID",
                "claim_value": stage134_id,
                "value_type": "STRING",
                "units": None,
                "qualifiers": {"bridge_type": "PHYSICAL_WORLD_OBSERVATION"},
            })

        return event, claims
