"""ATLAS Maps Live Physical-World Intelligence Service (Stage 134).

Orchestrates multi-provider ingestion, hot state caching, watermarks,
event revision deduplication, SGP4 orbital mechanics, H3 spatial aggregation,
and infrastructure proximity correlation.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .adapters.authorized_aircraft import AuthorizedAircraftAdapter
from .adapters.authorized_ais import AuthorizedAISAdapter
from .adapters.celestrak import CelesTrakAdapter
from .adapters.nasa_firms import NASAFIRMSAdapter
from .adapters.nws_weather import NWSWeatherAdapter
from .adapters.usgs_earthquakes import USGSEarthquakeAdapter
from .analytics.h3_live import aggregate_live_observations_to_h3
from .analytics.infrastructure_proximity import correlate_infrastructure_proximity
from .domain import (
    AtlasGeoObservation,
    EarthquakeEvent,
    FireDetection,
    FreshnessPolicy,
    FreshnessState,
    InfrastructureProximityMatch,
    LiveGeoProvider,
    LiveObservationCategory,
    ProviderStatus,
    SatelliteOrbitalElements,
    SatelliteState,
    TrajectorySegment,
    WeatherAlert,
)
from .errors import (
    LiveCoordinatesInvalidError,
    LiveEventNotFoundError,
    LiveProviderNotConfiguredError,
    LiveViewportTooLargeError,
)
from .orbital.propagation import propagate_satellite
from .seed import (
    AIRCRAFT_GAP_POINTS,
    EARTHQUAKE_INITIAL_GEOJSON,
    EARTHQUAKE_REVISED_GEOJSON,
    FIRMS_DETECTIONS_RAW,
    ISS_ELEMENTS,
    NOW_UTC,
    NWS_WEATHER_ALERT_GEOJSON,
    SEED_AIRCRAFT_OBSERVATIONS,
    SEED_INFRASTRUCTURE_FACILITIES,
    SEED_VESSEL_OBSERVATIONS,
    STALE_SATELLITE_ELEMENTS,
)
from .state.hot_store import LiveHotStateStore
from .temporal.freshness import evaluate_freshness
from .temporal.revisions import EventRevisionManager
from .trajectories.gap_splitter import split_trajectory_points


class AtlasLiveGeoService:
    """Institutional-grade live physical-world geospatial intelligence service."""

    def __init__(self) -> None:
        self.hot_store = LiveHotStateStore()
        self.revision_manager = EventRevisionManager()
        self.usgs_adapter = USGSEarthquakeAdapter(revision_manager=self.revision_manager)
        self.firms_adapter = NASAFIRMSAdapter()
        self.nws_adapter = NWSWeatherAdapter()
        self.celestrak_adapter = CelesTrakAdapter()
        self.aircraft_adapter = AuthorizedAircraftAdapter()
        self.ais_adapter = AuthorizedAISAdapter()

        # Seed initial institutional reference data
        self._load_seed_data()

    def _load_seed_data(self) -> None:
        """Initialize service with institutional benchmark fixtures."""
        # 1. Aircraft observations
        for obs in SEED_AIRCRAFT_OBSERVATIONS:
            self.hot_store.ingest_observation(obs)

        # 2. Vessel observations
        for obs in SEED_VESSEL_OBSERVATIONS:
            self.hot_store.ingest_observation(obs)

        # 3. Earthquake initial event (Revision 1)
        _, eq_obs, _ = self.usgs_adapter.parse_feature(EARTHQUAKE_INITIAL_GEOJSON)
        self.hot_store.ingest_observation(eq_obs)

        # 4. Weather alert
        _, weather_obs = self.nws_adapter.parse_cap_feature(NWS_WEATHER_ALERT_GEOJSON)
        self.hot_store.ingest_observation(weather_obs)

        # 5. Satellite propagation (ISS ZARYA)
        _, sat_obs = self.celestrak_adapter.propagate_to_observation(ISS_ELEMENTS, target_time=NOW_UTC)
        self.hot_store.ingest_observation(sat_obs)

        # 6. FIRMS thermal detections (parsed from raw data)
        for row in FIRMS_DETECTIONS_RAW:
            _, fire_obs = self.firms_adapter.parse_detection_row(row)
            self.hot_store.ingest_observation(fire_obs)

    def list_providers(self) -> List[LiveGeoProvider]:
        """Return status and configuration of all supported live providers."""
        return [
            self.aircraft_adapter.get_provider_metadata(),
            self.ais_adapter.get_provider_metadata(),
            self.firms_adapter.get_provider_metadata(),
            LiveGeoProvider(
                provider_id="celestrak",
                name="CelesTrak Satellite Ephemeris Catalog",
                category=LiveObservationCategory.SATELLITE,
                status=ProviderStatus.ONLINE,
                configured=True,
                requires_auth=False,
                nominal_latency_seconds=1.0,
                ttl_seconds=86400,
                attribution="CelesTrak / Space-Track / US Space Force",
                license_note="Publicly available orbital elements",
                endpoint_url="https://celestrak.org/NORAD/elements/gp.php",
            ),
            LiveGeoProvider(
                provider_id="usgs_earthquake_feed",
                name="USGS Earthquake Hazards Program",
                category=LiveObservationCategory.EARTHQUAKE,
                status=ProviderStatus.ONLINE,
                configured=True,
                requires_auth=False,
                nominal_latency_seconds=180.0,
                ttl_seconds=300,
                attribution="U.S. Geological Survey",
                license_note="US Public Domain / CC0",
                endpoint_url="https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php",
            ),
            LiveGeoProvider(
                provider_id="noaa_nws",
                name="NOAA National Weather Service",
                category=LiveObservationCategory.WEATHER_ALERT,
                status=ProviderStatus.ONLINE,
                configured=True,
                requires_auth=False,
                nominal_latency_seconds=60.0,
                ttl_seconds=300,
                attribution="National Oceanic and Atmospheric Administration",
                license_note="US Public Domain / Open Data",
                endpoint_url="https://api.weather.gov/alerts/active",
            ),
        ]

    def get_provider(self, provider_id: str) -> Optional[LiveGeoProvider]:
        """Retrieve single provider by identifier."""
        for p in self.list_providers():
            if p.provider_id == provider_id:
                return p
        return None

    def get_snapshot(
        self,
        categories: Optional[List[LiveObservationCategory]] = None,
        bbox: Optional[List[float]] = None,
        max_results: int = 1000,
        now_utc: Optional[datetime] = None,
    ) -> Tuple[List[AtlasGeoObservation], int]:
        """Query active observation snapshot with spatial bounds and freshness evaluation."""
        if bbox:
            if len(bbox) != 4:
                raise LiveCoordinatesInvalidError(0.0, 0.0)
            min_lon, min_lat, max_lon, max_lat = bbox
            if not (-180.0 <= min_lon <= 180.0 and -180.0 <= max_lon <= 180.0 and -90.0 <= min_lat <= 90.0 and -90.0 <= max_lat <= 90.0):
                raise LiveCoordinatesInvalidError(min_lat, min_lon)
            if min_lon > max_lon or min_lat > max_lat:
                raise LiveCoordinatesInvalidError(min_lat, min_lon)

        return self.hot_store.get_snapshot(
            categories=categories,
            bbox=bbox,
            max_results=max_results,
            now_utc=now_utc or NOW_UTC,
        )

    def get_deltas(
        self,
        since_sequence: int,
        categories: Optional[List[LiveObservationCategory]] = None,
        bbox: Optional[List[float]] = None,
        max_results: int = 1000,
    ) -> Tuple[List[AtlasGeoObservation], int]:
        """Query delta observations since a sequence number."""
        return self.hot_store.get_deltas(
            since_sequence=since_sequence,
            categories=categories,
            bbox=bbox,
            max_results=max_results,
        )

    def get_playback_snapshot(
        self,
        target_time_utc: datetime,
        categories: Optional[List[LiveObservationCategory]] = None,
        window_seconds: float = 3600.0,
    ) -> List[AtlasGeoObservation]:
        """Historical playback snapshot reconstructed at target_time_utc."""
        return self.hot_store.get_playback_snapshot(
            target_time_utc=target_time_utc,
            window_seconds=window_seconds,
            categories=categories,
        )

    def apply_earthquake_revision(self, revised_geojson: Dict[str, Any]) -> Tuple[EarthquakeEvent, AtlasGeoObservation, bool]:
        """Apply an earthquake revision (e.g. Fixture A).

        Updates existing earthquake in-place and updates hot cache without inflating count.
        """
        eq_event, obs, is_new = self.usgs_adapter.parse_feature(revised_geojson)
        self.hot_store.ingest_observation(obs)
        return eq_event, obs, is_new

    def propagate_satellite_elements(
        self,
        elements: SatelliteOrbitalElements,
        propagate_at: Optional[datetime] = None,
        fail_on_critical_stale: bool = False,
    ) -> SatelliteState:
        """Propagate satellite orbital elements to instantaneous geodetic state."""
        return propagate_satellite(
            elements=elements,
            propagate_at=propagate_at or NOW_UTC,
            fail_on_critical_stale=fail_on_critical_stale,
        )

    def correlate_infrastructure_proximity(
        self,
        event_dict: Dict[str, Any],
        facilities: Optional[List[Dict[str, Any]]] = None,
        max_radius_km: float = 150.0,
    ) -> List[InfrastructureProximityMatch]:
        """Correlate physical facilities with an observation (Fixture M)."""
        fac_list = facilities if facilities is not None else SEED_INFRASTRUCTURE_FACILITIES
        return correlate_infrastructure_proximity(
            facilities=fac_list,
            event=event_dict,
            max_radius_km=max_radius_km,
        )

    def aggregate_to_h3(
        self,
        resolution: int = 4,
        categories: Optional[List[LiveObservationCategory]] = None,
    ) -> List[Dict[str, Any]]:
        """Aggregate active observations into H3 hexagonal cells (Fixture L)."""
        observations, _ = self.hot_store.get_snapshot(categories=categories, max_results=5000)
        return aggregate_live_observations_to_h3(observations, resolution=resolution)

    def get_trajectory_segments(
        self,
        entity_id: str,
        category: LiveObservationCategory = LiveObservationCategory.AIRCRAFT,
        points: Optional[List[Dict[str, Any]]] = None,
        max_gap_seconds: Optional[float] = None,
    ) -> List[TrajectorySegment]:
        """Split entity trajectory points into segments respecting signal gaps (Fixture D)."""
        pts = points if points is not None else AIRCRAFT_GAP_POINTS
        return split_trajectory_points(
            points=pts,
            category=category,
            entity_id=entity_id,
            max_gap_seconds=max_gap_seconds,
        )


# Global singleton instance
atlas_live_geo_service = AtlasLiveGeoService()

