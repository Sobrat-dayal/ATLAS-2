"""USGS Earthquake GeoJSON Adapter (Stage 134).

Parses USGS real-time earthquake feeds and integrates with the EventRevisionManager
for revision tracking, ensuring revised earthquake records do not inflate counts.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from ..domain import (
    AtlasGeoObservation,
    EarthquakeEvent,
    FreshnessState,
    LiveObservationCategory,
    ObservationDataClass,
)
from ..temporal.revisions import EventRevisionManager


class USGSEarthquakeAdapter:
    """Adapter for parsing USGS GeoJSON earthquake feeds."""

    def __init__(self, revision_manager: Optional[EventRevisionManager] = None) -> None:
        self.provider_id = "usgs_earthquake_feed"
        self.product_id = "earthquake_geojson"
        self.revision_manager = revision_manager or EventRevisionManager()

    def parse_feature(self, feature: Dict[str, Any]) -> Tuple[EarthquakeEvent, AtlasGeoObservation, bool]:
        """Parse a single USGS GeoJSON feature into an EarthquakeEvent and AtlasGeoObservation.

        Returns:
            Tuple of (canonical_event, observation, is_new_event).
        """
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [0.0, 0.0, 0.0])

        lon = float(coords[0])
        lat = float(coords[1])
        depth_km = float(coords[2]) if len(coords) > 2 else 0.0

        event_id = str(feature.get("id", props.get("code", "us00000000")))
        title = props.get("title", f"M {props.get('mag', 0.0)} - {props.get('place', 'Unknown')}")
        place = props.get("place", "Unknown Location")
        mag = float(props.get("mag", 0.0) or 0.0)
        mag_type = props.get("magType", "mww")
        status = props.get("status", "reviewed")

        time_ms = props.get("time", 0)
        updated_ms = props.get("updated", time_ms)
        time_utc = datetime.fromtimestamp(time_ms / 1000.0, tz=timezone.utc)
        updated_utc = datetime.fromtimestamp(updated_ms / 1000.0, tz=timezone.utc)

        raw_event = EarthquakeEvent(
            event_id=event_id,
            title=title,
            place=place,
            magnitude=mag,
            magnitude_type=mag_type,
            depth_km=depth_km,
            time_utc=time_utc,
            updated_utc=updated_utc,
            status=status,
            tsunami=int(props.get("tsunami", 0) or 0),
            felt=props.get("felt"),
            alert_color=props.get("alert"),
            significance=int(props.get("sig", 0) or 0),
            longitude=lon,
            latitude=lat,
        )

        canonical_event, is_new = self.revision_manager.upsert_earthquake(
            provider_id=self.provider_id,
            product_id=self.product_id,
            event=raw_event,
        )

        observation = AtlasGeoObservation(
            observation_id=f"usgs-eq-{canonical_event.event_id}-r{canonical_event.source_revision}",
            category=LiveObservationCategory.EARTHQUAKE,
            data_class=ObservationDataClass.OBSERVED,
            entity_id=canonical_event.event_id,
            entity_name=canonical_event.title,
            provider_id=self.provider_id,
            product_id=self.product_id,
            source_revision=canonical_event.source_revision,
            longitude=canonical_event.longitude,
            latitude=canonical_event.latitude,
            altitude_m=-canonical_event.depth_km * 1000.0,
            geometry={"type": "Point", "coordinates": [canonical_event.longitude, canonical_event.latitude]},
            observed_at=canonical_event.time_utc,
            source_published_at=canonical_event.updated_utc,
            received_at=datetime.now(timezone.utc),
            ingested_at=datetime.now(timezone.utc),
            freshness_state=FreshnessState.CURRENT,
            properties={
                "magnitude": canonical_event.magnitude,
                "magnitude_type": canonical_event.magnitude_type,
                "depth_km": canonical_event.depth_km,
                "place": canonical_event.place,
                "status": canonical_event.status,
                "tsunami": canonical_event.tsunami,
                "alert": canonical_event.alert_color,
                "significance": canonical_event.significance,
                "revision_history": canonical_event.revision_history,
            },
            source_attribution="USGS Earthquake Hazards Program",
            provenance_note="USGS Real-Time Earthquake GeoJSON Feed",
        )

        return canonical_event, observation, is_new

    def parse_feed(self, feed_geojson: Dict[str, Any]) -> List[AtlasGeoObservation]:
        """Parse full USGS GeoJSON FeatureCollection."""
        features = feed_geojson.get("features", [])
        observations: List[AtlasGeoObservation] = []
        for feat in features:
            try:
                _, obs, _ = self.parse_feature(feat)
                observations.append(obs)
            except Exception:
                continue
        return observations

