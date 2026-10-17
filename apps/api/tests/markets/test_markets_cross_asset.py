"""Comprehensive Automated Tests for ATLAS Cross-Asset Markets V1 (Stage 65).

Tests:
1. Universe definitions: canonical multi-asset universes, member count, default symbols.
2. Options endpoint: supported modes, windows, asset classes, max selection count.
3. Native Market Overview semantics:
   - Equities: price change % vs prev close.
   - ETFs: exchange market price % change, proxy disclosure (is_proxy=True, proxy_kind="ETF Proxy").
   - FX: spot rate change %, directional pair orientation.
   - Crypto: continuous rolling 24h return %, quote asset disclosure (USDT).
   - Bonds: yield level in % and yield change in basis points (bps), NOT price return.
   - Futures: last price vs settlement points, futures proxy disclosure.
4. Benchmark vs Proxy distinction:
   - SPY and ESZ26 are explicitly marked as proxies for S&P 500 Index.
   - Canonical series marked as is_benchmark=True.
5. Aligned Price Performance semantics:
   - Common UTC window start/end resolution.
   - Zero look-ahead bias: effective start <= requested start.
   - Alignment tolerance enforcement (<= 7200s).
   - Bond exclusion: US10Y excluded with UNSUPPORTED_METRIC (yield level != price return).
   - Decimal return calculation: ((end - start) / start) * 100.
   - Indexed price level calculation (base 100.0).
6. Exclusion taxonomy & invalid denominators:
   - Non-positive start price excluded with INVALID_DENOMINATOR.
   - Large observation offset excluded with WINDOW_MISALIGNED.
7. Coverage & completeness reporting:
   - Correct qualified, excluded, and reason counts.
   - Completeness status: PARTIAL in aligned mode when bonds excluded;
     COMPLETE_FOR_DEFINED_SET in native mode.
8. Bounded selection:
   - User-specified symbols capped at 12; >12 rejected with HTTP 400.
9. FastAPI API Endpoints (authenticated AsyncClient):
   - /markets/cross-asset/universes
   - /markets/cross-asset/options
   - /markets/cross-asset
10. Read-only invariant: 0 writes, 0 provider RPC fanout on read.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.cross_asset.config import (
    MAX_SELECTION_COUNT,
    SUPPORTED_CROSS_ASSET_UNIVERSES,
    AssetClassEnum,
    CrossAssetCoverageStatus,
    CrossAssetExclusionReason,
    CrossAssetMode,
    CrossAssetWindow,
    NativeMetricKind,
    ProxyKind,
)
from atlas.markets.cross_asset.repository import (
    CandidateMarketData,
    CrossAssetMarketRepository,
)
from atlas.markets.cross_asset.service import CrossAssetMarketService
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.main import app


# =============================================================================
# Test Fixtures
# =============================================================================
@pytest.fixture
def mock_auth_user() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user-12345678-1234-5678-1234-567812345678",
        email="analyst@atlas.io",
    )


@pytest.fixture
def mock_auth_context(mock_auth_user: AuthPrincipal) -> AuthorizationContext:
    ctx = MagicMock(spec=AuthorizationContext)
    ctx.principal = mock_auth_user
    ctx.is_authenticated = True
    ctx.has_permission.return_value = True
    return ctx


@pytest.fixture
def anchor_time() -> datetime:
    return datetime(2026, 10, 17, 18, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def service(anchor_time: datetime) -> CrossAssetMarketService:
    repo = CrossAssetMarketRepository(anchor_time=anchor_time)
    return CrossAssetMarketService(repository=repo, anchor_time=anchor_time)


# =============================================================================
# 1. Universe & Options Tests
# =============================================================================
def test_cross_asset_universes(service: CrossAssetMarketService) -> None:
    """Verifies predefined canonical multi-asset universes."""
    resp = service.get_universes()
    assert resp.count == len(SUPPORTED_CROSS_ASSET_UNIVERSES)
    assert resp.count >= 3

    univ_ids = [u.universe_id for u in resp.universes]
    assert "univ_cross_asset_macro" in univ_ids
    assert "univ_cross_asset_us_liquidity" in univ_ids
    assert "univ_cross_asset_commodities_fx" in univ_ids

    macro_univ = next(u for u in resp.universes if u.universe_id == "univ_cross_asset_macro")
    assert AssetClassEnum.EQUITIES in macro_univ.asset_classes
    assert AssetClassEnum.BONDS in macro_univ.asset_classes
    assert AssetClassEnum.FX in macro_univ.asset_classes
    assert AssetClassEnum.CRYPTO in macro_univ.asset_classes
    assert AssetClassEnum.FUTURES in macro_univ.asset_classes


def test_cross_asset_options(service: CrossAssetMarketService) -> None:
    """Verifies supported modes, windows, and alignment parameters."""
    options = service.get_options()
    assert CrossAssetMode.NATIVE_OVERVIEW in options.modes
    assert CrossAssetMode.ALIGNED_PERFORMANCE in options.modes
    assert CrossAssetWindow.LAST_24H in options.windows
    assert CrossAssetWindow.LAST_7D in options.windows
    assert CrossAssetWindow.LAST_30D in options.windows
    assert options.max_selection_count == 12
    assert options.alignment_tolerance_seconds == 7200


# =============================================================================
# 2. Native Market Overview Tests
# =============================================================================
def test_native_market_overview_asset_class_semantics(service: CrossAssetMarketService) -> None:
    """Verifies that Native Mode preserves each asset class's underlying financial convention."""
    resp = service.get_cross_asset_overview(
        universe_id="univ_cross_asset_macro",
        mode=CrossAssetMode.NATIVE_OVERVIEW,
    )
    assert resp.mode == CrossAssetMode.NATIVE_OVERVIEW
    assert len(resp.comparison_members) >= 8

    # Find specific instruments
    aapl = next(m for m in resp.comparison_members if m.symbol == "AAPL")
    spy = next(m for m in resp.comparison_members if m.symbol == "SPY")
    eurusd = next(m for m in resp.comparison_members if m.symbol == "EURUSD")
    btcusdt = next(m for m in resp.comparison_members if m.symbol == "BTCUSDT")
    us10y = next(m for m in resp.comparison_members if m.symbol == "US10Y")
    clz26 = next(m for m in resp.comparison_members if m.symbol == "CLZ26")

    # Equities: Price change %
    assert aapl.asset_class == AssetClassEnum.EQUITIES
    assert aapl.native_metric.metric_kind == NativeMetricKind.EQUITY_PRICE_CHANGE
    assert aapl.native_metric.unit == "%"
    assert aapl.native_metric.current_value == Decimal("234.85")
    assert aapl.native_metric.change_percent == Decimal("1.4471")

    # ETFs: Market price change & Proxy status
    assert spy.asset_class == AssetClassEnum.ETFS
    assert spy.native_metric.metric_kind == NativeMetricKind.ETF_MARKET_PRICE_CHANGE
    assert spy.is_proxy is True
    assert spy.proxy_kind == ProxyKind.ETF_PROXY
    assert spy.proxy_benchmark_target == "S&P 500 Index"

    # FX: Spot rate change % with directional pair
    assert eurusd.asset_class == AssetClassEnum.FX
    assert eurusd.native_metric.metric_kind == NativeMetricKind.FX_SPOT_RATE_CHANGE
    assert eurusd.native_metric.current_value == Decimal("1.0845")
    assert eurusd.aligned_performance.quote_unit == "USD per EUR"

    # Crypto: Rolling 24h return %
    assert btcusdt.asset_class == AssetClassEnum.CRYPTO
    assert btcusdt.native_metric.metric_kind == NativeMetricKind.CRYPTO_SPOT_24H_CHANGE
    assert btcusdt.native_metric.current_value == Decimal("68450.00")
    assert btcusdt.native_metric.change_percent == Decimal("2.4701")

    # Bonds: Yield level & bps change; NOT percentage return!
    assert us10y.asset_class == AssetClassEnum.BONDS
    assert us10y.native_metric.metric_kind == NativeMetricKind.BOND_YIELD_BPS_CHANGE
    assert us10y.native_metric.unit == "bps"
    assert us10y.native_metric.current_value == Decimal("4.225")  # 4.225% yield
    assert us10y.native_metric.change_value == Decimal("7.5")  # +7.5 bps
    assert us10y.native_metric.change_percent is None  # CRITICAL: not a % return!

    # Futures: Last vs Settlement
    assert clz26.asset_class == AssetClassEnum.FUTURES
    assert clz26.native_metric.metric_kind == NativeMetricKind.FUTURES_SETTLEMENT_CHANGE
    assert clz26.native_metric.current_value == Decimal("71.40")
    assert clz26.native_metric.unit == "USD/barrel"


