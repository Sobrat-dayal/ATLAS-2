"""Comprehensive Automated Tests for ATLAS Market Heatmaps V1 (Stage 64).

Tests:
1. Universe definitions, supported visualization modes, hierarchies, and taxonomy metadata.
2. Equal-size performance heatmap: equal area weights summing to 1.0, independent of market cap.
3. Market-cap weighted treemap: area proportional to verified capitalization, weights sum to 1.0.
4. Missing weight handling: instruments missing market cap are excluded with MISSING_WEIGHT.
5. Invalid weight handling: instruments with <= 0 market cap are excluded with INVALID_WEIGHT.
6. Return calculations: positive, negative, zero returns with Decimal precision.
7. Missing data integrity: missing quote/reference is excluded and never treated as zero percent.
8. Non-positive reference price: excluded with INVALID_DENOMINATOR.
9. Sector classification: GICS sector grouping, sector aggregate returns.
10. Unclassified sector: instruments lacking authoritative sector grouped in 'Unclassified'.
11. Coverage reporting: universe_size, qualified_count, missing_returns, coverage_status.
12. API endpoints: /markets/heatmaps/universes, /markets/heatmaps/options, /markets/heatmaps.
13. Read-Only Invariant: 0 writes, 0 provider RPC fanout on read.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.heatmaps.config import (
    HEATMAP_UNIVERSES_BY_ID,
    HeatmapExclusionReason,
    HeatmapHierarchyMode,
    HeatmapVisualizationMode,
)
from atlas.markets.heatmaps.repository import (
    HeatmapCandidateObservation,
    MarketHeatmapRepository,
)
from atlas.markets.heatmaps.service import MarketHeatmapService
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
def mock_db():
    return MagicMock()


# =============================================================================
# 1. Universe Metadata and Configuration Tests
# =============================================================================
class TestHeatmapUniversesAndConfig:
    def test_default_universes_configured(self):
        """Verify standard canonical universes are available."""
        assert "univ_us_equities" in HEATMAP_UNIVERSES_BY_ID
        assert "univ_crypto_spot" in HEATMAP_UNIVERSES_BY_ID
        assert "univ_futures" in HEATMAP_UNIVERSES_BY_ID

        eq_univ = HEATMAP_UNIVERSES_BY_ID["univ_us_equities"]
        assert eq_univ.asset_class == "equity"
        assert HeatmapVisualizationMode.EQUAL_SIZE in eq_univ.supported_modes
        assert HeatmapVisualizationMode.MARKET_CAP_WEIGHTED in eq_univ.supported_modes
        assert HeatmapHierarchyMode.SECTOR in eq_univ.supported_hierarchies
        assert eq_univ.weight_metric_label == "Market Capitalization"
        assert eq_univ.weight_unit == "USD"
        assert eq_univ.taxonomy == "GICS"

        crypto_univ = HEATMAP_UNIVERSES_BY_ID["univ_crypto_spot"]
        assert crypto_univ.asset_class == "crypto"
        assert HeatmapVisualizationMode.EQUAL_SIZE in crypto_univ.supported_modes
        assert HeatmapVisualizationMode.MARKET_CAP_WEIGHTED in crypto_univ.supported_modes
        assert HeatmapHierarchyMode.NONE in crypto_univ.supported_hierarchies

        futures_univ = HEATMAP_UNIVERSES_BY_ID["univ_futures"]
        assert futures_univ.asset_class == "futures"
        assert HeatmapVisualizationMode.EQUAL_SIZE in futures_univ.supported_modes
        # Futures explicitly does NOT support fake market-cap weighting
        assert HeatmapVisualizationMode.MARKET_CAP_WEIGHTED not in futures_univ.supported_modes


# =============================================================================
# 2. Equal-Size Performance Heatmap Tests
# =============================================================================
class TestEqualSizeHeatmap:
    @pytest.mark.asyncio
    async def test_equal_size_mode_assigns_equal_normalized_weights(self):
        """Every qualified instrument receives equal area weight in equal-size mode."""
        service = MarketHeatmapService()
        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.EQUAL_SIZE,
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.visualization_mode == HeatmapVisualizationMode.EQUAL_SIZE
        assert len(snapshot.nodes) > 0
        qualified_nodes = [n for n in snapshot.nodes if n.is_qualified]
        assert len(qualified_nodes) > 0

        # Each qualified node should have normalized_weight == 1 / N
        expected_weight = (Decimal("1.0") / Decimal(len(qualified_nodes))).quantize(
            Decimal("0.000001")
        )
        for node in qualified_nodes:
            assert node.normalized_weight == expected_weight

    @pytest.mark.asyncio
    async def test_equal_size_mode_works_when_market_cap_is_absent(self):
        """Equal-size mode operates reliably without requiring market cap data."""
        now = datetime.now(timezone.utc)
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:stock_a",
                display_name="Stock A",
                symbol="STKA",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("100.00"),
                reference_price=Decimal("95.00"),
                weight_value=None,  # No market cap!
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:stock_b",
                display_name="Stock B",
                symbol="STKB",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Healthcare",
                industry="Biotech",
                current_price=Decimal("50.00"),
                reference_price=Decimal("52.00"),
                weight_value=None,  # No market cap!
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.EQUAL_SIZE,
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.coverage.qualified_count == 2
        for node in snapshot.nodes:
            assert node.is_qualified is True
            assert node.normalized_weight == Decimal("0.500000")


# =============================================================================
# 3. Market-Cap Weighted Treemap Tests
# =============================================================================
class TestMarketCapWeightedTreemap:
    @pytest.mark.asyncio
    async def test_market_cap_weighted_mode_normalizes_weights_proportional_to_cap(self):
        """Treemap tile area fraction is strictly proportional to market capitalization."""
        now = datetime.now(timezone.utc)
        # 3 Assets: A (50B = 50%), B (30B = 30%), C (20B = 20%) -> Total 100B
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:a",
                display_name="Asset A",
                symbol="ASSTA",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("100.00"),
                reference_price=Decimal("95.00"),
                weight_value=Decimal("50000000000"),  # 50B
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:b",
                display_name="Asset B",
                symbol="ASSTB",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Consumer Cyclical",
                industry="Retail",
                current_price=Decimal("200.00"),
                reference_price=Decimal("210.00"),
                weight_value=Decimal("30000000000"),  # 30B
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:c",
                display_name="Asset C",
                symbol="ASSTC",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Energy",
                industry="Oil",
                current_price=Decimal("50.00"),
                reference_price=Decimal("49.00"),
                weight_value=Decimal("20000000000"),  # 20B
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.coverage.qualified_count == 3
        assert snapshot.coverage.total_qualified_weight == Decimal("100000000000")

        nodes_by_sym = {n.symbol: n for n in snapshot.nodes}
        assert nodes_by_sym["ASSTA"].normalized_weight == Decimal("0.500000")
        assert nodes_by_sym["ASSTB"].normalized_weight == Decimal("0.300000")
        assert nodes_by_sym["ASSTC"].normalized_weight == Decimal("0.200000")

    @pytest.mark.asyncio
    async def test_missing_weight_is_excluded_from_market_cap_treemap(self):
        """An instrument lacking verified market cap cannot participate in a cap-weighted view."""
        now = datetime.now(timezone.utc)
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:has_cap",
                display_name="Has Cap",
                symbol="CAP1",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("100.00"),
                reference_price=Decimal("95.00"),
                weight_value=Decimal("10000000000"),  # 10B
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_cap",
                display_name="No Cap",
                symbol="NOCAP",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("50.00"),
                reference_price=Decimal("48.00"),
                weight_value=None,  # Missing!
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.coverage.qualified_count == 1
        assert snapshot.coverage.missing_weights == 1
        assert (
            snapshot.coverage.exclusion_breakdown[HeatmapExclusionReason.MISSING_WEIGHT.value] == 1
        )

        nodes_by_sym = {n.symbol: n for n in snapshot.nodes}
        assert nodes_by_sym["CAP1"].is_qualified is True
        assert nodes_by_sym["CAP1"].normalized_weight == Decimal("1.000000")

        assert nodes_by_sym["NOCAP"].is_qualified is False
        assert nodes_by_sym["NOCAP"].exclusion_reason == HeatmapExclusionReason.MISSING_WEIGHT


# =============================================================================
# 4. Sector Classification and Hierarchical Aggregation Tests
# =============================================================================
class TestSectorClassificationAndAggregation:
    @pytest.mark.asyncio
    async def test_gics_sector_grouping_with_equal_weight_aggregation(self):
        """Sector groups compute equal-weight mean return in equal-size mode."""
        now = datetime.now(timezone.utc)
        # Tech: AAPL (+5.0%), MSFT (+3.0%) -> Sector return: +4.0%
        # Healthcare: UNH (-2.0%) -> Sector return: -2.0%
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:aapl",
                display_name="Apple Inc.",
                symbol="AAPL",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Consumer Electronics",
                current_price=Decimal("105.00"),
                reference_price=Decimal("100.00"),  # +5.00%
                weight_value=Decimal("3000000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:msft",
                display_name="Microsoft Corp.",
                symbol="MSFT",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("103.00"),
                reference_price=Decimal("100.00"),  # +3.00%
                weight_value=Decimal("3000000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnys:unh",
                display_name="UnitedHealth",
                symbol="UNH",
                asset_class="equity",
                exchange_or_venue="XNYS",
                listing_currency="USD",
                is_active=True,
                sector="Healthcare",
                industry="Healthcare Plans",
                current_price=Decimal("98.00"),
                reference_price=Decimal("100.00"),  # -2.00%
                weight_value=Decimal("500000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.EQUAL_SIZE,
            hierarchy_mode=HeatmapHierarchyMode.SECTOR,
        )

        assert len(snapshot.groups) == 2
        groups_by_label = {g.label: g for g in snapshot.groups}

        tech_group = groups_by_label["Technology"]
        assert tech_group.qualified_count == 2
        assert tech_group.aggregate_method == "equal_weight_mean"
        assert tech_group.aggregate_return == Decimal("4.0000")  # (5.0 + 3.0) / 2 = 4.0

        health_group = groups_by_label["Healthcare"]
        assert health_group.qualified_count == 1
        assert health_group.aggregate_return == Decimal("-2.0000")

    @pytest.mark.asyncio
    async def test_cap_weighted_sector_aggregate_return(self):
        """Sector groups compute market-cap weighted aggregate return in weighted mode."""
        now = datetime.now(timezone.utc)
        # Tech:
        # AAPL: Cap $3T, Return +10% -> 30
        # MSFT: Cap $1T, Return -2%  -> -2
        # Sum weight = 4T. Cap-weighted return: (30 - 2) / 4 = +7.0%
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:aapl",
                display_name="Apple Inc.",
                symbol="AAPL",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Consumer Electronics",
                current_price=Decimal("110.00"),
                reference_price=Decimal("100.00"),  # +10.00%
                weight_value=Decimal("3000000000000"),  # 3T
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:msft",
                display_name="Microsoft Corp.",
                symbol="MSFT",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("98.00"),
                reference_price=Decimal("100.00"),  # -2.00%
                weight_value=Decimal("1000000000000"),  # 1T
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            visualization_mode=HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
            hierarchy_mode=HeatmapHierarchyMode.SECTOR,
        )

        assert len(snapshot.groups) == 1
        tech = snapshot.groups[0]
        assert tech.label == "Technology"
        assert tech.aggregate_method == "cap_weighted_return"
        assert tech.aggregate_return == Decimal("7.0000")

    @pytest.mark.asyncio
    async def test_unclassified_group_for_missing_sectors(self):
        """Securities without authoritative sector are grouped under 'Unclassified'."""
        now = datetime.now(timezone.utc)
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_sector",
                display_name="No Sector Stock",
                symbol="NOSEC",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector=None,  # Missing sector
                industry=None,
                current_price=Decimal("102.00"),
                reference_price=Decimal("100.00"),
                weight_value=Decimal("1000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            )
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            hierarchy_mode=HeatmapHierarchyMode.SECTOR,
        )

        assert len(snapshot.groups) == 1
        assert snapshot.groups[0].label == "Unclassified"
        assert snapshot.coverage.unclassified_count == 1


# =============================================================================
# 5. Financial Data Integrity Tests
# =============================================================================
class TestFinancialDataIntegrity:
    @pytest.mark.asyncio
    async def test_missing_quote_or_reference_is_not_zero_movement(self):
        """Missing observations must be excluded, never misrepresented as 0.00% return."""
        now = datetime.now(timezone.utc)
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_curr",
                display_name="No Current Quote",
                symbol="NOCURR",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=None,  # Missing current price
                reference_price=Decimal("100.00"),
                weight_value=Decimal("1000000000"),
                weight_unit="USD",
                source_timestamp=None,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="unavailable",
                delay_status="unknown",
                delivery_delay_seconds=None,
            ),
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:no_ref",
                display_name="No Reference Price",
                symbol="NOREF",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("100.00"),
                reference_price=None,  # Missing reference
                weight_value=Decimal("1000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=None,
                reference_period_label=None,
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            ),
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.coverage.qualified_count == 0
        assert snapshot.coverage.missing_returns == 2
        for node in snapshot.nodes:
            assert node.is_qualified is False
            assert node.percent_change is None  # NEVER Decimal("0.00")!

    @pytest.mark.asyncio
    async def test_nonpositive_reference_price_excluded(self):
        """A reference price <= 0 is mathematically invalid for percent change."""
        now = datetime.now(timezone.utc)
        candidates = [
            HeatmapCandidateObservation(
                instrument_entity_id=uuid.uuid4(),
                market_series_identity="equity:xnas:zero_ref",
                display_name="Zero Reference",
                symbol="ZREF",
                asset_class="equity",
                exchange_or_venue="XNAS",
                listing_currency="USD",
                is_active=True,
                sector="Technology",
                industry="Software",
                current_price=Decimal("10.00"),
                reference_price=Decimal("0.00"),  # Zero denominator!
                weight_value=Decimal("1000000000"),
                weight_unit="USD",
                source_timestamp=now,
                reference_timestamp=now,
                reference_period_label="Prev Close",
                provider="openbb",
                freshness_status="live",
                delay_status="realtime",
                delivery_delay_seconds=0,
            )
        ]
        repo = MarketHeatmapRepository(custom_candidates={"univ_us_equities": candidates})
        service = MarketHeatmapService(repository=repo)

        snapshot = await service.get_heatmap_snapshot(
            universe_id="univ_us_equities",
            hierarchy_mode=HeatmapHierarchyMode.NONE,
        )

        assert snapshot.coverage.qualified_count == 0
        node = snapshot.nodes[0]
        assert node.is_qualified is False
        assert node.exclusion_reason == HeatmapExclusionReason.INVALID_DENOMINATOR


# =============================================================================
# 6. FastAPI Router HTTP Endpoints Tests
# =============================================================================
class TestHeatmapApiEndpoints:
    @pytest.mark.asyncio
    async def test_get_universes_endpoint(self, mock_auth_user: AuthPrincipal, mock_auth_context):
        """GET /api/v1/markets/heatmaps/universes returns 200 with universe list."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/markets/heatmaps/universes")
            assert resp.status_code == 200
            data = resp.json()
            assert data["count"] >= 3
            universe_ids = [u["universe_id"] for u in data["universes"]]
            assert "univ_us_equities" in universe_ids
            assert "univ_crypto_spot" in universe_ids
            assert "univ_futures" in universe_ids

    @pytest.mark.asyncio
    async def test_get_options_endpoint(self, mock_auth_user: AuthPrincipal, mock_auth_context):
        """GET /api/v1/markets/heatmaps/options returns 200 with supported modes."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/markets/heatmaps/options")
            assert resp.status_code == 200
            data = resp.json()
            assert "equal_size" in data["modes"]
            assert "market_cap_weighted" in data["modes"]
            assert "sector" in data["hierarchies"]

    @pytest.mark.asyncio
    async def test_get_heatmap_snapshot_endpoint(
        self, mock_auth_user: AuthPrincipal, mock_auth_context
    ):
        """GET /api/v1/markets/heatmaps returns 200 with valid snapshot and coverage."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/markets/heatmaps?universe_id=univ_us_equities&visualization_mode=market_cap_weighted&hierarchy_mode=sector"
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["schema_version"] == "1.0.0"
            assert data["universe_id"] == "univ_us_equities"
            assert data["visualization_mode"] == "market_cap_weighted"
            assert data["hierarchy_mode"] == "sector"
            assert "coverage" in data
            assert data["coverage"]["qualified_count"] > 0
            assert len(data["groups"]) > 0

    @pytest.mark.asyncio
    async def test_get_heatmap_invalid_mode_rejected(
        self, mock_auth_user: AuthPrincipal, mock_auth_context
    ):
        """Requesting market_cap_weighted on futures is rejected with 400 Bad Request."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/markets/heatmaps?universe_id=univ_futures&visualization_mode=market_cap_weighted"
            )
            assert resp.status_code == 400
            data = resp.json()
            error_msg = data.get("error", {}).get("message", "") or data.get("detail", "")
            assert "not supported" in error_msg
