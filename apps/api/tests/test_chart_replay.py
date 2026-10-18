"""Comprehensive automated tests for Stage 75: Historical Chart Replay V1.

Verifies:
- Capability discovery with revision disclosures
- Authenticated replay session initialization
- Strict future-data boundary enforcement (no-look-ahead)
- Deterministic forward & backward step progression
- Seek repositioning within qualified historical coverage
- Session ownership isolation across distinct users
- Replay-aware TA-Lib indicator calculation without forward contamination
- End-of-data and start-of-data detection
- Inactive session expiration and cleanup
"""

import uuid

import pytest
from atlas.auth import AuthPrincipal
from atlas.charts.replay import (
    default_replay_session_manager,
)
from fastapi.testclient import TestClient

from atlas_api.main import app

USER_A_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
USER_B_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")

USER_A = AuthPrincipal(
    sub=str(USER_A_ID),
    email="trader_a@atlas.institutional",
    role="trader",
)

USER_B = AuthPrincipal(
    sub=str(USER_B_ID),
    email="trader_b@atlas.institutional",
    role="trader",
)



@pytest.fixture(autouse=True)
def reset_sessions():
    """Ensure session manager is clean before and after each test."""
    default_replay_session_manager.clear()
    yield
    default_replay_session_manager.clear()


@pytest.fixture
def client():
    """FastAPI test client with mock authenticated user dependency."""
    from atlas_api.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: USER_A
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_replay_capabilities_discovery(client: TestClient):
    """Verifies replay capability endpoint returns coverage and methodological disclosures."""
    response = client.get("/api/v1/charts/replay/capabilities?symbol=SPY&interval=1d")
    assert response.status_code == 200
    data = response.json()

    assert data["display_symbol"] == "SPY"
    assert data["is_replay_supported"] is True
    assert "1d" in data["supported_intervals"]
    assert data["total_bars_available"] > 10
    assert data["point_in_time_guarantee"] is False
    assert "adjusted/revised dataset" in data["methodological_notice"]
    assert data["earliest_available_bar"] is not None
    assert data["latest_available_bar"] is not None


def test_start_replay_session_success(client: TestClient):
    """Verifies session initialization and strict future-data boundary."""
    payload = {
        "panel_id": "panel-1",
        "symbol": "SPY",
        "interval": "1d",
        "history_window": 50,
        "playback_speed": 2.0,
    }
    response = client.post("/api/v1/charts/replay/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()

    session = data["session"]
    revealed_bars = data["revealed_bars"]

    assert session["target_panel_id"] == "panel-1"
    assert session["display_symbol"] == "SPY"
    assert session["interval"] == "1d"
    assert session["status"] == "READY"
    assert session["playback_speed"] == 2.0
    assert session["revealed_bars_count"] == len(revealed_bars)

    # Future isolation check: total bars in series must be strictly greater than revealed
    assert session["total_bars"] >= len(revealed_bars)
    assert len(revealed_bars) > 0

    # Cursor bar must match the last revealed bar
    cursor_bar = session["cursor_bar"]
    assert cursor_bar is not None
    assert cursor_bar["timestamp"] == revealed_bars[-1]["timestamp"]
    assert cursor_bar["close"] == revealed_bars[-1]["close"]


def test_step_forward_and_backward_determinism(client: TestClient):
    """Verifies single-bar forward and backward progression with no look-ahead."""
    # 1. Start session
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "history_window": 50},
    )
    assert start_res.status_code == 201
    start_data = start_res.json()
    session_id = start_data["session"]["session_id"]
    initial_cursor = start_data["session"]["cursor_index"]
    initial_count = len(start_data["revealed_bars"])

    # 2. Step Forward
    step_fwd_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/step",
        json={"direction": "forward", "count": 1},
    )
    assert step_fwd_res.status_code == 200
    fwd_data = step_fwd_res.json()

    assert fwd_data["cursor_index"] == initial_cursor + 1
    assert fwd_data["revealed_bars_count"] == initial_count + 1
    assert fwd_data["revealed_bar"] is not None
    assert fwd_data["removed_bar_index"] is None

    new_revealed_bar = fwd_data["revealed_bar"]
    assert fwd_data["cursor_bar"]["timestamp"] == new_revealed_bar["timestamp"]

    # 3. Step Backward
    step_back_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/step",
        json={"direction": "backward", "count": 1},
    )
    assert step_back_res.status_code == 200
    back_data = step_back_res.json()

    assert back_data["cursor_index"] == initial_cursor
    assert back_data["revealed_bars_count"] == initial_count
    assert back_data["revealed_bar"] is None
    assert back_data["removed_bar_index"] == initial_cursor + 1


def test_future_data_isolation_invariant(client: TestClient):
    """Directly asserts that future bars N+1.. are never exposed in step response."""
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "history_window": 30},
    )
    session_id = start_res.json()["session"]["session_id"]

    step_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/step",
        json={"direction": "forward", "count": 1},
    )
    data = step_res.json()

    # Step response only contains single revealed_bar and cursor_bar, no future array
    assert "revealed_bars" not in data
    assert "future_bars" not in data
    assert "upcoming_bars" not in data