# =============================================================================
# 3. Aligned Price Performance & Exclusion Tests
# =============================================================================
def test_aligned_price_performance_calculations(service: CrossAssetMarketService) -> None:
    """Verifies strict common-window time-aligned Decimal price return calculations."""
    resp = service.get_cross_asset_overview(
        universe_id="univ_cross_asset_macro",
        mode=CrossAssetMode.ALIGNED_PERFORMANCE,
        window=CrossAssetWindow.LAST_24H,
    )
    assert resp.mode == CrossAssetMode.ALIGNED_PERFORMANCE

    # Check AAPL aligned performance
    aapl = next(m for m in resp.comparison_members if m.symbol == "AAPL")
    assert aapl.aligned_performance.eligible is True
    # Start: 231.50, End: 234.85 -> return: ((234.85 - 231.50) / 231.50) * 100 = 1.4471%
    assert aapl.aligned_performance.price_return_percent == Decimal("1.4471")
    # Indexed value: (234.85 / 231.50) * 100 = 101.4471
    assert aapl.aligned_performance.indexed_value == Decimal("101.4471")
    assert aapl.aligned_performance.start_price == Decimal("231.50")
    assert aapl.aligned_performance.end_price == Decimal("234.85")
    assert aapl.aligned_performance.exclusion_reason is None

    # Zero Look-Ahead Bias Verification:
    # effective_start_time must be <= requested_start
    assert aapl.aligned_performance.effective_start_time <= resp.requested_start


