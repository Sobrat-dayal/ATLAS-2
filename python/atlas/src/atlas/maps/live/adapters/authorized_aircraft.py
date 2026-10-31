"""Authorized Aircraft ADS-B Observation Adapter (Stage 134).

Interfaces authorized ADS-B tracking feeds (e.g. OpenSky Network, FAA System Wide
Information Management, ADS-B Exchange).
Enforces zero simulation invariant: strictly fails closed or returns unconfigured
provider status if credentials or entitlements are absent.
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasGeoObservation,
    FreshnessState,
    LiveAircraftState,
    LiveGeoProvider,
    LiveObservationCategory,
    ObservationDataClass,
    ProviderStatus,
)
from ..errors import LiveProviderNotConfiguredError


class AuthorizedAircraftAdapter:
    """Adapter for authorized live aircraft state vectors (ADS-B)."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None) -> None:
        self.provider_id = "opensky_network"
        self.product_id = "adsb_state_vectors"
        self.client_id = client_id or os.getenv("OPENSKY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OPENSKY_CLIENT_SECRET")

    def get_provider_metadata(self) -> LiveGeoProvider:
        """Return provider configuration and authorization status."""
        is_configured = bool(self.client_id and self.client_secret)
        status = ProviderStatus.ONLINE if is_configured else ProviderStatus.UNCONFIGURED
        reason = None if is_configured else "OpenSky Network API credentials not configured in environment (OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET)."

        return LiveGeoProvider(
            provider_id=self.provider_id,
            name="OpenSky Network ADS-B Feed",
            category=LiveObservationCategory.AIRCRAFT,
            status=status,
            configured=is_configured,
            requires_auth=True,
            nominal_latency_seconds=10.0,
            ttl_seconds=300,
            attribution="The OpenSky Network (https://opensky-network.org)",
            license_note="Academic/Institutional API access under OpenSky Terms of Use",
            endpoint_url="https://opensky-network.org/api/states/all",
            status_reason=reason,
        )

    def parse_state_vector(self, vector: List[Any], time_utc: Optional[datetime] = None) -> Tuple[LiveAircraftState, AtlasGeoObservation]:
        """Parse OpenSky format state vector into LiveAircraftState and AtlasGeoObservation.

        OpenSky vector schema:
        [0] icao24, [1] callsign, [2] origin_country, [3] time_position, [4] last_contact,
        [5] longitude, [6] latitude, [7] baro_altitude, [8] on_ground, [9] velocity,
        [10] true_track, [11] vertical_rate, [12] sensors, [13] geo_altitude, [14] squawk,
        [15] spi, [16] position_source
        """
        if time_utc is None:
            time_utc = datetime.now(timezone.utc)

        icao24 = str(vector[0]).strip().lower()
        callsign = str(vector[1]).strip() if vector[1] else None
        country = str(vector[2]).strip() if vector[2] else "Unknown"

        pos_time_sec = vector[3] if len(vector) > 3 and vector[3] else None
        last_contact_sec = vector[4] if len(vector) > 4 and vector[4] else None

        pos_dt = (
            datetime.fromtimestamp(pos_time_sec, tz=timezone.utc)
            if pos_time_sec
            else time_utc
        )
        contact_dt = (
            datetime.fromtimestamp(last_contact_sec, tz=timezone.utc)
            if last_contact_sec
            else time_utc
        )

        lon = float(vector[5]) if len(vector) > 5 and vector[5] is not None else 0.0
        lat = float(vector[6]) if len(vector) > 6 and vector[6] is not None else 0.0
        baro_alt = float(vector[7]) if len(vector) > 7 and vector[7] is not None else None
        on_ground = bool(vector[8]) if len(vector) > 8 else False
        vel = float(vector[9]) if len(vector) > 9 and vector[9] is not None else None
        track = float(vector[10]) if len(vector) > 10 and vector[10] is not None else None
        v_rate = float(vector[11]) if len(vector) > 11 and vector[11] is not None else None
        geo_alt = float(vector[13]) if len(vector) > 13 and vector[13] is not None else None
        squawk = str(vector[14]) if len(vector) > 14 and vector[14] else None
        spi = bool(vector[15]) if len(vector) > 15 else False

        state = LiveAircraftState(
            icao24=icao24,
            callsign=callsign,
            origin_country=country,
            time_position_utc=pos_dt,
            last_contact_utc=contact_dt,
            longitude=lon,
            latitude=lat,
            baro_altitude_m=baro_alt,
            geo_altitude_m=geo_alt,
            on_ground=on_ground,
            velocity_mps=vel,
            true_track_deg=track,
            vertical_rate_mps=v_rate,
            squawk=squawk,
            spi=spi,
        )

        obs_id = f"adsb-{icao24}-{int(pos_dt.timestamp())}"
        obs = AtlasGeoObservation(
            observation_id=obs_id,
            category=LiveObservationCategory.AIRCRAFT,
            data_class=ObservationDataClass.OBSERVED,
            entity_id=icao24,
            entity_name=callsign or icao24.upper(),
            provider_id=self.provider_id,
            product_id=self.product_id,
            source_revision=1,
            longitude=lon,
            latitude=lat,
            altitude_m=baro_alt or geo_alt,
            heading_deg=track,
            speed_mps=vel,
            vertical_rate_mps=v_rate,
            geometry={"type": "Point", "coordinates": [lon, lat]},
            observed_at=pos_dt,
            source_published_at=contact_dt,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "icao24": icao24,
                "callsign": callsign,
                "origin_country": country,
                "on_ground": on_ground,
                "squawk": squawk,
                "baro_altitude_m": baro_alt,
                "velocity_mps": vel,
                "true_track_deg": track,
                "vertical_rate_mps": v_rate,
            },
            source_attribution="OpenSky Network ADS-B",
            provenance_note="Measured ADS-B State Vector",
        )

        return state, obs