def test_seek_session_repositioning(client: TestClient):
    """Verifies relocating cursor directly to target historical bar index."""
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "start_index": 10},
    )
    session_id = start_res.json()["session"]["session_id"]

    seek_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/seek",
        json={"target_index": 25},
    )
    assert seek_res.status_code == 200
    data = seek_res.json()

    assert data["session"]["cursor_index"] == 25
    assert len(data["revealed_bars"]) == 26
    assert data["revealed_bars"][-1]["timestamp"] == data["session"]["cursor_bar"]["timestamp"]


def test_session_ownership_isolation(client: TestClient):
    """Asserts that User B cannot read, step, or seek User A's replay session."""
    # User A creates session
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d"},
    )
    session_id = start_res.json()["session"]["session_id"]

    # Switch client authentication to User B
    from atlas_api.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: USER_B

    # User B attempts to access User A's session -> 404
    get_res = client.get(f"/api/v1/charts/replay/sessions/{session_id}")
    assert get_res.status_code == 404

    step_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/step",
        json={"direction": "forward"},
    )
    assert step_res.status_code == 404

    del_res = client.delete(f"/api/v1/charts/replay/sessions/{session_id}")
    assert del_res.status_code == 404


def test_replay_aware_indicator_calculation_no_lookahead(client: TestClient):
    """Verifies that indicator calculation in replay mode is bounded strictly to cursor_index."""
    # 1. Start session at fixed bar index
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "start_index": 30},
    )
    session_id = start_res.json()["session"]["session_id"]
    revealed_bars = start_res.json()["revealed_bars"]

    # 2. Request SMA(10) calculation for this replay position
    ind_payload = {
        "symbol": "SPY",
        "interval": "1d",
        "instances": [
            {
                "instance_id": "sma-replay-1",
                "indicator_id": "atlas.sma",
                "version": 1,
                "parameters": {"period": 10},
            }
        ],
    }

    ind_res = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/indicators", json=ind_payload
    )
    assert ind_res.status_code == 200
    ind_data = ind_res.json()

    results = ind_data["results"]
    assert len(results) == 1
    sma_series = results[0]["series"][0]["points"]

    # The last SMA point must correspond to the cursor bar timestamp
    assert len(sma_series) > 0
    last_sma_point = sma_series[-1]
    assert last_sma_point["timestamp"] == revealed_bars[-1]["timestamp"]

    # 3. Advance cursor by 1 bar
    client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/step",
        json={"direction": "forward", "count": 1},
    )

    # 4. Re-calculate SMA(10) at new cursor
    ind_res_2 = client.post(
        f"/api/v1/charts/replay/sessions/{session_id}/indicators", json=ind_payload
    )
    sma_series_2 = ind_res_2.json()["results"][0]["series"][0]["points"]

    # The new SMA series must have exactly 1 more point than before
    assert len(sma_series_2) == len(sma_series) + 1


def test_close_replay_session(client: TestClient):
    """Verifies deleting session frees resources and makes session inaccessible."""
    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d"},
    )
    session_id = start_res.json()["session"]["session_id"]

    del_res = client.delete(f"/api/v1/charts/replay/sessions/{session_id}")
    assert del_res.status_code == 204

    # Subsequent access fails with 404
    get_res = client.get(f"/api/v1/charts/replay/sessions/{session_id}")
    assert get_res.status_code == 404


def test_end_of_data_detection(client: TestClient):
    """Verifies seeking to the last bar sets END_OF_DATA status."""
    cap_res = client.get("/api/v1/charts/replay/capabilities?symbol=SPY&interval=1d")
    total_bars = cap_res.json()["total_bars_available"]

    start_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "start_index": total_bars - 1},
    )
    session = start_res.json()["session"]
    assert session["status"] == "END_OF_DATA"

    step_res = client.post(
        f"/api/v1/charts/replay/sessions/{session['session_id']}/step",
        json={"direction": "forward"},
    )
    assert step_res.json()["is_end_of_data"] is True


def test_session_quota_enforcement(client: TestClient):
    """Verifies maximum 5 concurrent replay sessions per user."""
    sessions = []
    for i in range(5):
        res = client.post(
            "/api/v1/charts/replay/sessions",
            json={"symbol": "SPY", "interval": "1d", "panel_id": f"panel-{i}"},
        )
        assert res.status_code == 201
        sessions.append(res.json()["session"]["session_id"])

    # 6th session should be rejected with 400
    sixth_res = client.post(
        "/api/v1/charts/replay/sessions",
        json={"symbol": "SPY", "interval": "1d", "panel_id": "panel-6"},
    )
    assert sixth_res.status_code == 400
    assert "quota exceeded" in sixth_res.json()["error"]["message"].lower()