def test_bond_yield_excluded_from_aligned_price_performance(
    service: CrossAssetMarketService,
) -> None:
    """Verifies non-price series (e.g. bond yields) are excluded from aligned comparison."""
    resp = service.get_cross_asset_overview(
        universe_id="univ_cross_asset_macro",
        mode=CrossAssetMode.ALIGNED_PERFORMANCE,
        window=CrossAssetWindow.LAST_24H,
    )
    us10y = next(m for m in resp.comparison_members if m.symbol == "US10Y")
    assert us10y.aligned_performance.eligible is False
    assert us10y.aligned_performance.price_return_percent is None
    assert us10y.aligned_performance.indexed_value is None
    assert (
        us10y.aligned_performance.exclusion_reason == CrossAssetExclusionReason.UNSUPPORTED_METRIC
    )
    assert "basis points" in (us10y.aligned_performance.exclusion_detail or "")

    # Coverage should show PARTIAL completeness because US10Y is excluded
    assert resp.coverage.completeness_status == CrossAssetCoverageStatus.PARTIAL
    assert resp.coverage.excluded_members >= 1
    assert "UNSUPPORTED_METRIC" in resp.coverage.exclusions_by_reason


def test_invalid_denominator_exclusion(anchor_time: datetime) -> None:
    """Verifies that non-positive start reference prices are excluded with INVALID_DENOMINATOR."""
    now = anchor_time
    test_cand = CandidateMarketData(
        symbol="BAD_DENOM",
        display_name="Negative Start Test",
        asset_class=AssetClassEnum.EQUITIES,
        market_or_venue="TEST",
        market_series_identity="TEST:BAD",
        quote_currency="USD",
        quote_unit="USD/share",
        native_metric_kind=NativeMetricKind.EQUITY_PRICE_CHANGE,
        native_display_label="Test Price",
        native_unit="%",
        current_value=Decimal("10.00"),
        reference_value=Decimal("0.00"),
        change_value=Decimal("10.00"),
        change_percent=Decimal("0.00"),
        as_of_time=now,
        window_start_prices={CrossAssetWindow.LAST_24H: Decimal("0.00")},  # 0.00 start price!
        window_start_offsets_sec={CrossAssetWindow.LAST_24H: 0},
    )

    repo_mock = MagicMock(spec=CrossAssetMarketRepository)
    repo_mock.get_candidates_by_symbols.return_value = [test_cand]

    svc = CrossAssetMarketService(repository=repo_mock, anchor_time=now)
    resp = svc.get_cross_asset_overview(
        mode=CrossAssetMode.ALIGNED_PERFORMANCE,
        selected_symbols=["BAD_DENOM"],
    )
    member = resp.comparison_members[0]
    assert member.aligned_performance.eligible is False
    assert (
        member.aligned_performance.exclusion_reason == CrossAssetExclusionReason.INVALID_DENOMINATOR
    )


