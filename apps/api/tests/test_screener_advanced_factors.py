"""
Institutional Unit and Integration Tests for Stage 96:
Advanced Fundamental, Technical, and Multi-Factor Screening Engine.
"""

from decimal import Decimal

import pytest
from atlas.screeners.enums import (
    FilterOperator,
)
from atlas.screeners.schemas import (
    FilterCriterionDTO,
    ScreenerRunRequestDTO,
)
from atlas.screeners.service import ScreenerService
from atlas.screeners.technical import (
    compute_52w_high_low,
    compute_atr,
    compute_bollinger_bands,
    compute_ema,
    compute_historical_volatility,
    compute_macd,
    compute_momentum,
    compute_relative_volume,
    compute_rsi,
    compute_sma,
    validate_ohlcv_bar,
)
from fastapi.testclient import TestClient

from atlas_api.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return ScreenerService()


# =============================================================================
# 1. TECHNICAL INDICATOR PURE MATHEMATICAL TESTS
# =============================================================================

def test_sma_calculation():
    """Verify SMA calculation against deterministic sequence and lookback checks."""
    closes = [Decimal(x) for x in [10, 11, 12, 13, 14]]
    
    # 5-period SMA: (10+11+12+13+14)/5 = 12.0
    sma5 = compute_sma(closes, period=5)
    assert sma5 == Decimal("12")

    # 3-period SMA: (12+13+14)/3 = 13.0
    sma3 = compute_sma(closes, period=3)
    assert sma3 == Decimal("13")

    # Insufficient history returns None (no synthetic filling)
    sma10 = compute_sma(closes, period=10)
    assert sma10 is None


def test_ema_calculation():
    """Verify EMA initialization via seed SMA and recursive weighting."""
    # Constant price series produces identical EMA
    constant_closes = [Decimal("50")] * 30
    ema_const = compute_ema(constant_closes, period=10)
    assert ema_const == Decimal("50")

    # Trending series test
    trending = [Decimal(x) for x in range(1, 51)]
    ema20 = compute_ema(trending, period=20)
    assert ema20 is not None
    assert ema20 > Decimal("25")

    # Insufficient history
    assert compute_ema([Decimal("10")], period=5) is None


def test_rsi_calculation():
    """Verify RSI Wilder smoothing and extreme boundary conditions."""
    # Constant series -> Price change 0 -> RSI 50
    constant_closes = [Decimal("100")] * 25
    assert compute_rsi(constant_closes, period=14) == Decimal("50")

    # Strictly monotonic gains -> Losses = 0 -> RSI 100
    all_gains = [Decimal(x) for x in range(10, 35)]
    assert compute_rsi(all_gains, period=14) == Decimal("100")

    # Strictly monotonic losses -> Gains = 0 -> RSI 0
    all_losses = [Decimal(x) for x in range(35, 10, -1)]
    assert compute_rsi(all_losses, period=14) == Decimal("0")

    # Insufficient history
    assert compute_rsi([Decimal("10")] * 10, period=14) is None


def test_macd_calculation():
    """Verify MACD fast/slow EMA divergence and signal line calculation."""
    # 50 bars of upward trending data
    prices = [Decimal(str(100 + i * 1.5)) for i in range(50)]
    res = compute_macd(prices, fast_period=12, slow_period=26, signal_period=9)
    assert res is not None
    assert "macd" in res
    assert "signal" in res
    assert "histogram" in res

    # Histogram must equal MACD - Signal exactly
    assert res["histogram"] == res["macd"] - res["signal"]
    # Upward trending series has positive MACD
    assert res["macd"] > Decimal("0")

    # Insufficient bars (less than 35)
    short_prices = [Decimal("100")] * 25
    assert compute_macd(short_prices) is None


def test_bollinger_bands():
    """Verify Bollinger Bands middle SMA, upper/lower dispersion, and %B."""
    prices = [Decimal(str(100 + (i % 5))) for i in range(30)]
    bb = compute_bollinger_bands(prices, period=20, multiplier=Decimal("2"))
    assert bb is not None
    assert bb["middle"] == compute_sma(prices, period=20)
    assert bb["upper"] > bb["middle"]
    assert bb["lower"] < bb["middle"]
    assert bb["bandwidth"] > Decimal("0")
    # %B = (Close - Lower) / (Upper - Lower)
    assert Decimal("0") <= bb["percent_b"] <= Decimal("1")


