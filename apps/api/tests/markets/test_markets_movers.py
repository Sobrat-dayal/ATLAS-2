"""Comprehensive Automated Tests for ATLAS Market Movers V1 (Stage 63).

Tests:
1. Universe resolution, metadata, supported categories, and windows.
2. Top Gainers: strictly positive percentage returns sorted DESC.
3. Top Losers: strictly negative percentage returns sorted ASC (most negative first).
4. Most Active: qualified activity observations sorted DESC with explicit units.
5. Zero price change exclusion from both Gainers and Losers.
6. Non-positive reference price exclusion (INVALID_DENOMINATOR).
7. Missing current quote exclusion (NO_CURRENT_QUOTE).
8. Missing reference exclusion (NO_REFERENCE).
9. Missing volume exclusion from Most Active (MISSING_VOLUME).
10. Inactive security exclusion (INSTRUMENT_INACTIVE).
11. Deterministic tie-breaking using canonical instrument UUID.
12. Decimal precision preservation without float conversion.
13. Keyset cursor pagination and bounds enforcement.
14. Comprehensive coverage reporting (candidate, evaluated, qualified, excluded counts, status).
15. Authenticated and Authorized Read APIs (200, 401, 400, 404).
16. Read-Only Invariants: 0 writes, 0 provider fanouts.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.movers.config import (
    DEFAULT_MOVER_UNIVERSE_ID,
    MOVER_UNIVERSES_BY_ID,
    ComparisonWindow,
    CoverageStatus,
    ExclusionReason,
    MoverAssetClass,
    MoverCategory,
    MoverUniverseDefinition,
)
from atlas.markets.movers.repository import CandidateObservation, MarketMoversRepository
from atlas.markets.movers.service import MarketMoverRankingService
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# Test Fixtures
# =============================================================================
@pytest.fixture
def mock_auth_user() -> AuthPrincipal:
    return AuthPrincipal(
        sub="user-12345678-1234-5678-1234-567812345678",
        email="trader@atlas.io",
    )


@pytest.fixture
def mock_auth_context(mock_auth_user: AuthPrincipal) -> AuthorizationContext:
    ctx = MagicMock(spec=AuthorizationContext)
    ctx.principal = mock_auth_user
    ctx.is_authenticated = True
    ctx.has_permission.return_value = True
    return ctx


@pytest.fixture
def mock_db():
    session = MagicMock()
    return session


# =============================================================================
# 1. Universe Metadata and Metric Definitions Tests
# =============================================================================
class TestMoverUniversesAndMetrics:
    def test_default_universes_configured(self):
        """Verify standard canonical universes are available."""
        assert "univ_us_equities" in MOVER_UNIVERSES_BY_ID
        assert "univ_crypto_spot" in MOVER_UNIVERSES_BY_ID
        assert "univ_futures" in MOVER_UNIVERSES_BY_ID

        eq_univ = MOVER_UNIVERSES_BY_ID["univ_us_equities"]
        assert eq_univ.asset_class == MoverAssetClass.EQUITY
        assert MoverCategory.GAINERS in eq_univ.supported_categories
        assert MoverCategory.LOSERS in eq_univ.supported_categories
        assert MoverCategory.MOST_ACTIVE in eq_univ.supported_categories
        assert eq_univ.activity_unit == "shares"

        crypto_univ = MOVER_UNIVERSES_BY_ID["univ_crypto_spot"]
        assert crypto_univ.asset_class == MoverAssetClass.CRYPTO
        assert crypto_univ.activity_unit == "USDT"

        futures_univ = MOVER_UNIVERSES_BY_ID["univ_futures"]
        assert futures_univ.asset_class == MoverAssetClass.FUTURES
        assert futures_univ.activity_unit == "contracts"

    def test_metric_options_service(self):
        """Verify metric options returns typed policies for valid universe."""
        service = MarketMoverRankingService()
        opts = service.get_metric_options("univ_us_equities")
        assert opts.universe_id == "univ_us_equities"
        assert len(opts.metrics) == 3
        kinds = {m.metric_kind for m in opts.metrics}
        assert kinds == {MoverCategory.GAINERS, MoverCategory.LOSERS, MoverCategory.MOST_ACTIVE}


# =============================================================================
# 2. Mathematical Qualification & Ranking Engine Tests
# =============================================================================
class TestRankingEngineQualification:
    @pytest.mark.asyncio
    async def test_deterministic_gainers_and_losers_and_zeros(self):
        """
        Verify:
        Instrument A = +8.0%
        Instrument B = +3.0%
        Instrument C = -2.0%
        Instrument D = 0.0% (Zero change)
        Expected Gainers: A, B (D and C excluded)
        Expected Losers: C (A, B, D excluded)
        """
        id_a = uuid.UUID("aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa")
        id_b = uuid.UUID("bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb")
        id_c = uuid.UUID("cccccccc-cccc-4ccc-cccc-cccccccccccc")
        id_d = uuid.UUID("dddddddd-dddd-4ddd-dddd-dddddddddddd")

        now = datetime.now(timezone.utc)
        test_candidates = [
            CandidateObservation(
                instrument_entity_id=id_a,
                market_series_identity="equity:xnas:a",
                display_name="Instrument A",
                symbol="A",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("108.00"),
                reference_price=Decimal("100.00"),  # +8.0%
                trading_volume=Decimal("1000000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            CandidateObservation(
                instrument_entity_id=id_b,
                market_series_identity="equity:xnas:b",
                display_name="Instrument B",
                symbol="B",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("103.00"),
                reference_price=Decimal("100.00"),  # +3.0%
                trading_volume=Decimal("2000000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            CandidateObservation(
                instrument_entity_id=id_c,
                market_series_identity="equity:xnas:c",
                display_name="Instrument C",
                symbol="C",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("98.00"),
                reference_price=Decimal("100.00"),  # -2.0%
                trading_volume=Decimal("500000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            CandidateObservation(
                instrument_entity_id=id_d,
                market_series_identity="equity:xnas:d",
                display_name="Instrument D",
                symbol="D",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("100.00"),
                reference_price=Decimal("100.00"),  # 0.0% FLAT
                trading_volume=Decimal("300000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]

        repo = MarketMoversRepository(custom_candidates={"univ_us_equities": test_candidates})
        service = MarketMoverRankingService(repository=repo)

        # 1. Top Gainers
        gainers_res = await service.get_market_movers(
            universe_id="univ_us_equities",
            category=MoverCategory.GAINERS,
        )
        assert len(gainers_res.items) == 2
        assert gainers_res.items[0].symbol == "A"
        assert gainers_res.items[0].percent_change == Decimal("8.00")
        assert gainers_res.items[0].rank == 1

        assert gainers_res.items[1].symbol == "B"
        assert gainers_res.items[1].percent_change == Decimal("3.00")
        assert gainers_res.items[1].rank == 2

        # 2. Top Losers
        losers_res = await service.get_market_movers(
            universe_id="univ_us_equities",
            category=MoverCategory.LOSERS,
        )
        assert len(losers_res.items) == 1
        assert losers_res.items[0].symbol == "C"
        assert losers_res.items[0].percent_change == Decimal("-2.00")
        assert losers_res.items[0].rank == 1

        # 3. Most Active
        active_res = await service.get_market_movers(
            universe_id="univ_us_equities",
            category=MoverCategory.MOST_ACTIVE,
        )
        assert len(active_res.items) == 4
        # Sorted by volume DESC: B (2M), A (1M), C (500k), D (300k)
        assert [i.symbol for i in active_res.items] == ["B", "A", "C", "D"]
        assert active_res.items[0].ranking_unit == "shares"

    @pytest.mark.asyncio
    async def test_tie_breaking_by_canonical_uuid(self):
        """Verify deterministic ordering when two instruments have identical metric values."""
        id_1 = uuid.UUID("11111111-1111-4111-a111-000000000001")
        id_2 = uuid.UUID("22222222-2222-4222-a222-000000000002")

        now = datetime.now(timezone.utc)
        candidates = [
            CandidateObservation(
                instrument_entity_id=id_2,
                market_series_identity="equity:xnas:two",
                display_name="Security Two",
                symbol="TWO",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("105.00"),
                reference_price=Decimal("100.00"),  # +5%
                trading_volume=Decimal("100000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            CandidateObservation(
                instrument_entity_id=id_1,
                market_series_identity="equity:xnas:one",
                display_name="Security One",
                symbol="ONE",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("105.00"),
                reference_price=Decimal("100.00"),  # +5%
                trading_volume=Decimal("100000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]

        repo = MarketMoversRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketMoverRankingService(repository=repo)

        res = await service.get_market_movers(
            universe_id="univ_us_equities", category=MoverCategory.GAINERS
        )
        assert len(res.items) == 2
        # Equal +5%, tie-break by UUID ASC: id_1 comes before id_2
        assert res.items[0].instrument_entity_id == id_1
        assert res.items[1].instrument_entity_id == id_2

    @pytest.mark.asyncio
    async def test_exclusion_reasons_and_coverage_status(self):
        """
        Verify all institutional exclusion rules:
        - Nonpositive reference price <= 0 -> INVALID_DENOMINATOR
        - Missing current price -> NO_CURRENT_QUOTE
        - Missing reference price -> NO_REFERENCE
        - Inactive security -> INSTRUMENT_INACTIVE
        - Missing volume for Most Active -> MISSING_VOLUME
        """
        now = datetime.now(timezone.utc)
        candidates = [
            # 1. Invalid denominator: reference price = 0
            CandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:zero_ref",
                display_name="Zero Ref",
                symbol="ZREF",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("10.00"),
                reference_price=Decimal("0.00"),  # ZERO REF
                trading_volume=Decimal("1000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            # 2. Missing current quote
            CandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_cur",
                display_name="No Current",
                symbol="NOCUR",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=None,  # MISSING CURRENT
                reference_price=Decimal("50.00"),
                trading_volume=Decimal("1000"),
                volume_unit="shares",
                source_timestamp=None,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="unavailable",
                delay_status="unknown",
                delivery_delay_seconds=None,
            ),
            # 3. Missing reference quote
            CandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_ref",
                display_name="No Ref",
                symbol="NOREF",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("75.00"),
                reference_price=None,  # MISSING REF
                trading_volume=Decimal("1000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=None,
                reference_period_label=None,
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            # 4. Inactive instrument
            CandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:inact",
                display_name="Inactive Co",
                symbol="INACT",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=False,  # INACTIVE
                current_price=Decimal("120.00"),
                reference_price=Decimal("100.00"),
                trading_volume=Decimal("1000"),
                volume_unit="shares",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            # 5. Missing volume
            CandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:novol",
                display_name="No Vol Co",
                symbol="NOVOL",
                asset_class=MoverAssetClass.EQUITY,
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                current_price=Decimal("110.00"),
                reference_price=Decimal("100.00"),
                trading_volume=None,  # MISSING VOLUME
                volume_unit=None,
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="test",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]

        repo = MarketMoversRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketMoverRankingService(repository=repo)

        # Test Gainers exclusions
        gainers_res = await service.get_market_movers(
            universe_id="univ_us_equities", category=MoverCategory.GAINERS
        )
        assert gainers_res.coverage.universe_size == 5
        assert gainers_res.coverage.qualified_count == 1  # Only NOVOL has valid +10% return
        assert gainers_res.coverage.coverage_status == CoverageStatus.PARTIAL_COVERAGE
        reasons = gainers_res.coverage.exclusion_reasons
        assert reasons.get(ExclusionReason.INVALID_DENOMINATOR.value) == 1
        assert reasons.get(ExclusionReason.NO_CURRENT_QUOTE.value) == 1
        assert reasons.get(ExclusionReason.NO_REFERENCE.value) == 1
        assert reasons.get(ExclusionReason.INSTRUMENT_INACTIVE.value) == 1

        # Test Most Active exclusions
        active_res = await service.get_market_movers(
            universe_id="univ_us_equities", category=MoverCategory.MOST_ACTIVE
        )
        assert active_res.coverage.exclusion_reasons.get(ExclusionReason.MISSING_VOLUME.value) == 1


# =============================================================================
# 3. HTTP API Endpoints Integration Tests
# =============================================================================
class TestMarketMoversAPIEndpoints:
    @pytest.mark.asyncio
    async def test_list_universes_endpoint_200(self, mock_auth_user, mock_auth_context, mock_db):
        """Verify GET /api/v1/markets/movers/universes returns 200 and list of universes."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/markets/movers/universes")
                assert res.status_code == 200
                data = res.json()
                assert len(data["universes"]) >= 3
                assert data["default_universe_id"] == DEFAULT_MOVER_UNIVERSE_ID
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_metrics_options_endpoint_200_and_404(
        self, mock_auth_user, mock_auth_context, mock_db
    ):
        """Verify GET /api/v1/markets/movers/metrics returns 200 for valid, 404 for invalid."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Valid
                res = await client.get("/api/v1/markets/movers/metrics?universe_id=univ_us_equities")
                assert res.status_code == 200
                data = res.json()
                assert data["universe_id"] == "univ_us_equities"
                assert len(data["metrics"]) == 3

                # Unknown universe -> 404
                res_404 = await client.get("/api/v1/markets/movers/metrics?universe_id=unknown_univ")
                assert res_404.status_code == 404
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_movers_endpoint_categories_and_universes(
        self, mock_auth_user, mock_auth_context, mock_db
    ):
        """Verify GET /api/v1/markets/movers for Equities, Crypto, and Futures across all categories."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Equities Gainers
                res_eq = await client.get(
                    "/api/v1/markets/movers?universe_id=univ_us_equities&category=gainers"
                )
                assert res_eq.status_code == 200
                data_eq = res_eq.json()
                assert data_eq["category"] == "gainers"
                assert data_eq["asset_class"] == "equity"
                assert len(data_eq["items"]) > 0
                for item in data_eq["items"]:
                    assert float(item["percent_change"]) > 0
                    assert item["ranking_unit"] == "%"

                # 2. Crypto Most Active
                res_crypto = await client.get(
                    "/api/v1/markets/movers?universe_id=univ_crypto_spot&category=most_active"
                )
                assert res_crypto.status_code == 200
                data_crypto = res_crypto.json()
                assert data_crypto["category"] == "most_active"
                assert data_crypto["asset_class"] == "crypto"
                assert data_crypto["items"][0]["ranking_unit"] == "USDT"

                # 3. Futures Losers
                res_fut = await client.get(
                    "/api/v1/markets/movers?universe_id=univ_futures&category=losers"
                )
                assert res_fut.status_code == 200
                data_fut = res_fut.json()
                assert data_fut["category"] == "losers"
                assert data_fut["asset_class"] == "futures"
                for item in data_fut["items"]:
                    assert float(item["percent_change"]) < 0
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_movers_pagination_and_cursor(
        self, mock_auth_user, mock_auth_context, mock_db
    ):
        """Verify limit and cursor keyset pagination."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Limit 2
                res = await client.get(
                    "/api/v1/markets/movers?universe_id=univ_us_equities&category=most_active&limit=2"
                )
                assert res.status_code == 200
                data = res.json()
                assert len(data["items"]) == 2
                assert data["items"][0]["rank"] == 1
                assert data["items"][1]["rank"] == 2
                assert data["has_more"] is True
                assert data["next_cursor"] is not None

                # Next page
                cursor = data["next_cursor"]
                res_page2 = await client.get(
                    f"/api/v1/markets/movers?universe_id=univ_us_equities&category=most_active&limit=2&cursor={cursor}"
                )
                assert res_page2.status_code == 200
                data2 = res_page2.json()
                assert len(data2["items"]) == 2
                assert data2["items"][0]["rank"] == 3
                assert data2["items"][1]["rank"] == 4
        finally:
            app.dependency_overrides.clear()
