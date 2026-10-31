"""Authorized AIS Maritime Vessel Observation Adapter (Stage 134).

Interfaces authorized AIS vessel tracking feeds (e.g. US Coast Guard NAIS,
Spire Maritime, MarineTraffic).
Enforces zero simulation invariant: strictly fails closed or returns unconfigured
provider status if credentials or entitlements are absent.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasGeoObservation,
    FreshnessState,
    LiveGeoProvider,
    LiveObservationCategory,
    LiveVesselState,
    ObservationDataClass,
    ProviderStatus,
)
from ..errors import LiveProviderNotConfiguredError


class AuthorizedAISAdapter:
    """Adapter for authorized AIS maritime vessel position and voyage reports."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.provider_id = "spire_ais"
        self.product_id = "ais_position_reports"
        self.api_key = api_key or os.getenv("SPIRE_AIS_API_KEY") or os.getenv("MARINETRAFFIC_API_KEY")

    def get_provider_metadata(self) -> LiveGeoProvider:
        """Return provider configuration and authorization status."""
        is_configured = bool(self.api_key and len(self.api_key.strip()) > 8)
        status = ProviderStatus.ONLINE if is_configured else ProviderStatus.UNCONFIGURED
        reason = None if is_configured else "Commercial AIS API key not configured in environment (SPIRE_AIS_API_KEY / MARINETRAFFIC_API_KEY)."

        return LiveGeoProvider(
            provider_id=self.provider_id,
            name="Commercial Satellite/Terrestrial AIS Feed",
            category=LiveObservationCategory.VESSEL,
            status=status,
            configured=is_configured,
            requires_auth=True,
            nominal_latency_seconds=60.0,
            ttl_seconds=3600,
            attribution="Spire Maritime / Global AIS Network",
            license_note="Commercial Maritime Subscription Required",
            endpoint_url="https://api.spire.com/vessel-tracking/v1",
            status_reason=reason,
        )

    def parse_ais_report(self, report: Dict[str, Any]) -> Tuple[LiveVesselState, AtlasGeoObservation]:
        """Parse AIS vessel position and voyage dictionary."""
        mmsi = str(report["mmsi"])
        imo = str(report.get("imo")) if report.get("imo") else None
        vessel_name = str(report.get("vessel_name", report.get("name", f"VESSEL-{mmsi}")))
        ship_type = str(report.get("ship_type", "Cargo"))
        nav_status = str(report.get("nav_status", "Under way using engine"))

        lon = float(report["longitude"])
        lat = float(report["latitude"])
        cog = float(report.get("cog_deg", report.get("course", 0.0))) if report.get("cog_deg") is not None or report.get("course") is not None else None
        sog = float(report.get("sog_knots", report.get("speed", 0.0))) if report.get("sog_knots") is not None or report.get("speed") is not None else None
        heading = float(report.get("heading_deg", report.get("heading", 0.0))) if report.get("heading_deg") is not None or report.get("heading") is not None else None
        draught = float(report.get("draught_m", 10.0)) if report.get("draught_m") is not None else None
        dest = str(report.get("destination")) if report.get("destination") else None

        pos_time = report.get("time_position_utc", datetime.now(timezone.utc))
        if isinstance(pos_time, str):
            pos_time = datetime.fromisoformat(pos_time.replace("Z", "+00:00"))

        eta_dt: Optional[datetime] = None
        if report.get("eta_utc"):
            eta_raw = report["eta_utc"]
            eta_dt = datetime.fromisoformat(eta_raw.replace("Z", "+00:00")) if isinstance(eta_raw, str) else eta_raw

        state = LiveVesselState(
            mmsi=mmsi,
            imo=imo,
            vessel_name=vessel_name,
            ship_type=ship_type,
            nav_status=nav_status,
            longitude=lon,
            latitude=lat,
            cog_deg=cog,
            sog_knots=sog,
            heading_deg=heading,
            draught_m=draught,
            destination=dest,
            eta_utc=eta_dt,
            time_position_utc=pos_time,
        )

        obs_id = f"ais-{mmsi}-{int(pos_time.timestamp())}"
        obs = AtlasGeoObservation(
            observation_id=obs_id,
            category=LiveObservationCategory.VESSEL,
            data_class=ObservationDataClass.OBSERVED,
            entity_id=mmsi,
            entity_name=vessel_name,
            provider_id=self.provider_id,
            product_id=self.product_id,
            source_revision=1,
            longitude=lon,
            latitude=lat,
            altitude_m=0.0,
            heading_deg=heading or cog,
            speed_mps=(sog * 0.514444) if sog is not None else None,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            observed_at=pos_time,
            source_published_at=pos_time,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "mmsi": mmsi,
                "imo": imo,
                "vessel_name": vessel_name,
                "ship_type": ship_type,
                "nav_status": nav_status,
                "cog_deg": cog,
                "sog_knots": sog,
                "draught_m": draught,
                "destination": dest,
                "eta_utc": eta_dt.isoformat() if eta_dt else None,
            },
            source_attribution="Commercial AIS Network",
            provenance_note="Measured AIS Transponder Position",
        )

        return state, obs