def test_atr_and_bars():
    """Verify True Range computation, Wilder smoothing, and bar invariants."""
    # Test valid bar invariant
    valid_bar = {
        "open": Decimal("100"),
        "high": Decimal("105"),
        "low": Decimal("98"),
        "close": Decimal("103"),
        "volume": Decimal("1000000"),
    }
    assert validate_ohlcv_bar(valid_bar) is True

    # Test invalid bar (high < low)
    invalid_bar = {
        "open": Decimal("100"),
        "high": Decimal("95"),
        "low": Decimal("98"),
        "close": Decimal("96"),
        "volume": Decimal("1000"),
    }
    assert validate_ohlcv_bar(invalid_bar) is False

    # Generate 25 valid bars with synthetic volatility
    highs = []
    lows = []
    closes = []
    base = Decimal("100")
    for i in range(25):
        highs.append(base + Decimal("2"))
        lows.append(base - Decimal("2"))
        closes.append(base + Decimal("1"))
        base += Decimal("1")

    atr_res = compute_atr(highs, lows, closes, period=14)
    assert atr_res is not None
    assert "atr" in atr_res
    assert "atr_pct" in atr_res
    assert atr_res["atr"] > Decimal("0")
    assert atr_res["atr_pct"] > Decimal("0")


def test_momentum_and_volatility():
    """Verify rate-of-change momentum and sample annualized volatility."""
    prices = [Decimal(str(100 + i)) for i in range(30)]
    # Momentum 20-period: (Close_t - Close_{t-20}) / Close_{t-20} * 100
    mom = compute_momentum(prices, period=20)
    assert mom is not None
    # 29th bar is 129, 9th bar is 109 -> (129 - 109) / 109 * 100 = 18.3486%
    expected = ((Decimal("129") - Decimal("109")) / Decimal("109")) * Decimal("100")
    assert abs(mom - expected) < Decimal("0.01")

    # Volatility
    vol = compute_historical_volatility(prices, lookback=20, annualization_sessions=252)
    assert vol is not None
    assert vol > Decimal("0")


def test_relative_volume_and_52w():
    """Verify relative volume and rolling 52-week distance metrics."""
    rvol = compute_relative_volume(Decimal("2000000"), Decimal("1000000"))
    assert rvol == Decimal("2.00")

    # 52w range
    prices = [Decimal(str(100 + i)) for i in range(260)]
    hilo = compute_52w_high_low(prices)
    assert hilo is not None
    assert hilo["high_52w"] == Decimal("359")
    assert hilo["pct_from_high"] == Decimal("0.00")


# =============================================================================
# 2. FUNDAMENTAL SECTOR ELIGIBILITY & PERIOD INTEGRITY
# =============================================================================

def test_financial_sector_eligibility(service):
    """Verify that banking institutions (JPM) have ineligibility for industrial-only metrics."""
    repo = service._repo
    records = {r.ticker: r for r in repo.get_records()}
    jpm = records.get("JPM")
    assert jpm is not None
    assert jpm.sector == "Financial Services"

    # Banking records must have None for industrial FCF, Net Debt, Gross Margin, and EV/EBITDA
    assert jpm.fcf is None
    assert jpm.net_debt is None
    assert jpm.ev_to_ebitda is None

    # Filtering by positive FCF must exclude JPM without error
    req = ScreenerRunRequestDTO(
        universe_id="all_us_equities",
        filters=[
            FilterCriterionDTO(filter_id="fcf", operator=FilterOperator.GT, value="0"),
        ],
        limit=50,
    )
    res = service.run_screen(req)
    tickers = [row.ticker for row in res.rows]
    assert "JPM" not in tickers
    assert "AAPL" in tickers  # AAPL has robust positive FCF ($108.7B)


def test_growth_metrics_integrity(service):
    """Verify revenue growth, net income growth, and EPS growth filtering."""
    # Filter for companies with YoY revenue growth > 10%
    req = ScreenerRunRequestDTO(
        universe_id="all_us_equities",
        filters=[
            FilterCriterionDTO(filter_id="revenue_growth_yoy", operator=FilterOperator.GT, value="10"),
        ],
        limit=50,
    )
    res = service.run_screen(req)
    assert res.total_matching_count > 0
    # NVDA (122.4%), MSFT (15.7%) should pass
    tickers = [row.ticker for row in res.rows]
    assert "NVDA" in tickers
    assert "MSFT" in tickers


# =============================================================================
# 3. MULTI-FACTOR SCREENING COMBINATIONS (FUNDAMENTAL + TECHNICAL)
# =============================================================================

def test_multi_factor_growth_plus_trend(service):
    """
    Verify multi-factor query:
    1. Revenue Growth YoY > 10% (Fundamental Growth)
    2. Price > 200 SMA == True (Technical Trend)
    3. RSI 14 < 70 (Technical Momentum / Overbought filter)
    """
    req = ScreenerRunRequestDTO(
        universe_id="all_us_equities",
        filters=[
            FilterCriterionDTO(filter_id="revenue_growth_yoy", operator=FilterOperator.GT, value="10"),
            FilterCriterionDTO(filter_id="price_above_sma200", operator=FilterOperator.EQ, value=True),
            FilterCriterionDTO(filter_id="rsi_14", operator=FilterOperator.LT, value="70"),
        ],
        limit=50,
    )
    res = service.run_screen(req)
    assert res.total_matching_count > 0
    for row in res.rows:
        # Every matched row must satisfy all three criteria
        rec = service._repo.get_records()
        matching_rec = next(r for r in rec if r.ticker == row.ticker)
        assert matching_rec.revenue_growth_yoy > Decimal("10")
        assert matching_rec.price_above_sma200 is True
        assert matching_rec.rsi_14 < Decimal("70")


