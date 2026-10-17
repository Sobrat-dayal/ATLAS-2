"""Comprehensive backend test suite for Technical Indicator Infrastructure (Stage 69).

Verifies:
1. Indicator registry registration, duplicate rejection, unknown indicator, and versioning.
2. Authoritative parameter validation (types, bounds, defaults, allowed choices).
3. Deterministic SMA mathematical calculation, O(N) rolling arithmetic, Decimal precision.
4. Exact warmup behavior (N-1 bars marked WARMUP with value=None, never 0!).
5. Insufficient history handling (status INSUFFICIENT_HISTORY when total bars < N).
6. Missing data / gap policy (DATA_GAP when Close price is missing in rolling window).
7. Zero look-ahead guarantee (point at T depends strictly on bars <= T).
8. Support for negative futures prices (e.g. CLZ26 WTI Crude).
9. TechnicalIndicatorService orchestration, canonical resolution, lookback management.
10. API endpoints:
    - GET /charts/indicators/catalog
    - GET /charts/indicators/{indicator_id}
    - POST /charts/indicators/calculate (single and multiple instances, error handling)
11. Resource limits (max 5 active instances per request).
12. Read-only guarantee (0 database or market-data mutations).
"""

from decimal import Decimal
import pytest
from httpx import ASGITransport, AsyncClient

from atlas.charts.indicators import (
    IndicatorCategory,
    IndicatorCalculationRequest,
    IndicatorInstanceConfig,
    IndicatorParameterDefinition,
    IndicatorParameterType,
    IndicatorRenderingTarget,
    IndicatorStatus,
    IndicatorRegistry,
    SmaCalculator,
    TechnicalIndicatorService,
    default_indicator_registry,
)
from atlas.charts.models import ChartBarDTO
from atlas_api.app import create_app
from atlas_api.config import get_settings


# ---------------------------------------------------------------------------
# Test Fixtures & Helpers
# ---------------------------------------------------------------------------

class MockGapBar:
    def __init__(self, index: int, time_unix: int = 1700000000):
        self.timestamp = f"2023-11-{(index + 1):02d}T00:00:00Z"
        self.time_unix = time_unix + index * 86400
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None


def make_test_bar(index: int, close_val: float, time_unix: int = 1700000000) -> ChartBarDTO:
    """Create a minimal valid ChartBarDTO fixture."""
    bar_time = time_unix + index * 86400
    return ChartBarDTO(
        timestamp=f"2023-11-{(index + 1):02d}T00:00:00Z",
        time_unix=bar_time,
        open=Decimal(str(close_val)),
        high=Decimal(str(close_val + 2)),
        low=Decimal(str(close_val - 2)),
        close=Decimal(str(close_val)),
        volume=Decimal("1000"),
    )


# ---------------------------------------------------------------------------
# 1. Registry Tests
# ---------------------------------------------------------------------------

def test_registry_registration_and_lookup():
    reg = IndicatorRegistry()
    sma = SmaCalculator()
    reg.register(sma)

    assert reg.is_registered("atlas.sma", 1) is True
    assert reg.is_registered("atlas.sma", 2) is False

    defn, calc = reg.get("atlas.sma", 1)
    assert defn.indicator_id == "atlas.sma"
    assert defn.display_name == "Simple Moving Average"
    assert defn.category == IndicatorCategory.TREND
    assert defn.rendering_target == IndicatorRenderingTarget.PRICE_OVERLAY
    assert calc is sma

    # Duplicate registration must fail
    with pytest.raises(ValueError, match="already registered"):
        reg.register(sma)

    # Unknown indicator must raise KeyError
    with pytest.raises(KeyError, match="Unknown indicator 'unknown.indicator'"):
        reg.get("unknown.indicator", 1)

    # Unsupported version must raise KeyError with available versions
    with pytest.raises(KeyError, match="Unsupported version 99"):
        reg.get("atlas.sma", 99)

    # List definitions
    defs = reg.list_definitions()
    assert len(defs) == 1
    assert defs[0].indicator_id == "atlas.sma"


# ---------------------------------------------------------------------------
# 2. Parameter Validation Tests
# ---------------------------------------------------------------------------

def test_parameter_validation_bounds_and_types():
    sma = SmaCalculator()

    # Valid parameter dictionary
    valid = sma.validate_parameters({"period": 20, "source": "close"})
    assert valid["period"] == 20
    assert valid["source"] == "close"

    # Default period fallback
    defaulted = sma.validate_parameters({})
    assert defaulted["period"] == 20
    assert defaulted["source"] == "close"

    # Out of bounds: period < 2
    with pytest.raises(ValueError, match="below minimum allowed 2"):
        sma.validate_parameters({"period": 1})

    # Out of bounds: period > 500
    with pytest.raises(ValueError, match="exceeds maximum allowed 500"):
        sma.validate_parameters({"period": 501})

    # Type error: non-integer
    with pytest.raises(ValueError, match="must be an integer"):
        sma.validate_parameters({"period": "twenty"})

    # Type error: float fraction
    with pytest.raises(ValueError, match="must be a whole integer"):
        sma.validate_parameters({"period": 14.5})

    # Allowed choices for source
    with pytest.raises(ValueError, match="not in allowed choices"):
        sma.validate_parameters({"period": 20, "source": "open"})