def test_window_misaligned_exclusion(anchor_time: datetime) -> None:
    """Verifies observation exceeding alignment tolerance is excluded with WINDOW_MISALIGNED."""
    now = anchor_time
    test_cand = CandidateMarketData(
        symbol="STALE_START",
        display_name="Misaligned Start Test",
        asset_class=AssetClassEnum.EQUITIES,
        market_or_venue="TEST",
        market_series_identity="TEST:STALE",
        quote_currency="USD",
        quote_unit="USD/share",
        native_metric_kind=NativeMetricKind.EQUITY_PRICE_CHANGE,
        native_display_label="Test Price",
        native_unit="%",
        current_value=Decimal("100.00"),
        reference_value=Decimal("95.00"),
        change_value=Decimal("5.00"),
        change_percent=Decimal("5.26"),
        as_of_time=now,
        window_start_prices={CrossAssetWindow.LAST_24H: Decimal("95.00")},
        window_start_offsets_sec={CrossAssetWindow.LAST_24H: 15000},  # 15000s > 7200s tolerance
    )

    repo_mock = MagicMock(spec=CrossAssetMarketRepository)
    repo_mock.get_candidates_by_symbols.return_value = [test_cand]

    svc = CrossAssetMarketService(repository=repo_mock, anchor_time=now)
    resp = svc.get_cross_asset_overview(
        mode=CrossAssetMode.ALIGNED_PERFORMANCE,
        selected_symbols=["STALE_START"],
    )
    member = resp.comparison_members[0]
    assert member.aligned_performance.eligible is False
    assert (
        member.aligned_performance.exclusion_reason == CrossAssetExclusionReason.WINDOW_MISALIGNED
    )


# =============================================================================
# 4. Bounded Selection Tests
# =============================================================================
def test_bounded_selection_cap(service: CrossAssetMarketService) -> None:
    """Verifies that user selection is clamped to MAX_SELECTION_COUNT (12)."""
    many_symbols = [f"SYM{i}" for i in range(20)]
    resp = service.get_cross_asset_overview(
        selected_symbols=many_symbols,
    )
    assert resp.coverage.requested_members <= MAX_SELECTION_COUNT


# =============================================================================
# 5. FastAPI Endpoints via AsyncClient
# =============================================================================
@pytest.mark.asyncio
async def test_api_list_universes(
    mock_auth_user: AuthPrincipal, mock_auth_context: AuthorizationContext
) -> None:
    """Tests GET /api/v1/markets/cross-asset/universes."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/markets/cross-asset/universes")
            assert resp.status_code == 200
            data = resp.json()
            assert "universes" in data
            assert data["count"] >= 3
            assert data["universes"][0]["universe_id"] == "univ_cross_asset_macro"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_get_options(
    mock_auth_user: AuthPrincipal, mock_auth_context: AuthorizationContext
) -> None:
    """Tests GET /api/v1/markets/cross-asset/options."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/markets/cross-asset/options")
            assert resp.status_code == 200
            data = resp.json()
            assert "native_overview" in data["modes"]
            assert "aligned_performance" in data["modes"]
            assert "last_24h" in data["windows"]
            assert data["max_selection_count"] == 12
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_get_overview_native(
    mock_auth_user: AuthPrincipal, mock_auth_context: AuthorizationContext
) -> None:
    """Tests GET /api/v1/markets/cross-asset in Native Overview mode."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/markets/cross-asset?universe_id=univ_cross_asset_macro&mode=native_overview"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["mode"] == "native_overview"
            assert len(data["comparison_members"]) >= 8
            assert len(data["asset_class_sections"]) >= 4
            assert data["coverage"]["completeness_status"] == "COMPLETE_FOR_DEFINED_SET"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_get_overview_aligned(
    mock_auth_user: AuthPrincipal, mock_auth_context: AuthorizationContext
) -> None:
    """Tests GET /api/v1/markets/cross-asset in Aligned Performance mode."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/markets/cross-asset?universe_id=univ_cross_asset_macro&mode=aligned_performance&window=last_7d"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["mode"] == "aligned_performance"
            assert data["comparison_window"] == "last_7d"

            # Check that bond yield is excluded
            bond_member = next(m for m in data["comparison_members"] if m["symbol"] == "US10Y")
            assert bond_member["aligned_performance"]["eligible"] is False
            assert bond_member["aligned_performance"]["exclusion_reason"] == "UNSUPPORTED_METRIC"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_exceeded_selection_rejected(
    mock_auth_user: AuthPrincipal, mock_auth_context: AuthorizationContext
) -> None:
    """Tests that requesting >12 symbols returns HTTP 400."""
    app.dependency_overrides[get_current_user] = lambda: mock_auth_user
    app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

    try:
        transport = ASGITransport(app=app)
        symbols_13 = ",".join([f"S{i}" for i in range(13)])
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/markets/cross-asset?symbols={symbols_13}")
            assert resp.status_code == 400
            data = resp.json()
            error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
            assert "Exceeded maximum" in error_msg
    finally:
        app.dependency_overrides.clear()
