"""Unit and Integration Tests for ATLAS Stage 134 — Live Physical-World Intelligence.

Validates all 15 institutional test fixtures (Fixtures A through O):
- Fixture A: Event revision deduplication & in-place upsert
- Fixture B: Freshness evaluation engine & clock invariants
- Fixture C: Watermark tracking & out-of-order packet protection
- Fixture D: Trajectory gap splitting invariant
- Fixture E: Orbital mechanics propagation (SGP4)
- Fixture F: Stale orbital epoch alerts and critical thresholds
- Fixture G: NASA FIRMS map key gating & zero fabrication
- Fixture H: NWS CAP weather alert polygon parsing
- Fixture I & K: Multi-provider redundancy & licensed provider gating
- Fixture J: Snapshot & cursor-based delta sync
- Fixture L: High-volume spatial aggregation with H3
- Fixture M: Infrastructure proximity correlation (no damage assertion)
- Fixture N: Historical temporal playback scrubbing
- Fixture O: Viewport bounding box filtering & validation
- FastAPI Endpoints: Comprehensive HTTP route verification
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from atlas.maps.live.adapters.authorized_aircraft import AuthorizedAircraftAdapter
from atlas.maps.live.adapters.authorized_ais import AuthorizedAISAdapter
from atlas.maps.live.adapters.celestrak import CelesTrakAdapter
from atlas.maps.live.adapters.nasa_firms import NASAFIRMSAdapter
from atlas.maps.live.adapters.nws_weather import NWSWeatherAdapter
from atlas.maps.live.adapters.usgs_earthquakes import USGSEarthquakeAdapter
from atlas.maps.live.analytics.h3_live import aggregate_live_observations_to_h3
from atlas.maps.live.analytics.infrastructure_proximity import correlate_infrastructure_proximity
from atlas.maps.live.domain import (
    AtlasGeoObservation,
    EarthquakeEvent,
    FreshnessState,
    LiveObservationCategory,
    ObservationDataClass,
    ProviderStatus,
    SatelliteOrbitalElements,
    WeatherAlertSeverity,
)
from atlas.maps.live.errors import (
    LiveCoordinatesInvalidError,
    LiveStaleOrbitElementsError,
)
from atlas.maps.live.orbital.elements import parse_tle_pair
from atlas.maps.live.orbital.propagation import propagate_satellite
from atlas.maps.live.seed import (
    AIRCRAFT_GAP_POINTS,
    CRITICAL_STALE_ELEMENTS,
    EARTHQUAKE_INITIAL_GEOJSON,
    EARTHQUAKE_REVISED_GEOJSON,
    FIRMS_DETECTIONS_RAW,
    ISS_ELEMENTS,
    NOW_UTC,
    NWS_WEATHER_ALERT_GEOJSON,
    SEED_INFRASTRUCTURE_FACILITIES,
    STALE_SATELLITE_ELEMENTS,
)
from atlas.maps.live.service import AtlasLiveGeoService
from atlas.maps.live.state.hot_store import LiveHotStateStore
from atlas.maps.live.temporal.freshness import evaluate_freshness
from atlas.maps.live.temporal.revisions import EventRevisionManager
from atlas.maps.live.temporal.watermarks import WatermarkManager
from atlas.maps.live.trajectories.gap_splitter import split_trajectory_points
from atlas_api.main import app


@pytest.fixture
def client():
    return TestClient(app)


# --------------------------------------------------------------------------
# Fixture A: Event Revision Deduplication & Upsert
# --------------------------------------------------------------------------
def test_fixture_a_earthquake_revision_upsert():
    rev_manager = EventRevisionManager()
    adapter = USGSEarthquakeAdapter(revision_manager=rev_manager)

    # Ingest initial earthquake (M 5.2)
    eq1, obs1, is_new1 = adapter.parse_feature(EARTHQUAKE_INITIAL_GEOJSON)
    assert is_new1 is True
    assert eq1.magnitude == 5.2
    assert eq1.source_revision == 1
    assert len(rev_manager.list_events()) == 1

    # Ingest revised earthquake (M 5.4, updated depth and status)
    eq2, obs2, is_new2 = adapter.parse_feature(EARTHQUAKE_REVISED_GEOJSON)
    assert is_new2 is False  # Must NOT be marked as a new event!
    assert eq2.magnitude == 5.4
    assert eq2.source_revision == 2
    # Invariant: Event count MUST remain exactly 1 (no duplicate inflation)
    assert len(rev_manager.list_events()) == 1

    # Invariant: Revision history contains both records
    assert len(eq2.revision_history) == 2
    assert eq2.revision_history[0]["magnitude"] == 5.2
    assert eq2.revision_history[1]["magnitude"] == 5.4


# --------------------------------------------------------------------------
# Fixture B: Freshness Evaluation Engine
# --------------------------------------------------------------------------
def test_fixture_b_freshness_evaluation():
    base_time = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)

    # 1. CURRENT state: 5 seconds ago for aircraft
    st1, age1 = evaluate_freshness(base_time - timedelta(seconds=5), LiveObservationCategory.AIRCRAFT, now_utc=base_time)
    assert st1 == FreshnessState.CURRENT
    assert age1 == 5.0

    # 2. DELAYED state: 60 seconds ago for aircraft (nominal latency is 10s, stale threshold is 120s)
    st2, age2 = evaluate_freshness(base_time - timedelta(seconds=60), LiveObservationCategory.AIRCRAFT, now_utc=base_time)
    assert st2 == FreshnessState.DELAYED
    assert age2 == 60.0

    # 3. STALE state: 300 seconds ago for aircraft (exceeds 120s stale threshold)
    st3, age3 = evaluate_freshness(base_time - timedelta(seconds=300), LiveObservationCategory.AIRCRAFT, now_utc=base_time)
    assert st3 == FreshnessState.STALE

    # 4. EXPIRED state: 1200 seconds ago for aircraft (exceeds 900s expiration)
    st4, age4 = evaluate_freshness(base_time - timedelta(seconds=1200), LiveObservationCategory.AIRCRAFT, now_utc=base_time)
    assert st4 == FreshnessState.EXPIRED

    # 5. Alert with past expires_utc -> EXPIRED
    st5, _ = evaluate_freshness(
        base_time - timedelta(minutes=10),
        LiveObservationCategory.WEATHER_ALERT,
        now_utc=base_time,
        expires_utc=base_time - timedelta(minutes=1),
    )
    assert st5 == FreshnessState.EXPIRED


# --------------------------------------------------------------------------
# Fixture C: Watermarks & Out-of-Order Packet Protection
# --------------------------------------------------------------------------
def test_fixture_c_watermark_protection():
    store = LiveHotStateStore()
    t_newer = datetime(2026, 10, 31, 12, 5, 0, tzinfo=timezone.utc)
    t_older = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)

    # Newer observation arrives first at T2 (12:05)
    obs_t2 = AtlasGeoObservation(
        observation_id="flight-001-t2",
        category=LiveObservationCategory.AIRCRAFT,
        entity_id="UAL1842",
        provider_id="opensky",
        product_id="adsb",
        longitude=-122.38,
        latitude=37.62,
        geometry={"type": "Point", "coordinates": [-122.38, 37.62]},
        observed_at=t_newer,
        received_at=t_newer,
        ingested_at=t_newer,
    )
    obs_res, updated = store.ingest_observation(obs_t2)
    assert updated is True
    assert store._active_state["UAL1842"].longitude == -122.38

    # Delayed out-of-order packet arrives at T1 (12:00)
    obs_t1 = AtlasGeoObservation(
        observation_id="flight-001-t1",
        category=LiveObservationCategory.AIRCRAFT,
        entity_id="UAL1842",
        provider_id="opensky",
        product_id="adsb",
        longitude=-122.10,
        latitude=37.75,
        geometry={"type": "Point", "coordinates": [-122.10, 37.75]},
        observed_at=t_older,
        received_at=t_newer + timedelta(seconds=2),
        ingested_at=t_newer + timedelta(seconds=2),
    )
    obs_res2, updated2 = store.ingest_observation(obs_t1)
    # Invariant: Older arrival must NOT update hot active state!
    assert updated2 is False
    assert store._active_state["UAL1842"].longitude == -122.38  # Preserved at T2 position!


# --------------------------------------------------------------------------
# Fixture D: Trajectory Gap Splitting Invariant
# --------------------------------------------------------------------------
def test_fixture_d_trajectory_gap_splitting():
    segments = split_trajectory_points(
        points=AIRCRAFT_GAP_POINTS,
        category=LiveObservationCategory.AIRCRAFT,
        entity_id="UAL1842",
        max_gap_seconds=900.0,  # 15 minutes
    )
    # Invariant: 45-minute transponder blackout must split into exactly 2 distinct segments
    assert len(segments) == 2
    assert segments[0].point_count == 3
    assert segments[1].point_count == 2
    assert segments[1].has_gap_break is True
    assert "Tracking blackout" in str(segments[1].gap_reason)


# --------------------------------------------------------------------------
# Fixture E: Orbital Mechanics Propagation (SGP4)
# --------------------------------------------------------------------------
def test_fixture_e_orbital_propagation():
    sat_state = propagate_satellite(ISS_ELEMENTS, propagate_at=NOW_UTC)
    assert -90.0 <= sat_state.subpoint_latitude <= 90.0
    assert -180.0 <= sat_state.subpoint_longitude <= 180.0
    # ISS orbital altitude is between 400 and 435 km
    assert 400.0 <= sat_state.altitude_km <= 440.0
    # Orbital velocity is ~7.6 km/s
    assert 7.4 <= sat_state.velocity_km_s <= 7.8
    # Footprint radius ~2200 km
    assert 2000.0 <= sat_state.footprint_radius_km <= 2500.0
    assert sat_state.data_class == ObservationDataClass.PROPAGATED
    assert sat_state.provenance_note == "PROPAGATED FROM ORBITAL ELEMENTS (SGP4)"


# --------------------------------------------------------------------------
# Fixture F: Stale Orbital Epoch Alerts
# --------------------------------------------------------------------------
def test_fixture_f_stale_orbital_epoch():
    # 25-day old epoch: should flag is_stale_epoch == True
    state_stale = propagate_satellite(STALE_SATELLITE_ELEMENTS, propagate_at=NOW_UTC)
    assert state_stale.is_stale_epoch is True
    assert state_stale.epoch_age_days >= 24.0

    # 35-day old epoch with fail_on_critical_stale=True: should raise LiveStaleOrbitElementsError
    with pytest.raises(LiveStaleOrbitElementsError) as exc_info:
        propagate_satellite(CRITICAL_STALE_ELEMENTS, propagate_at=NOW_UTC, fail_on_critical_stale=True)
    assert "exceeds" in str(exc_info.value)
    assert "tens of kilometers" in str(exc_info.value)


# --------------------------------------------------------------------------
# Fixture G: NASA FIRMS Map Key Gating & Zero Simulation Invariant
# --------------------------------------------------------------------------
def test_fixture_g_nasa_firms_gating():
    firms = NASAFIRMSAdapter(map_key=None)
    meta = firms.get_provider_metadata()
    assert meta.status == ProviderStatus.UNCONFIGURED
    assert meta.configured is False
    assert "MAP_KEY required" in str(meta.status_reason)

    # Parsing genuine telemetry
    det, obs = firms.parse_detection_row(FIRMS_DETECTIONS_RAW[0])
    assert det.frp_mw == 142.8
    assert obs.category == LiveObservationCategory.ACTIVE_FIRE
    assert obs.source_attribution == "NASA FIRMS"


# --------------------------------------------------------------------------
# Fixture H: NWS CAP Weather Alert Polygon Parsing
# --------------------------------------------------------------------------
def test_fixture_h_nws_weather_alert_polygon():
    nws = NWSWeatherAdapter()
    alert, obs = nws.parse_cap_feature(NWS_WEATHER_ALERT_GEOJSON)
    assert alert.severity == WeatherAlertSeverity.SEVERE
    assert alert.event == "Flash Flood Warning"
    assert obs.geometry["type"] == "Polygon"
    assert len(obs.geometry["coordinates"][0]) == 5
    assert -96.0 <= obs.longitude <= -94.0
    assert 29.0 <= obs.latitude <= 30.0


# --------------------------------------------------------------------------
# Fixture I & K: Licensed Provider Gating
# --------------------------------------------------------------------------
def test_fixture_i_k_licensed_providers():
    aircraft = AuthorizedAircraftAdapter(client_id=None, client_secret=None)
    meta_ac = aircraft.get_provider_metadata()
    assert meta_ac.status == ProviderStatus.UNCONFIGURED
    assert meta_ac.configured is False

    ais = AuthorizedAISAdapter(api_key=None)
    meta_ais = ais.get_provider_metadata()
    assert meta_ais.status == ProviderStatus.UNCONFIGURED
    assert meta_ais.configured is False


# --------------------------------------------------------------------------
# Fixture J: Snapshot & Cursor-based Delta Sync
# --------------------------------------------------------------------------
def test_fixture_j_snapshot_and_delta_sync():
    store = LiveHotStateStore()
    t0 = datetime(2026, 10, 31, 10, 0, 0, tzinfo=timezone.utc)

    obs1 = AtlasGeoObservation(
        observation_id="o1",
        category=LiveObservationCategory.VESSEL,
        entity_id="MMSI1",
        provider_id="ais",
        product_id="ais",
        longitude=-122.3,
        latitude=37.8,
        geometry={"type": "Point", "coordinates": [-122.3, 37.8]},
        observed_at=t0,
        received_at=t0,
        ingested_at=t0,
    )
    store.ingest_observation(obs1)

    snap, cursor = store.get_snapshot()
    assert len(snap) == 1
    assert cursor == 1001

    # Ingest next observation
    obs2 = AtlasGeoObservation(
        observation_id="o2",
        category=LiveObservationCategory.VESSEL,
        entity_id="MMSI2",
        provider_id="ais",
        product_id="ais",
        longitude=-122.4,
        latitude=37.9,
        geometry={"type": "Point", "coordinates": [-122.4, 37.9]},
        observed_at=t0 + timedelta(seconds=10),
        received_at=t0 + timedelta(seconds=10),
        ingested_at=t0 + timedelta(seconds=10),
    )
    store.ingest_observation(obs2)

    # Query deltas since previous cursor
    deltas, new_cursor = store.get_deltas(since_sequence=cursor)
    assert len(deltas) == 1
    assert deltas[0].entity_id == "MMSI2"
    assert new_cursor == 1002


# --------------------------------------------------------------------------
# Fixture L: H3 Spatial Aggregation
# --------------------------------------------------------------------------
def test_fixture_l_h3_aggregation():
    obs_list = [
        AtlasGeoObservation(
            observation_id=f"obs-{i}",
            category=LiveObservationCategory.AIRCRAFT,
            entity_id=f"PLANE-{i % 3}",  # 3 distinct aircraft
            provider_id="opensky",
            product_id="adsb",
            longitude=-122.38 + i * 0.001,
            latitude=37.62 + i * 0.001,
            geometry={"type": "Point", "coordinates": [-122.38, 37.62]},
            observed_at=NOW_UTC,
            received_at=NOW_UTC,
            ingested_at=NOW_UTC,
        )
        for i in range(10)
    ]
    aggs = aggregate_live_observations_to_h3(obs_list, resolution=4)
    assert len(aggs) >= 1
    agg = aggs[0]
    assert agg["raw_observation_count"] == 10
    assert agg["distinct_entity_count"] == 3
    assert agg["dominant_category"] == "AIRCRAFT"


# --------------------------------------------------------------------------
# Fixture M: Infrastructure Proximity Correlation (No Damage Assertion)
# --------------------------------------------------------------------------
def test_fixture_m_infrastructure_proximity_no_damage():
    service = AtlasLiveGeoService()
    event_dict = {
        "observation_id": "usgs-test-eq",
        "category": "EARTHQUAKE",
        "entity_id": "eq-sf-test",
        "longitude": -122.35,
        "latitude": 37.75,
        "magnitude": 5.8,
    }
    matches = service.correlate_infrastructure_proximity(
        event_dict=event_dict,
        facilities=SEED_INFRASTRUCTURE_FACILITIES,
        max_radius_km=50.0,
    )
    assert len(matches) > 0
    match = matches[0]
    # Invariants:
    assert match.damage_assessment == "UNVERIFIED_PROXIMITY_ONLY"
    assert match.damage_confirmed is False
    assert "does not constitute physical damage" in match.disclaimer


# --------------------------------------------------------------------------
# Fixture N: Historical Playback Scrubbing
# --------------------------------------------------------------------------
def test_fixture_n_playback_scrubbing():
    service = AtlasLiveGeoService()
    # Query playback at NOW_UTC
    snap = service.get_playback_snapshot(target_time_utc=NOW_UTC, window_seconds=7200.0)
    assert len(snap) > 0
    for obs in snap:
        assert obs.freshness_state == FreshnessState.HISTORICAL


# --------------------------------------------------------------------------
# Fixture O: Viewport Bounding Box Filtering
# --------------------------------------------------------------------------
def test_fixture_o_viewport_bounding_box():
    service = AtlasLiveGeoService()
    # SF Bay Area BBox
    sf_bbox = [-123.0, 37.0, -121.5, 38.5]
    snap, _ = service.get_snapshot(bbox=sf_bbox)
    for obs in snap:
        assert -123.0 <= obs.longitude <= -121.5
        assert 37.0 <= obs.latitude <= 38.5

    # Invalid BBox should raise error
    with pytest.raises(LiveCoordinatesInvalidError):
        service.get_snapshot(bbox=[190.0, 37.0, -121.5, 38.5])


# --------------------------------------------------------------------------
# FastAPI Integration Tests
# --------------------------------------------------------------------------
def test_fastapi_live_endpoints(client):
    # 1. Providers list
    res = client.get("/api/v1/maps/live/providers")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) >= 5

    # 2. Specific provider status
    res = client.get("/api/v1/maps/live/providers/celestrak/status")
    assert res.status_code == 200
    assert res.json()["provider_id"] == "celestrak"

    # 3. Live layers catalog
    res = client.get("/api/v1/maps/live/layers")
    assert res.status_code == 200
    assert "layers" in res.json()

    # 4. Snapshot endpoint
    res = client.post("/api/v1/maps/live/observations/snapshot", json={"max_results": 100})
    assert res.status_code == 200
    data = res.json()
    assert "observations" in data
    assert data["count"] > 0

    # 5. Deltas endpoint
    res = client.post("/api/v1/maps/live/observations/deltas", json={"since_sequence": 1000})
    assert res.status_code == 200
    assert "deltas" in res.json()

    # 6. Satellite propagation endpoint
    res = client.post(
        "/api/v1/maps/live/satellites/propagate",
        json={"norad_cat_id": 25544, "propagate_at": NOW_UTC.isoformat()},
    )
    assert res.status_code == 200
    sat_res = res.json()["satellite_state"]
    assert sat_res["norad_cat_id"] == 25544
    assert sat_res["data_class"] == "PROPAGATED"

    # 7. Infrastructure proximity endpoint
    res = client.post(
        "/api/v1/maps/live/infrastructure/proximity",
        json={
            "event": {
                "observation_id": "test-eq",
                "category": "EARTHQUAKE",
                "entity_id": "eq-1",
                "longitude": -122.38,
                "latitude": 37.75,
            },
            "max_radius_km": 100.0,
        },
    )
    assert res.status_code == 200
    prox_res = res.json()
    assert prox_res["match_count"] > 0
    assert prox_res["matches"][0]["damage_confirmed"] is False

    # 8. H3 aggregates endpoint
    res = client.post("/api/v1/maps/live/aggregates/h3", json={"resolution": 4})
    assert res.status_code == 200
    assert res.json()["cell_count"] > 0

    # 9. Trajectory split endpoint
    res = client.post(
        "/api/v1/maps/live/trajectories/split",
        json={
            "entity_id": "UAL1842",
            "category": "AIRCRAFT",
            "points": [
                {"longitude": -122.5, "latitude": 37.7, "timestamp": "2026-10-31T05:00:00Z"},
                {"longitude": -122.6, "latitude": 37.8, "timestamp": "2026-10-31T05:05:00Z"},
                {"longitude": -128.0, "latitude": 38.0, "timestamp": "2026-10-31T06:00:00Z"},  # 55 min gap
            ],
            "max_gap_seconds": 900.0,
        },
    )
    assert res.status_code == 200
    assert res.json()["segment_count"] == 2

    # 10. Earthquake revision endpoint
    res = client.post("/api/v1/maps/live/earthquakes/revision", json=EARTHQUAKE_REVISED_GEOJSON)
    assert res.status_code == 200
    rev_res = res.json()
    assert rev_res["is_new_event"] is False
    assert rev_res["earthquake_event"]["magnitude"] == 5.4
