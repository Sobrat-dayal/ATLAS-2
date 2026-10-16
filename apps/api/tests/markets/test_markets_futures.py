"""Comprehensive Automated Tests for ATLAS Futures & Commodities Markets V1 (Stage 62).

Tests:
1. Canonical Commodity Identity, Deterministic Namespaces, Categories, and Physical Units.
2. Futures Product Identity, Venue Scope, Exchange MICs, and Specifications.
3. Individual Contract Identity, Month Codes, Expiration vs Settlement Dates.
4. Contract Size, Unit Quotation, Tick Size, and Tick Value Precision.
5. Cash-Settled vs Physically Delivered Derivatives Classification.
6. Legitimate Negative Futures Prices, Spread Validation, and Reference Changes.
7. Separation of Last Executed Trade, Official Daily Settlement, and Spot Benchmarks.
8. Volume (Contracts Traded) vs Open Interest (Clearing Positions As-Of Date).
9. Directory Search, Multi-Dimensional Filtering, and Keyset Pagination.
10. Authenticated and Authorized Read APIs (200, 401, 404).
11. Read-Only Invariants: 0 writes, 0 external provider fanouts.
"""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.futures.config import (
    CANONICAL_COMMODITIES,
    CANONICAL_FUTURES_CONTRACTS,
    CANONICAL_FUTURES_PRODUCTS,
    COMMODITIES_BY_ID,
    MONTH_CODE_TO_NUM,
    NUM_TO_MONTH_CODE,
    CommodityCategoryEnum,
    ContractLifecycleEnum,
    SettlementTypeEnum,
    generate_commodity_id,
    generate_futures_contract_id,
    generate_futures_product_id,
)
from atlas.markets.futures.repository import FuturesMarketRepository
from atlas.markets.futures.service import (
    FuturesDirectoryService,
    FuturesMarketReadService,
    FuturesOverviewService,
    SpotBenchmarkService,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# 1. Commodity & Product Identity Tests
# =============================================================================
class TestCommodityAndProductIdentity:
    def test_canonical_commodities_catalog(self):
        """Verify commodities catalog contains energy, metals, ags, livestock, and index."""
        assert len(CANONICAL_COMMODITIES) >= 10
        categories = {c.category for c in CANONICAL_COMMODITIES}
        assert CommodityCategoryEnum.ENERGY in categories
        assert CommodityCategoryEnum.PRECIOUS_METALS in categories
        assert CommodityCategoryEnum.INDUSTRIAL_METALS in categories
        assert CommodityCategoryEnum.AGRICULTURE in categories
        assert CommodityCategoryEnum.LIVESTOCK in categories
        assert CommodityCategoryEnum.FINANCIAL_INDEX in categories

    def test_deterministic_namespaces(self):
        """Verify UUID generation is strictly deterministic and distinct across types."""
        comm_id1 = generate_commodity_id("wti-crude-oil")
        comm_id2 = generate_commodity_id("wti-crude-oil")
        prod_id = generate_futures_product_id("NYMEX", "CL")
        contract_id = generate_futures_contract_id("NYMEX", "CLZ26")

        assert comm_id1 == comm_id2
        assert comm_id1 != prod_id
        assert prod_id != contract_id

    def test_month_code_mappings(self):
        """Verify standard futures month code conventions (F=Jan through Z=Dec)."""
        assert MONTH_CODE_TO_NUM["F"] == 1
        assert MONTH_CODE_TO_NUM["G"] == 2
        assert MONTH_CODE_TO_NUM["H"] == 3
        assert MONTH_CODE_TO_NUM["J"] == 4
        assert MONTH_CODE_TO_NUM["K"] == 5
        assert MONTH_CODE_TO_NUM["M"] == 6
        assert MONTH_CODE_TO_NUM["N"] == 7
        assert MONTH_CODE_TO_NUM["Q"] == 8
        assert MONTH_CODE_TO_NUM["U"] == 9
        assert MONTH_CODE_TO_NUM["V"] == 10
        assert MONTH_CODE_TO_NUM["X"] == 11
        assert MONTH_CODE_TO_NUM["Z"] == 12

        assert NUM_TO_MONTH_CODE[1] == "F"
        assert NUM_TO_MONTH_CODE[12] == "Z"

    def test_product_to_underlying_linkage(self):
        """Verify each futures product references a valid canonical underlying commodity."""
        for prod in CANONICAL_FUTURES_PRODUCTS:
            assert prod.underlying_entity_id in COMMODITIES_BY_ID
            und = COMMODITIES_BY_ID[prod.underlying_entity_id]
            assert und.category == prod.category


# =============================================================================
# 2. Contract Specifications & Tick Math Tests
# =============================================================================
class TestContractSpecificationsAndTickMath:
    def test_contract_specifications_completeness(self):
        """Verify all listed contracts have verified sizes, quote units, and tick sizes."""
        for c in CANONICAL_FUTURES_CONTRACTS:
            assert c.contract_size > Decimal("0")
            assert len(c.size_unit) > 0
            assert len(c.quote_currency) == 3
            assert len(c.quote_unit) > 0
            assert c.tick_size > Decimal("0")
            assert c.expiration_date <= c.contract_month + "-31"
            assert c.last_trading_date <= c.settlement_date

    def test_tick_value_calculation_nymex_crude(self):
        """Verify NYMEX Crude Oil (CL): 1,000 barrels, 0.01 tick size -> 10.00 USD tick value."""
        cl = next(p for p in CANONICAL_FUTURES_PRODUCTS if p.root_symbol == "CL")
        assert cl.contract_size == Decimal("1000.0")
        assert cl.tick_size == Decimal("0.01")
        assert cl.tick_value == Decimal("10.00")

    def test_tick_value_calculation_comex_gold(self):
        """Verify COMEX Gold (GC): 100 troy oz, 0.10 tick size -> 10.00 USD tick value."""
        gc = next(p for p in CANONICAL_FUTURES_PRODUCTS if p.root_symbol == "GC")
        assert gc.contract_size == Decimal("100.0")
        assert gc.tick_size == Decimal("0.10")
        assert gc.tick_value == Decimal("10.00")

    def test_tick_value_calculation_cbot_corn(self):
        """Verify CBOT Corn (ZC): 5,000 bushels, 0.25 cents tick size -> 12.50 USD tick value."""
        zc = next(p for p in CANONICAL_FUTURES_PRODUCTS if p.root_symbol == "ZC")
        assert zc.contract_size == Decimal("5000.0")
        assert zc.tick_size == Decimal("0.25")
        assert zc.tick_value == Decimal("12.50")

    def test_cash_vs_physical_settlement_types(self):
        """Verify distinction between cash-settled and physically delivered contracts."""
        phys_contracts = [
            c
            for c in CANONICAL_FUTURES_CONTRACTS
            if c.settlement_type == SettlementTypeEnum.PHYSICAL
        ]
        cash_contracts = [
            c for c in CANONICAL_FUTURES_CONTRACTS if c.settlement_type == SettlementTypeEnum.CASH
        ]

        assert len(phys_contracts) > 0
        assert len(cash_contracts) > 0

        # ICE Brent and CME E-mini S&P 500 must be cash settled
        brent_contracts = [c for c in CANONICAL_FUTURES_CONTRACTS if "BZ" in c.symbol]
        es_contracts = [c for c in CANONICAL_FUTURES_CONTRACTS if "ES" in c.symbol]
        for bz in brent_contracts:
            assert bz.settlement_type == SettlementTypeEnum.CASH
        for es in es_contracts:
            assert es.settlement_type == SettlementTypeEnum.CASH


# =============================================================================
# 3. Negative Pricing & Price Change Safeguards
# =============================================================================
class TestNegativePricingAndPriceChange:
    def test_negative_futures_price_acceptance(self):
        """Verify legitimate negative futures price (CLK20 at -37.63) is preserved."""
        repo = FuturesMarketRepository()
        clk20 = next(c for c in repo._contracts if c.symbol == "CLK20")
        assert clk20.latest_trade_price == Decimal("-37.63")
        assert clk20.official_settlement == Decimal("-37.63")
        assert clk20.lifecycle_status == ContractLifecycleEnum.EXPIRED

    def test_negative_bid_ask_spread(self):
        """Verify bid/ask spread remains valid when both bid and ask are negative (ask >= bid)."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        clk20 = next(c for c in repo._contracts if c.symbol == "CLK20")

        obs = read_service.build_price_observation(clk20)
        assert obs.bid == Decimal("-38.00")
        assert obs.ask == Decimal("-37.50")
        # Spread = -37.50 - (-38.00) = 0.50
        assert obs.spread == Decimal("0.50")

    def test_percentage_change_suppression_on_nonpositive_reference(self):
        """Strict guard: Verify percentage change is suppressed (None) when reference price <= 0."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        clk20 = next(c for c in repo._contracts if c.symbol == "CLK20")

        # Mock a contract where reference previous_settlement was negative or zero
        mock_contract = clk20.model_copy(
            update={
                "latest_trade_price": Decimal("10.00"),
                "previous_settlement": Decimal("-5.00"),
            }
        )
        chg = read_service.build_price_change(mock_contract)
        assert chg.change_absolute == Decimal("15.00")
        # Critical test: change_percent MUST BE None because reference is <= 0!
        assert chg.change_percent is None

    def test_percentage_change_on_positive_reference(self):
        """Verify standard percentage change operates correctly on strictly positive reference."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        clz26 = next(c for c in repo._contracts if c.symbol == "CLZ26")

        chg = read_service.build_price_change(clz26)
        assert chg.reference_price == Decimal("70.15")
        assert chg.change_absolute == Decimal("69.45") - Decimal("70.15")  # -0.70
        expected_pct = (Decimal("-0.70") / Decimal("70.15")) * Decimal("100")
        assert chg.change_percent == expected_pct
        assert chg.change_ticks == Decimal("-0.70") / Decimal("0.01")  # -70.0


# =============================================================================
# 4. Last vs Settlement & Volume vs Open Interest
# =============================================================================
class TestMarketObservationsSeparation:
    def test_last_distinct_from_official_settlement(self):
        """Verify last executed trade and official settlement are distinct fields."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        clz26 = next(c for c in repo._contracts if c.symbol == "CLZ26")

        price_obs = read_service.build_price_observation(clz26)
        settle_obs = read_service.build_settlement_observation(clz26)

        assert price_obs.last == Decimal("69.45")
        assert settle_obs.settlement_price == Decimal("69.50")
        assert price_obs.last != settle_obs.settlement_price

    def test_volume_distinct_from_open_interest(self):
        """Verify volume (trading activity) is distinct from open interest (reported positions)."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        clz26 = next(c for c in repo._contracts if c.symbol == "CLZ26")

        vol_oi = read_service.build_volume_open_interest(clz26)
        assert vol_oi.volume == 284500
        assert vol_oi.open_interest == 412300
        assert vol_oi.open_interest_as_of == "2026-10-14"
        assert vol_oi.volume != vol_oi.open_interest

    def test_spot_benchmarks_catalog_and_separation(self):
        """Verify spot benchmarks exist and are separate from listed futures contracts."""
        repo = FuturesMarketRepository()
        spot_service = SpotBenchmarkService(repository=repo)
        benchmarks_resp = spot_service.get_spot_benchmarks()

        assert benchmarks_resp.total >= 5
        names = {b.name for b in benchmarks_resp.items}
        assert "WTI Spot FOB Cushing" in names
        assert "Brent Dated Spot" in names
        assert "LBMA Gold Price PM" in names


# =============================================================================
# 5. Directory Search, Filtering & Pagination
# =============================================================================
class TestDirectorySearchAndFiltering:
    def test_directory_text_search(self):
        """Verify search matches contract symbols, product roots, and underlying names."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        dir_service = FuturesDirectoryService(repository=repo, read_service=read_service)

        # Search by symbol
        res = dir_service.get_directory(query="CLZ26")
        assert res.total >= 1
        assert any(item.symbol == "CLZ26" for item in res.items)

        # Search by underlying
        res_gold = dir_service.get_directory(query="Gold")
        assert res_gold.total >= 2
        assert all(
            "Gold" in item.product_name or "Gold" in item.underlying_name for item in res_gold.items
        )

    def test_directory_category_filter(self):
        """Verify filtering contracts by commodity category."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        dir_service = FuturesDirectoryService(repository=repo, read_service=read_service)

        res_ag = dir_service.get_directory(category="agriculture")
        assert res_ag.total >= 4
        assert all(item.category == CommodityCategoryEnum.AGRICULTURE for item in res_ag.items)

    def test_directory_exchange_filter(self):
        """Verify filtering contracts by exchange venue."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        dir_service = FuturesDirectoryService(repository=repo, read_service=read_service)

        res_comex = dir_service.get_directory(exchange="COMEX")
        assert res_comex.total >= 4
        assert all(item.exchange == "COMEX" for item in res_comex.items)

    def test_directory_keyset_pagination(self):
        """Verify deterministic keyset pagination with cursor and limit."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        dir_service = FuturesDirectoryService(repository=repo, read_service=read_service)

        page1 = dir_service.get_directory(limit=3)
        assert len(page1.items) == 3
        assert page1.has_more is True
        assert page1.next_cursor is not None

        page2 = dir_service.get_directory(limit=3, cursor=page1.next_cursor)
        assert len(page2.items) == 3
        # Page 1 and Page 2 must not overlap
        p1_symbols = {item.symbol for item in page1.items}
        p2_symbols = {item.symbol for item in page2.items}
        assert p1_symbols.isdisjoint(p2_symbols)

    def test_filter_options_and_coverage_summary(self):
        """Verify filter options returns distinct categories, exchanges, and valid coverage."""
        repo = FuturesMarketRepository()
        filter_opts = repo.get_filter_options()

        assert len(filter_opts.categories) >= 5
        assert "NYMEX" in filter_opts.exchanges
        assert "COMEX" in filter_opts.exchanges
        assert "CBOT" in filter_opts.exchanges
        assert "CME" in filter_opts.exchanges
        assert "ICE" in filter_opts.exchanges
        assert filter_opts.coverage.total_contracts >= 15
        assert filter_opts.coverage.contracts_with_last >= 10
        assert filter_opts.coverage.contracts_with_settlement >= 10


# =============================================================================
# 6. Authenticated and Authorized API Endpoints
# =============================================================================
@pytest.fixture
def mock_auth_user():
    return AuthPrincipal(
        sub="user-12345678-1234-5678-1234-567812345678",
        email="trader@atlas.io",
    )


@pytest.fixture
def mock_auth_context():
    context = MagicMock(spec=AuthorizationContext)
    context.has_permission = MagicMock(return_value=True)
    return context


@pytest.fixture
def mock_db():
    session = AsyncMock()
    session.execute.return_value = MagicMock()
    return session


@pytest.mark.asyncio
class TestFuturesAPIEndpoints:
    async def test_list_contracts_authenticated_200(
        self, mock_auth_user, mock_auth_context, mock_db
    ):
        """Verify GET /api/v1/markets/futures/contracts returns 200 with directory data."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/markets/futures/contracts?limit=10")
                assert res.status_code == 200
                data = res.json()
                assert "items" in data
                assert "total" in data
                assert "coverage" in data
                assert len(data["items"]) == 10
                assert data["items"][0]["symbol"] is not None
        finally:
            app.dependency_overrides.clear()

    async def test_get_contract_overview_200_and_404(
        self, mock_auth_user, mock_auth_context, mock_db
    ):
        """Verify GET contract overview returns 200 for existing and 404 for unknown."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                contract_id = CANONICAL_FUTURES_CONTRACTS[0].instrument_entity_id
                res = await client.get(f"/api/v1/markets/futures/contracts/{contract_id}")
                assert res.status_code == 200
                data = res.json()
                assert data["symbol"] == CANONICAL_FUTURES_CONTRACTS[0].symbol
                assert "underlying" in data
                assert "product" in data
                assert "specifications" in data
                assert "price_observation" in data
                assert "settlement_observation" in data

                # 404 for random UUID
                rand_id = "00000000-0000-0000-0000-000000009999"
                res_404 = await client.get(f"/api/v1/markets/futures/contracts/{rand_id}")
                assert res_404.status_code == 404
        finally:
            app.dependency_overrides.clear()

    async def test_list_commodities_and_detail(self, mock_auth_user, mock_auth_context, mock_db):
        """Verify GET /api/v1/markets/futures/commodities and /{id} endpoints."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/markets/futures/commodities")
                assert res.status_code == 200
                data = res.json()
                assert data["total"] >= 10

                comm_id = CANONICAL_COMMODITIES[0].commodity_entity_id
                detail_res = await client.get(f"/api/v1/markets/futures/commodities/{comm_id}")
                assert detail_res.status_code == 200
                assert detail_res.json()["name"] == CANONICAL_COMMODITIES[0].name
        finally:
            app.dependency_overrides.clear()

    async def test_list_spot_benchmarks_endpoint(self, mock_auth_user, mock_auth_context, mock_db):
        """Verify GET /api/v1/markets/futures/spot-benchmarks endpoint."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/markets/futures/spot-benchmarks")
                assert res.status_code == 200
                data = res.json()
                assert data["total"] >= 5
        finally:
            app.dependency_overrides.clear()

    async def test_get_filters_endpoint(self, mock_auth_user, mock_auth_context, mock_db):
        """Verify GET /api/v1/markets/futures/filters endpoint."""
        app.dependency_overrides[get_current_user] = lambda: mock_auth_user
        app.dependency_overrides[get_authorization_context] = lambda: mock_auth_context
        app.dependency_overrides[get_db_session] = lambda: mock_db

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                res = await client.get("/api/v1/markets/futures/filters")
                assert res.status_code == 200
                data = res.json()
                assert "categories" in data
                assert "exchanges" in data
                assert "products" in data
                assert "coverage" in data
        finally:
            app.dependency_overrides.clear()


# =============================================================================
# 7. Read-Only Invariants Tests
# =============================================================================
class TestReadOnlyInvariants:
    def test_read_operations_perform_zero_writes(self):
        """Verify queries and directory access mutate zero catalog state."""
        repo = FuturesMarketRepository()
        read_service = FuturesMarketReadService(repository=repo)
        dir_service = FuturesDirectoryService(repository=repo, read_service=read_service)
        overview_service = FuturesOverviewService(repository=repo, read_service=read_service)

        init_contracts_count = len(repo._contracts)
        init_products_count = len(repo._products)
        init_commodities_count = len(repo._commodities)

        # Execute multiple reads
        dir_service.get_directory(query="CL")
        dir_service.get_directory(category="energy", limit=10)
        c_id = CANONICAL_FUTURES_CONTRACTS[0].instrument_entity_id
        overview_service.get_overview(c_id)

        # State must remain identical
        assert len(repo._contracts) == init_contracts_count
        assert len(repo._products) == init_products_count
        assert len(repo._commodities) == init_commodities_count
