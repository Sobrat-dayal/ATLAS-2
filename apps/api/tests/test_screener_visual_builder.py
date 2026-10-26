"""Stage 95: Automated tests for Visual Screener Filter presentation metadata, issue attribution, and contradiction detection."""

import pytest
from atlas.screeners import ScreenerRepository, ScreenerService
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.routers.screeners import get_screener_service
from atlas_api.routers.screeners import router as screeners_router


@pytest.fixture
def repo():
    return ScreenerRepository()


@pytest.fixture
def service(repo):
    return ScreenerService(repository=repo)


@pytest.fixture
def client(service: ScreenerService) -> TestClient:
    app = FastAPI()
    app.include_router(screeners_router)
    app.dependency_overrides[get_screener_service] = lambda: service
    return TestClient(app)


def test_filters_registry_includes_stage95_presentation_metadata(client: TestClient):
    """Verify that filter definitions include typed editor metadata, aliases, and methodologies."""
    response = client.get("/screeners/filters")
    assert response.status_code == 200
    filters = response.json()
    assert len(filters) >= 20

    mcap = next(f for f in filters if f["filter_id"] == "market_cap")
    assert mcap["editor_type"] == "monetary_input"
    assert "USD" in mcap["currency_options"]
    assert "BILLIONS" in mcap["magnitude_options"]
    assert "mcap" in mcap["aliases"]
    assert "Total shares outstanding" in mcap["methodology_reference"]
    assert mcap["decimal_precision"] == 2

    pe = next(f for f in filters if f["filter_id"] == "pe_ratio")
    assert pe["editor_type"] == "multiple_input"
    assert "pe" in pe["aliases"]
    assert "Price to Earnings" in pe["methodology_reference"]

    vol = next(f for f in filters if f["filter_id"] == "volume_latest")
    assert vol["editor_type"] == "decimal_input"
    assert vol["decimal_precision"] == 0
    assert "THOUSANDS" in vol["magnitude_options"]

    sector = next(f for f in filters if f["filter_id"] == "sector")
    assert sector["editor_type"] == "enum_multi_select"


def test_validate_detects_numeric_contradiction_bounds(client: TestClient):
    """Verify that validate_query detects lower bound strictly exceeding upper bound."""
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [
            {
                "condition_id": "cond-1",
                "filter_id": "last_price",
                "operator": "gt",
                "value": "200.0",
            },
            {
                "condition_id": "cond-2",
                "filter_id": "last_price",
                "operator": "lt",
                "value": "100.0",
            },
        ],
    }
    response = client.post("/screeners/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["contradictions_detected"] is True
    assert len(data["issues"]) >= 1
    issue = data["issues"][0]
    assert issue["code"] == "SCREENER_CONTRADICTORY_CONDITIONS"
    assert issue["severity"] == "error"
    assert "strictly exceeds upper bound" in issue["message"]


def test_validate_detects_strict_equality_contradiction(client: TestClient):
    """Verify that validate_query detects unsatisfiable strict inequality on same boundary."""
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [
            {
                "condition_id": "c-gt",
                "filter_id": "last_price",
                "operator": "gt",
                "value": "100.0",
            },
            {
                "condition_id": "c-lt",
                "filter_id": "last_price",
                "operator": "lt",
                "value": "100.0",
            },
        ],
    }
    response = client.post("/screeners/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["contradictions_detected"] is True


def test_validate_detects_single_valued_enum_contradiction(client: TestClient):
    """Verify that multiple EQ conditions for single-valued fields (e.g. sector) are flagged."""
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [
            {
                "condition_id": "c-sec-1",
                "filter_id": "sector",
                "operator": "eq",
                "value": "Technology",
            },
            {
                "condition_id": "c-sec-2",
                "filter_id": "sector",
                "operator": "eq",
                "value": "Healthcare",
            },
        ],
    }
    response = client.post("/screeners/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["contradictions_detected"] is True
    assert any(i["code"] == "SCREENER_CONTRADICTORY_CONDITIONS" for i in data["issues"])


def test_validate_accepts_valid_compatible_conditions(client: TestClient):
    """Verify that compatible non-contradictory conditions pass validation."""
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [
            {
                "condition_id": "c-1",
                "filter_id": "last_price",
                "operator": "gte",
                "value": "50.0",
            },
            {
                "condition_id": "c-2",
                "filter_id": "last_price",
                "operator": "lte",
                "value": "200.0",
            },
            {
                "condition_id": "c-3",
                "filter_id": "market_cap",
                "operator": "gte",
                "value": "10000000000",
            },
        ],
    }
    response = client.post("/screeners/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["contradictions_detected"] is False
    assert len(data["accepted_filters"]) == 3