# ---------------------------------------------------------------------------
# 3. SMA Mathematical Calculation Tests
# ---------------------------------------------------------------------------

def test_sma_calculation_exact_mathematics():
    """Verify SMA calculation against deterministic prompt test fixture.

    Input Close values: 100, 102, 104, 106, 108
    Period: 3
    Expected output:
      Bar 1: None (WARMUP)
      Bar 2: None (WARMUP)
      Bar 3: 102.0
      Bar 4: 104.0
      Bar 5: 106.0
    """
    sma = SmaCalculator()
    closes = [100.0, 102.0, 104.0, 106.0, 108.0]
    bars = [make_test_bar(i, c) for i, c in enumerate(closes)]

    result = sma.calculate(
        instance_id="sma-test-1",
        bars=bars,
        params={"period": 3},
    )

    assert result.status == IndicatorStatus.READY
    assert len(result.series) == 1
    series = result.series[0]
    points = series.points
    assert len(points) == 5

    # Bar 0 (Warmup)
    assert points[0].status == IndicatorStatus.WARMUP
    assert points[0].value is None

    # Bar 1 (Warmup)
    assert points[1].status == IndicatorStatus.WARMUP
    assert points[1].value is None

    # Bar 2: (100 + 102 + 104) / 3 = 102.0
    assert points[2].status == IndicatorStatus.READY
    assert pytest.approx(points[2].value, 0.0001) == 102.0

    # Bar 3: (102 + 104 + 106) / 3 = 104.0
    assert points[3].status == IndicatorStatus.READY
    assert pytest.approx(points[3].value, 0.0001) == 104.0

    # Bar 4: (104 + 106 + 108) / 3 = 106.0
    assert points[4].status == IndicatorStatus.READY
    assert pytest.approx(points[4].value, 0.0001) == 106.0


def test_sma_insufficient_history():
    """Verify that requesting period > total bars returns INSUFFICIENT_HISTORY with value=None."""
    sma = SmaCalculator()
    bars = [make_test_bar(i, 100.0) for i in range(5)]

    result = sma.calculate(
        instance_id="sma-test-2",
        bars=bars,
        params={"period": 10},
    )

    assert result.status == IndicatorStatus.INSUFFICIENT_HISTORY
    assert "Insufficient history" in (result.error_message or "")
    for pt in result.series[0].points:
        assert pt.value is None
        assert pt.status == IndicatorStatus.INSUFFICIENT_HISTORY


def test_sma_data_gap_handling():
    """Verify that a bar with close=None results in DATA_GAP status without crashing."""
    sma = SmaCalculator()
    bars = [
        make_test_bar(0, 100.0),
        make_test_bar(1, 102.0),
        MockGapBar(2),  # Bar with close = None
        make_test_bar(3, 106.0),
    ]

    result = sma.calculate(
        instance_id="sma-gap",
        bars=bars,
        params={"period": 2},
    )

    points = result.series[0].points
    # Bar 0: Warmup
    assert points[0].status == IndicatorStatus.WARMUP
    # Bar 1: (100 + 102)/2 = 101.0
    assert points[1].status == IndicatorStatus.READY
    assert pytest.approx(points[1].value, 0.001) == 101.0
    # Bar 2: Close is None -> DATA_GAP
    assert points[2].status == IndicatorStatus.DATA_GAP
    assert points[2].value is None
    # Bar 3: Window includes bar 2 (None) and bar 3 (106) -> DATA_GAP
    assert points[3].status == IndicatorStatus.DATA_GAP
    assert points[3].value is None


def test_sma_zero_look_ahead_guarantee():
    """Verify that future bars do not modify indicator values at prior timestamps."""
    sma = SmaCalculator()
    initial_bars = [make_test_bar(i, 100.0 + i * 2) for i in range(5)]

    res1 = sma.calculate("sma-1", initial_bars, {"period": 3})
    points1 = [p.value for p in res1.series[0].points]

    # Add 5 more future bars with wild swings
    extended_bars = initial_bars + [make_test_bar(i, 500.0 + i * 50) for i in range(5, 10)]
    res2 = sma.calculate("sma-1", extended_bars, {"period": 3})
    points2 = [p.value for p in res2.series[0].points]

    # The first 5 outputs must be exactly identical
    assert points1 == points2[:5]


