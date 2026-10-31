"""Institutional Reference Seed Data for ATLAS Live Physical-World (Stage 134).

Provides deterministic benchmarks, real-world orbital elements, verified
earthquake records, CAP weather alerts, thermal detections, and test fixtures (A through O).
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from .domain import (
    AtlasGeoObservation,
    FreshnessState,
    LiveObservationCategory,
    ObservationDataClass,
    SatelliteOrbitalElements,
)
from .orbital.elements import parse_tle_pair


NOW_UTC = datetime(2026, 10, 31, 7, 0, 0, tzinfo=timezone.utc)

# --------------------------------------------------------------------------
# Fixture E & F: Satellite Orbital Elements (ISS ZARYA & Starlink)
# --------------------------------------------------------------------------
ISS_TLE_L1 = "1 25544U 98067A   26300.25000000  .00016717  00000-0  10270-3 0  9025"
ISS_TLE_L2 = "2 25544  51.6416 142.1234 0005432  65.4321 294.6543 15.49876543451234"
ISS_ELEMENTS = parse_tle_pair(ISS_TLE_L1, ISS_TLE_L2, name="ISS (ZARYA)")

# Stale satellite elements (Epoch 25 days older than NOW_UTC)
STALE_EPOCH_DT = NOW_UTC - timedelta(days=25)
STALE_SATELLITE_ELEMENTS = SatelliteOrbitalElements(
    norad_cat_id=48011,
    name="STARLINK-3011",
    intl_designator="2021-024A",
    epoch_utc=STALE_EPOCH_DT,
    inclination_deg=53.05,
    raan_deg=75.2,
    eccentricity=0.00015,
    arg_perigee_deg=92.1,
    mean_anomaly_deg=268.0,
    mean_motion_rev_day=15.06,
    bstar=0.000025,
    period_minutes=95.6,
    apogee_km=552.0,
    perigee_km=548.0,
)

# Critical stale elements (35 days old)
CRITICAL_STALE_ELEMENTS = SatelliteOrbitalElements(
    norad_cat_id=99999,
    name="DECOMMISSIONED-SAT",
    intl_designator="2010-099B",
    epoch_utc=NOW_UTC - timedelta(days=35),
    inclination_deg=98.2,
    raan_deg=110.0,
    eccentricity=0.001,
    arg_perigee_deg=45.0,
    mean_anomaly_deg=180.0,
    mean_motion_rev_day=14.2,
    bstar=0.0,
    period_minutes=101.4,
    apogee_km=780.0,
    perigee_km=770.0,
)

# --------------------------------------------------------------------------
# Fixture A: USGS Earthquake Event Revisions (Initial M5.2 -> Revised M5.4)
# --------------------------------------------------------------------------
EARTHQUAKE_INITIAL_GEOJSON: Dict[str, Any] = {
    "type": "Feature",
    "id": "us7000m8v1",
    "properties": {
        "mag": 5.2,
        "place": "14 km ENE of Ridgecrest, CA",
        "time": int((NOW_UTC - timedelta(minutes=20)).timestamp() * 1000),
        "updated": int((NOW_UTC - timedelta(minutes=18)).timestamp() * 1000),
        "status": "automatic",
        "tsunami": 0,
        "sig": 415,
        "magType": "ml",
        "title": "M 5.2 - 14 km ENE of Ridgecrest, CA",
        "alert": "yellow",
    },
    "geometry": {
        "type": "Point",
        "coordinates": [-117.514, 35.688, 8.4],
    },
}

EARTHQUAKE_REVISED_GEOJSON: Dict[str, Any] = {
    "type": "Feature",
    "id": "us7000m8v1",
    "properties": {
        "mag": 5.4,
        "place": "14 km ENE of Ridgecrest, CA",
        "time": int((NOW_UTC - timedelta(minutes=20)).timestamp() * 1000),
        "updated": int((NOW_UTC - timedelta(minutes=5)).timestamp() * 1000),
        "status": "reviewed",
        "tsunami": 0,
        "sig": 462,
        "magType": "mww",
        "title": "M 5.4 - 14 km ENE of Ridgecrest, CA",
        "alert": "yellow",
    },
    "geometry": {
        "type": "Point",
        "coordinates": [-117.514, 35.688, 8.4],
    },
}

# --------------------------------------------------------------------------
# Fixture H: NWS Common Alerting Protocol (CAP) Alert with Polygon Boundary
# --------------------------------------------------------------------------
NWS_WEATHER_ALERT_GEOJSON: Dict[str, Any] = {
    "type": "Feature",
    "id": "NWS-ALERT-HOU-2026-0891",
    "properties": {
        "event": "Flash Flood Warning",
        "headline": "Flash Flood Warning issued October 31 for Harris and Galveston Counties",
        "severity": "Severe",
        "urgency": "Immediate",
        "certainty": "Likely",
        "areaDesc": "Harris, TX; Galveston, TX",
        "effective": (NOW_UTC - timedelta(minutes=30)).isoformat(),
        "expires": (NOW_UTC + timedelta(hours=3)).isoformat(),
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [-95.65, 29.85],
                [-95.10, 29.85],
                [-95.10, 29.40],
                [-95.65, 29.40],
                [-95.65, 29.85],
            ]
        ],
    },
}

# --------------------------------------------------------------------------
# Fixture G: NASA FIRMS Active Fire Detections
# --------------------------------------------------------------------------
FIRMS_DETECTIONS_RAW: List[Dict[str, Any]] = [
    {
        "latitude": 39.8123,
        "longitude": -121.4321,
        "brightness": 348.5,
        "scan": 0.45,
        "track": 0.40,
        "acq_date": "2026-10-31",
        "acq_time": "0540",
        "satellite": "SNPP",
        "confidence": "high",
        "frp": 142.8,
        "daynight": "N",
    },
    {
        "latitude": 39.8250,
        "longitude": -121.4180,
        "brightness": 362.1,
        "scan": 0.45,
        "track": 0.40,
        "acq_date": "2026-10-31",
        "acq_time": "0540",
        "satellite": "SNPP",
        "confidence": "high",
        "frp": 215.3,
        "daynight": "N",
    },
]

# --------------------------------------------------------------------------
# Fixture D: Aircraft Tracking Blackout (45-Minute Gap across Ocean)
# --------------------------------------------------------------------------
AIRCRAFT_GAP_POINTS: List[Dict[str, Any]] = [
    # Segment 1: Approaching coast
    {"longitude": -122.50, "latitude": 37.70, "altitude_m": 10500, "timestamp": NOW_UTC - timedelta(minutes=90)},
    {"longitude": -123.10, "latitude": 37.60, "altitude_m": 10800, "timestamp": NOW_UTC - timedelta(minutes=85)},
    {"longitude": -123.80, "latitude": 37.50, "altitude_m": 11000, "timestamp": NOW_UTC - timedelta(minutes=80)},
    # 45-minute communication blackout / transponder loss
    # Segment 2: Re-acquired by oceanic radar
    {"longitude": -128.90, "latitude": 36.80, "altitude_m": 11000, "timestamp": NOW_UTC - timedelta(minutes=35)},
    {"longitude": -129.70, "latitude": 36.65, "altitude_m": 11000, "timestamp": NOW_UTC - timedelta(minutes=30)},
]

# --------------------------------------------------------------------------
# Fixture M: Stage 133 Physical Infrastructure Assets for Proximity
# --------------------------------------------------------------------------
SEED_INFRASTRUCTURE_FACILITIES: List[Dict[str, Any]] = [
    {
        "facility_id": "FAC-ENERGY-001",
        "facility_name": "Richmond Energy Hub and Refinery",
        "sector": "ENERGY",
        "longitude": -122.388,
        "latitude": 37.935,
        "capacity_value": 250000.0,
        "capacity_unit": "BPD",
    },
    {
        "facility_id": "FAC-PORT-002",
        "facility_name": "Port of Oakland Container Terminal",
        "sector": "PORT",
        "longitude": -122.302,
        "latitude": 37.801,
        "capacity_value": 2400000.0,
        "capacity_unit": "TEU_PER_YEAR",
    },
    {
        "facility_id": "FAC-AIRPORT-003",
        "facility_name": "San Francisco International Airport (SFO)",
        "sector": "AIRPORT",
        "longitude": -122.375,
        "latitude": 37.619,
        "capacity_value": 55000000.0,
        "capacity_unit": "PASSENGERS_PER_YEAR",
    },
    {
        "facility_id": "FAC-DATACENTER-004",
        "facility_name": "Silicon Valley Cloud Supercluster DC1",
        "sector": "DATA_CENTER",
        "longitude": -121.968,
        "latitude": 37.386,
        "capacity_value": 120.0,
        "capacity_unit": "MW",
    },
    {
        "facility_id": "FAC-ENERGY-HOUSTON",
        "facility_name": "Houston Ship Channel Petrochemical Complex",
        "sector": "ENERGY",
        "longitude": -95.250,
        "latitude": 29.720,
        "capacity_value": 450000.0,
        "capacity_unit": "BPD",
    },
]

# --------------------------------------------------------------------------
# Benchmark Aircraft & Vessel Observations
# --------------------------------------------------------------------------
SEED_AIRCRAFT_OBSERVATIONS: List[AtlasGeoObservation] = [
    AtlasGeoObservation(
        observation_id="adsb-a45b1c-1761894000",
        category=LiveObservationCategory.AIRCRAFT,
        data_class=ObservationDataClass.OBSERVED,
        entity_id="a45b1c",
        entity_name="UAL1842",
        provider_id="opensky_network",
        product_id="adsb_state_vectors",
        source_revision=1,
        longitude=-122.385,
        latitude=37.615,
        altitude_m=3500.0,
        heading_deg=285.0,
        speed_mps=140.0,
        vertical_rate_mps=-5.2,
        geometry={"type": "Point", "coordinates": [-122.385, 37.615]},
        observed_at=NOW_UTC - timedelta(seconds=15),
        source_published_at=NOW_UTC - timedelta(seconds=12),
        received_at=NOW_UTC - timedelta(seconds=8),
        ingested_at=NOW_UTC - timedelta(seconds=7),
        freshness_state=FreshnessState.CURRENT,
        properties={
            "callsign": "UAL1842",
            "icao24": "a45b1c",
            "squawk": "3421",
            "baro_altitude_m": 3500.0,
            "origin_country": "United States",
        },
        source_attribution="OpenSky Network ADS-B",
        provenance_note="Measured ADS-B State Vector",
    ),
    AtlasGeoObservation(
        observation_id="adsb-400a21-1761893980",
        category=LiveObservationCategory.AIRCRAFT,
        data_class=ObservationDataClass.OBSERVED,
        entity_id="400a21",
        entity_name="BAW287",
        provider_id="opensky_network",
        product_id="adsb_state_vectors",
        source_revision=1,
        longitude=-122.150,
        latitude=37.720,
        altitude_m=8500.0,
        heading_deg=310.0,
        speed_mps=220.0,
        vertical_rate_mps=0.0,
        geometry={"type": "Point", "coordinates": [-122.150, 37.720]},
        observed_at=NOW_UTC - timedelta(seconds=45),
        source_published_at=NOW_UTC - timedelta(seconds=40),
        received_at=NOW_UTC - timedelta(seconds=35),
        ingested_at=NOW_UTC - timedelta(seconds=34),
        freshness_state=FreshnessState.CURRENT,
        properties={
            "callsign": "BAW287",
            "icao24": "400a21",
            "squawk": "7102",
            "origin_country": "United Kingdom",
        },
        source_attribution="OpenSky Network ADS-B",
        provenance_note="Measured ADS-B State Vector",
    ),
]

SEED_VESSEL_OBSERVATIONS: List[AtlasGeoObservation] = [
    AtlasGeoObservation(
        observation_id="ais-368123450-1761893800",
        category=LiveObservationCategory.VESSEL,
        data_class=ObservationDataClass.OBSERVED,
        entity_id="368123450",
        entity_name="EVER GOLDEN",
        provider_id="spire_ais",
        product_id="ais_position_reports",
        source_revision=1,
        longitude=-122.340,
        latitude=37.810,
        altitude_m=0.0,
        heading_deg=180.0,
        speed_mps=6.2,
        geometry={"type": "Point", "coordinates": [-122.340, 37.810]},
        observed_at=NOW_UTC - timedelta(minutes=2),
        source_published_at=NOW_UTC - timedelta(minutes=2),
        received_at=NOW_UTC - timedelta(seconds=90),
        ingested_at=NOW_UTC - timedelta(seconds=88),
        freshness_state=FreshnessState.CURRENT,
        properties={
            "mmsi": "368123450",
            "imo": "9811000",
            "vessel_name": "EVER GOLDEN",
            "ship_type": "Container Ship (Fully Cellular)",
            "nav_status": "Under way using engine",
            "sog_knots": 12.0,
            "draught_m": 14.8,
            "destination": "US OAK",
        },
        source_attribution="Spire Maritime AIS",
        provenance_note="Measured AIS Transponder Position",
    ),
]
