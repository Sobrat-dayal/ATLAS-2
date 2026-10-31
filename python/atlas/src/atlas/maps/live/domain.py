"""ATLAS Maps Live Physical-World Domain Models (Stage 134).

Defines institutional-grade domain models, categories, freshness states,
clocks, providers, and observation types for real-time and near-real-time
geospatial observation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LiveObservationCategory(str, Enum):
    """Canonical categories of live physical-world observations."""
    AIRCRAFT = "AIRCRAFT"
    VESSEL = "VESSEL"
    SATELLITE = "SATELLITE"
    WEATHER_OBSERVATION = "WEATHER_OBSERVATION"
    WEATHER_FORECAST = "WEATHER_FORECAST"
    WEATHER_ALERT = "WEATHER_ALERT"
    EARTHQUAKE = "EARTHQUAKE"
    ACTIVE_FIRE = "ACTIVE_FIRE"
    NATURAL_EVENT = "NATURAL_EVENT"


class FreshnessState(str, Enum):
    """Institutional freshness evaluation state."""
    CURRENT = "CURRENT"
    DELAYED = "DELAYED"
    STALE = "STALE"
    EXPIRED = "EXPIRED"
    HISTORICAL = "HISTORICAL"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"


class ObservationDataClass(str, Enum):
    """Scientific data class characterizing the nature of the observation."""
    OBSERVED = "OBSERVED"
    PROPAGATED = "PROPAGATED"
    FORECAST = "FORECAST"
    REFERENCE = "REFERENCE"


class ProviderStatus(str, Enum):
    """Health and operational status of an upstream data provider."""
    ONLINE = "ONLINE"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    UNCONFIGURED = "UNCONFIGURED"
    ACCESS_RESTRICTED = "ACCESS_RESTRICTED"


class WeatherAlertSeverity(str, Enum):
    """Standardized Common Alerting Protocol (CAP) severity."""
    EXTREME = "EXTREME"
    SEVERE = "SEVERE"
    MODERATE = "MODERATE"
    MINOR = "MINOR"
    UNKNOWN = "UNKNOWN"


class FreshnessPolicy(BaseModel):
    """Freshness policy governing TTL, stale horizons, and latency thresholds."""
    category: LiveObservationCategory
    nominal_latency_seconds: float = 30.0
    stale_threshold_seconds: float = 300.0
    expired_threshold_seconds: float = 3600.0


class LiveGeoProvider(BaseModel):
    """Metadata and operational status for an authorized live data provider."""
    provider_id: str
    name: str
    category: LiveObservationCategory
    status: ProviderStatus = ProviderStatus.ONLINE
    configured: bool = True
    requires_auth: bool = False
    nominal_latency_seconds: float = 15.0
    ttl_seconds: int = 300
    last_sync_at: Optional[datetime] = None
    rate_limit_remaining: Optional[int] = None
    attribution: str
    license_note: str
    endpoint_url: Optional[str] = None
    status_reason: Optional[str] = None


class AtlasGeoObservation(BaseModel):
    """Unified institutional geospatial observation envelope."""
    observation_id: str
    category: LiveObservationCategory
    data_class: ObservationDataClass = ObservationDataClass.OBSERVED
    entity_id: str
    entity_name: Optional[str] = None
    provider_id: str
    product_id: str
    source_revision: int = 1
    longitude: float
    latitude: float
    altitude_m: Optional[float] = None
    heading_deg: Optional[float] = None
    speed_mps: Optional[float] = None
    vertical_rate_mps: Optional[float] = None
    geometry: Dict[str, Any]
    observed_at: datetime
    source_published_at: Optional[datetime] = None
    received_at: datetime
    ingested_at: datetime
    freshness_state: FreshnessState = FreshnessState.CURRENT
    freshness_age_seconds: float = 0.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    source_attribution: str = ""
    provenance_note: Optional[str] = None
    sequence_number: int = 0


class LiveAircraftState(BaseModel):
    """ADS-B aircraft flight state vector."""
    icao24: str
    callsign: Optional[str] = None
    origin_country: str
    time_position_utc: datetime
    last_contact_utc: datetime
    longitude: float
    latitude: float
    baro_altitude_m: Optional[float] = None
    geo_altitude_m: Optional[float] = None
    on_ground: bool = False
    velocity_mps: Optional[float] = None
    true_track_deg: Optional[float] = None
    vertical_rate_mps: Optional[float] = None
    squawk: Optional[str] = None
    spi: bool = False
    position_source: str = "ADS-B"


class LiveVesselState(BaseModel):
    """AIS maritime vessel position and voyage report."""
    mmsi: str
    imo: Optional[str] = None
    vessel_name: str
    ship_type: str
    nav_status: str
    longitude: float
    latitude: float
    cog_deg: Optional[float] = None
    sog_knots: Optional[float] = None
    heading_deg: Optional[float] = None
    draught_m: Optional[float] = None
    destination: Optional[str] = None
    eta_utc: Optional[datetime] = None
    time_position_utc: datetime


class SatelliteOrbitalElements(BaseModel):
    """Two-Line Element (TLE) / OMM Keplerian orbital elements."""
    norad_cat_id: int
    name: str
    intl_designator: str
    epoch_utc: datetime
    inclination_deg: float
    raan_deg: float
    eccentricity: float
    arg_perigee_deg: float
    mean_anomaly_deg: float
    mean_motion_rev_day: float
    bstar: float = 0.0
    period_minutes: float
    apogee_km: float
    perigee_km: float


class SatelliteState(BaseModel):
    """SGP4-propagated satellite instantaneous state."""
    norad_cat_id: int
    name: str
    propagated_at_utc: datetime
    epoch_utc: datetime
    epoch_age_days: float
    is_stale_epoch: bool = False
    subpoint_latitude: float
    subpoint_longitude: float
    altitude_km: float
    velocity_km_s: float
    footprint_radius_km: float
    data_class: ObservationDataClass = ObservationDataClass.PROPAGATED
    provenance_note: str = "PROPAGATED FROM ORBITAL ELEMENTS (SGP4)"


class EarthquakeEvent(BaseModel):
    """USGS Earthquake event record."""
    event_id: str
    title: str
    place: str
    magnitude: float
    magnitude_type: str
    depth_km: float
    time_utc: datetime
    updated_utc: datetime
    status: str
    tsunami: int = 0
    felt: Optional[int] = None
    alert_color: Optional[str] = None
    significance: int = 0
    longitude: float
    latitude: float
    source_revision: int = 1
    revision_history: List[Dict[str, Any]] = Field(default_factory=list)


class FireDetection(BaseModel):
    """NASA FIRMS thermal anomaly / active fire detection."""
    detection_id: str
    latitude: float
    longitude: float
    brightness_kelvin: float
    scan: float
    track: float
    acq_date: str
    acq_time: str
    satellite: str
    confidence: str
    frp_mw: float
    daynight: str
    instrument: str = "VIIRS"


class WeatherAlert(BaseModel):
    """NOAA / NWS Common Alerting Protocol (CAP) active alert."""
    alert_id: str
    event: str
    headline: str
    severity: WeatherAlertSeverity
    urgency: str
    certainty: str
    effective_utc: datetime
    expires_utc: datetime
    area_desc: str
    polygon_geojson: Optional[Dict[str, Any]] = None


class WeatherObservation(BaseModel):
    """Surface weather station observation (METAR / NOAA)."""
    station_id: str
    station_name: str
    observation_time_utc: datetime
    temperature_c: Optional[float] = None
    dew_point_c: Optional[float] = None
    pressure_hpa: Optional[float] = None
    wind_speed_mps: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    wind_gust_mps: Optional[float] = None
    visibility_m: Optional[float] = None
    condition_text: Optional[str] = None
    longitude: float
    latitude: float


class TrajectorySegment(BaseModel):
    """Trajectory segment split by temporal or spatial distance gaps."""
    entity_id: str
    category: LiveObservationCategory
    segment_id: str
    start_time: datetime
    end_time: datetime
    point_count: int
    coordinates: List[List[float]]
    timestamps: List[datetime]
    has_gap_break: bool = False
    gap_reason: Optional[str] = None


class InfrastructureProximityMatch(BaseModel):
    """Correlation between live event and physical infrastructure (Stage 133)."""
    facility_id: str
    facility_name: str
    facility_sector: str
    facility_coordinates: List[float]
    observation_id: str
    observation_category: LiveObservationCategory
    event_entity_id: str
    distance_km: float
    inside_alert_perimeter: bool = False
    severity: Optional[str] = None
    damage_assessment: str = "UNVERIFIED_PROXIMITY_ONLY"
    damage_confirmed: bool = False
    disclaimer: str = (
        "Spatial proximity does not constitute physical damage, structural failure, "
        "or operational outage. On-site telemetry or official inspection required."
    )

