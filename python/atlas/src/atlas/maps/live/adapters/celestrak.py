"""CelesTrak Satellite Ephemeris Adapter (Stage 134).

Interfaces CelesTrak orbital element sets and runs SGP4-compatible analytical
propagation to generate instantaneous satellite observations.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasGeoObservation,
    FreshnessState,
    LiveObservationCategory,
    ObservationDataClass,
    SatelliteOrbitalElements,
    SatelliteState,
)
from ..orbital.propagation import propagate_satellite


class CelesTrakAdapter:
    """Adapter for CelesTrak orbital element sets and satellite propagation."""

    def __init__(self) -> None:
        self.provider_id = "celestrak"
        self.product_id = "gp_elements_v1"

    def propagate_to_observation(
        self,
        elements: SatelliteOrbitalElements,
        target_time: Optional[datetime] = None,
        fail_on_critical_stale: bool = False,
    ) -> Tuple[SatelliteState, AtlasGeoObservation]:
        """Propagate orbital elements and construct an AtlasGeoObservation."""
        if target_time is None:
            target_time = datetime.now(timezone.utc)

        sat_state = propagate_satellite(
            elements=elements,
            propagate_at=target_time,
            fail_on_critical_stale=fail_on_critical_stale,
        )

        obs_id = f"sat-{elements.norad_cat_id}-{target_time.strftime('%Y%m%d%H%M%S')}"

        obs = AtlasGeoObservation(
            observation_id=obs_id,
            category=LiveObservationCategory.SATELLITE,
            data_class=ObservationDataClass.PROPAGATED,
            entity_id=str(elements.norad_cat_id),
            entity_name=elements.name,
            provider_id=self.provider_id,
            product_id=self.product_id,
            source_revision=1,
            longitude=sat_state.subpoint_longitude,
            latitude=sat_state.subpoint_latitude,
            altitude_m=sat_state.altitude_km * 1000.0,
            geometry={"type": "Point", "coordinates": [sat_state.subpoint_longitude, sat_state.subpoint_latitude]},
            observed_at=target_time,
            source_published_at=elements.epoch_utc,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "norad_cat_id": elements.norad_cat_id,
                "intl_designator": elements.intl_designator,
                "epoch_utc": elements.epoch_utc.isoformat(),
                "epoch_age_days": sat_state.epoch_age_days,
                "is_stale_epoch": sat_state.is_stale_epoch,
                "altitude_km": sat_state.altitude_km,
                "velocity_km_s": sat_state.velocity_km_s,
                "footprint_radius_km": sat_state.footprint_radius_km,
                "inclination_deg": elements.inclination_deg,
                "period_minutes": elements.period_minutes,
                "apogee_km": elements.apogee_km,
                "perigee_km": elements.perigee_km,
            },
            source_attribution="CelesTrak / Space-Track.org / US Space Force 18th SDS",
            provenance_note=sat_state.provenance_note,
        )

        return sat_state, obs