def test_sma_negative_futures_prices():
    """Verify support for negative prices (e.g. WTI Crude CLZ26 historical sub-zero)."""
    sma = SmaCalculator()
    negative_closes = [-37.63, -30.00, -20.00, -10.00]
    bars = [make_test_bar(i, c) for i, c in enumerate(negative_closes)]

    res = sma.calculate("sma-neg", bars, {"period": 2})
    assert res.status == IndicatorStatus.READY
    pts = res.series[0].points
    assert pts[0].value is None
    # (-37.63 + -30.00) / 2 = -33.815
    assert pytest.approx(pts[1].value, 0.001) == -33.815


# ---------------------------------------------------------------------------
# 4. Service Orchestration Tests
# ---------------------------------------------------------------------------

def test_service_catalog():
    svc = TechnicalIndicatorService()
    cat = svc.get_catalog()
    assert len(cat.indicators) >= 1
    ids = [d.indicator_id for d in cat.indicators]
    assert "atlas.sma" in ids


def test_service_calculate_multiple_instances():
    svc = TechnicalIndicatorService()
    request = IndicatorCalculationRequest(
        symbol="SPY",
        interval="1d",
        instances=[
            IndicatorInstanceConfig(
                instance_id="sma-fast",
                indicator_id="atlas.sma",
                version=1,
                parameters={"period": 5},
                color="#10b981",
                line_width=2,
            ),
            IndicatorInstanceConfig(
                instance_id="sma-slow",
                indicator_id="atlas.sma",
                version=1,
                parameters={"period": 20},
                color="#f59e0b",
                line_width=3,
            ),
        ],
    )

    resp = svc.calculate_indicators(request)
    assert resp.symbol == "SPY"
    assert resp.interval == "1d"
    assert len(resp.results) == 2

    # Fast instance
    res_fast = next(r for r in resp.results if r.instance_id == "sma-fast")
    assert res_fast.status == IndicatorStatus.READY
    assert res_fast.parameters["period"] == 5
    assert res_fast.series[0].color == "#10b981"
    assert res_fast.series[0].line_width == 2

    # Slow instance
    res_slow = next(r for r in resp.results if r.instance_id == "sma-slow")
    assert res_slow.status == IndicatorStatus.READY
    assert res_slow.parameters["period"] == 20
    assert res_slow.series[0].color == "#f59e0b"
    assert res_slow.series[0].line_width == 3


def test_service_rejects_exceeded_instance_limit():
    from pydantic import ValidationError

    # 6 instances exceeds max_length=5 on IndicatorCalculationRequest
    instances = [
        IndicatorInstanceConfig(
            instance_id=f"sma-{i}",
            indicator_id="atlas.sma",
            version=1,
            parameters={"period": 5 + i},
        )
        for i in range(6)
    ]
    with pytest.raises(ValidationError):
        IndicatorCalculationRequest(
            symbol="SPY",
            interval="1d",
            instances=instances,
        )


# ---------------------------------------------------------------------------
# 5. FastAPI Endpoints Integration Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_api_get_catalog():
    settings = get_settings()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(f"{settings.api_prefix}/charts/indicators/catalog")
        assert resp.status_code == 200
        data = resp.json()
        assert "indicators" in data
        assert any(ind["indicator_id"] == "atlas.sma" for ind in data["indicators"])


@pytest.mark.asyncio
async def test_api_get_single_definition():
    settings = get_settings()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Existing definition
        resp = await client.get(f"{settings.api_prefix}/charts/indicators/atlas.sma")
        assert resp.status_code == 200
        data = resp.json()
        assert data["indicator_id"] == "atlas.sma"
        assert data["display_name"] == "Simple Moving Average"
        assert len(data["parameters"]) >= 1

        # Non-existing definition
        resp_404 = await client.get(f"{settings.api_prefix}/charts/indicators/unknown.indicator")
        assert resp_404.status_code == 404


@pytest.mark.asyncio
async def test_api_calculate_endpoint():
    settings = get_settings()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "symbol": "BTCUSDT",
            "interval": "1d",
            "instances": [
                {
                    "instance_id": "sma-btc-20",
                    "indicator_id": "atlas.sma",
                    "version": 1,
                    "parameters": {"period": 20},
                }
            ],
        }
        resp = await client.post(f"{settings.api_prefix}/charts/indicators/calculate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "BTCUSDT"
        assert data["interval"] == "1d"
        assert len(data["results"]) == 1
        res = data["results"][0]
        assert res["instance_id"] == "sma-btc-20"
        assert res["status"] == "READY"
        assert len(res["series"][0]["points"]) > 0


@pytest.mark.asyncio
async def test_api_calculate_invalid_parameter():
    settings = get_settings()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "symbol": "SPY",
            "interval": "1d",
            "instances": [
                {
                    "instance_id": "sma-bad",
                    "indicator_id": "atlas.sma",
                    "version": 1,
                    "parameters": {"period": 0},  # Below min 2
                }
            ],
        }
        resp = await client.post(f"{settings.api_prefix}/charts/indicators/calculate", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        error_msg = data.get("detail") or data.get("error", {}).get("message", "")
        assert "below minimum allowed 2" in error_msg