def test_insufficient_lookback_exclusion(service):
    """Verify delisted security (ENE) without required history is strictly excluded from 200-SMA screens."""
    records = {r.ticker: r for r in service._repo.get_records()}
    ene = records.get("ENE")
    assert ene is not None
    assert ene.sma_200 is None

    req = ScreenerRunRequestDTO(
        universe_id="all_us_equities",
        filters=[
            FilterCriterionDTO(filter_id="sma_200", operator=FilterOperator.GT, value="0"),
        ],
        limit=50,
    )
    res = service.run_screen(req)
    tickers = [row.ticker for row in res.rows]
    assert "ENE" not in tickers


def test_parameter_bounds_validation(service):
    """Verify that technical parameters out of allowed bounds [2, 500] are rejected."""
    req = ScreenerRunRequestDTO(
        universe_id="all_us_equities",
        filters=[
            FilterCriterionDTO(
                filter_id="sma_50",
                operator=FilterOperator.GT,
                value="100",
                parameters={"period": 999},
            ),
        ],
        limit=50,
    )
    val = service.validate_query(req)
    assert val.valid is False
    assert any(iss.code == "SCREENER_PARAMETER_INVALID" for iss in val.issues)


# =============================================================================
# 4. FASTAPI FACTOR DISCOVERY & INSPECTION ENDPOINTS
# =============================================================================

def test_api_list_factors(client):
    """Test GET /api/v1/screeners/factors returns complete factor registry."""
    res = client.get("/api/v1/screeners/factors")
    assert res.status_code == 200
    factors = res.json()
    assert len(factors) >= 70
    filter_ids = [f["filter_id"] for f in factors]
    assert "revenue_growth_yoy" in filter_ids
    assert "fcf" in filter_ids
    assert "sma_200" in filter_ids
    assert "rsi_14" in filter_ids
    assert "macd_hist" in filter_ids


def test_api_list_factors_by_category(client):
    """Test GET /api/v1/screeners/factors?category=technical_trend."""
    res = client.get("/api/v1/screeners/factors?category=technical_trend")
    assert res.status_code == 200
    factors = res.json()
    assert len(factors) > 0
    assert all(f["category"] == "technical_trend" for f in factors)


def test_api_get_factor_inspection(client):
    """Test GET /api/v1/screeners/factors/{factor_id} returns methodology and specs."""
    res = client.get("/api/v1/screeners/factors/rsi_14")
    assert res.status_code == 200
    data = res.json()
    assert data["filter_id"] == "rsi_14"
    assert data["indicator_type"] == "rsi"
    assert data["minimum_lookback"] == 15
    assert "Wilder" in data["description"]

    # Not found case
    not_found = client.get("/api/v1/screeners/factors/nonexistent_factor")
    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "NOT_FOUND"


def test_api_get_factor_parameters(client):
    """Test GET /api/v1/screeners/factors/{factor_id}/parameters."""
    res = client.get("/api/v1/screeners/factors/sma_50/parameters")
    assert res.status_code == 200
    data = res.json()
    assert data["factor_id"] == "sma_50"
    assert data["indicator_type"] == "sma"
    assert "period" in data["allowed_parameters"]
    assert data["calculation_version"] == "1.0.0"


def test_api_post_factors_validate(client):
    """Test POST /api/v1/screeners/factors/validate."""
    payload = {
        "universe_id": "all_us_equities",
        "filters": [
            {
                "filter_id": "revenue_growth_yoy",
                "operator": "gt",
                "value": "15",
            },
            {
                "filter_id": "price_above_sma200",
                "operator": "eq",
                "value": True,
            },
        ],
    }
    res = client.post("/api/v1/screeners/factors/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert len(data["accepted_filters"]) == 2


def test_api_run_multi_factor_screener(client):
    """Test POST /api/v1/screeners/run with multi-factor institutional query."""
    payload = {
        "universe_id": "all_us_equities",
        "filters": [
            {"filter_id": "market_cap", "operator": "gte", "value": "100000000000"},  # Mega cap
            {"filter_id": "operating_margin", "operator": "gte", "value": "20"},      # Quality margin
            {"filter_id": "price_above_sma50", "operator": "eq", "value": True},      # Trend
        ],
        "sort": [{"field_id": "market_cap", "direction": "desc"}],
        "limit": 10,
    }
    res = client.post("/api/v1/screeners/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_matching_count"] > 0
    assert len(data["rows"]) <= 10
    top_tickers = [row["ticker"] for row in data["rows"]]
    assert any(t in top_tickers for t in ["MSFT", "AAPL", "NVDA", "GOOGL"])
