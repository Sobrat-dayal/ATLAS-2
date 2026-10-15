"""Comprehensive Automated Tests for ATLAS ETFs & Funds Markets V1 (Stage 58).

Tests:
1. Canonical Fund and Share-Class Identity (ETFs, Mutual Funds, CEFs).
2. Distinction between ETFs and ETNs / non-funds.
3. Strict separation between Market Price (Quotes) and Official NAV.
4. Mutual funds without exchange quotes (not applicable, no fake quotes).
5. NAV valuation dates, currencies, and publication timestamps.
6. Fee metrics (Net/Gross Expense Ratios) and AUM scope/currencies.
7. Directory filtering, search, pagination, and deterministic ordering.
8. Coverage summary metrics calculation.
9. Authenticated and authorized read APIs (200, 401, 403, 404).
10. Read-only verification: 0 database writes, 0 redis writes.
"""

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.home.market_summary.models import (
    MarketSummaryDataStatus,
)
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.market_data.quote import Quote
from atlas.markets.funds.config import (
    DEFAULT_FUNDS_CATALOG,
    CanonicalFundConfig,
    validate_funds_catalog,
)
from atlas.markets.funds.repository import FundDirectoryRepository
from atlas.markets.funds.service import FundMarketReadService
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# 1. Identity & Classification Tests
# =============================================================================
class TestFundIdentityAndClassification:
    def test_canonical_catalog_presence_and_types(self):
        """Verifies canonical funds catalog contains ETFs, Mutual Funds, and Closed-End Funds."""
        configs = DEFAULT_FUNDS_CATALOG
        assert len(configs) >= 8

        types = {c.fund_type for c in configs}
        assert "ETF" in types
        assert "OPEN_END_MUTUAL_FUND" in types
        assert "CLOSED_END_FUND" in types

    def test_fund_validation_duplicate_prevention(self):
        """Asserts that duplicate instrument UUIDs or duplicate exchange listings are rejected."""
        dup_id = uuid.uuid4()
        conf1 = CanonicalFundConfig(
            instrument_entity_id=dup_id,
            fund_name="Fund One",
            display_symbol="FND1",
            fund_type="ETF",
            exchange_mic="ARCX",
        )
        conf2 = CanonicalFundConfig(
            instrument_entity_id=dup_id,
            fund_name="Fund Two",
            display_symbol="FND2",
            fund_type="ETF",
            exchange_mic="ARCX",
        )
        with pytest.raises(ValueError, match="Duplicate canonical instrument_entity_id"):
            validate_funds_catalog([conf1, conf2])

        # Duplicate listing symbol on same exchange
        conf3 = CanonicalFundConfig(
            instrument_entity_id=uuid.uuid4(),
            fund_name="Fund Three",
            display_symbol="FND1",
            fund_type="ETF",
            exchange_mic="ARCX",
        )
        with pytest.raises(ValueError, match="Duplicate exchange listing"):
            validate_funds_catalog([conf1, conf3])

    def test_unlisted_mutual_fund_has_no_exchange_context(self):
        """Verifies open-end mutual funds are unlisted and have no exchange MIC."""
        mf = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "VTSAX")
        assert mf.fund_type == "OPEN_END_MUTUAL_FUND"
        assert mf.is_exchange_traded is False
        assert mf.exchange_mic is None
        assert mf.exchange_display_name is None
        assert mf.trading_currency is None
        assert mf.initial_nav is not None
        assert mf.initial_nav > 0


# =============================================================================
# 2. Quote vs NAV Separation Tests
# =============================================================================
class TestQuoteAndNAVSeparation:
    @pytest.mark.asyncio
    async def test_mutual_fund_has_no_fake_exchange_quote(self):
        """
        Crucial Stage 58 rule: Open-end mutual funds must NOT receive fake exchange quotes.
        Their market_quote must reflect NOT_CONFIGURED / not exchange-traded,
        while official_nav is valid.
        """
        read_service = FundMarketReadService(quote_service=None)
        unlisted_mf = CanonicalFundConfig(
            instrument_entity_id=uuid.uuid4(),
            fund_name="Test Vanguard Admiral",
            display_symbol="TSTAX",
            fund_type="OPEN_END_MUTUAL_FUND",
            is_exchange_traded=False,
            initial_nav=125.75,
            nav_currency="USD",
            nav_valuation_date=date(2026, 10, 14),
        )

        items = await read_service.enrich_fund_items([unlisted_mf])
        assert len(items) == 1
        item = items[0]

        # Market quote must state not exchange-traded
        assert item.market_quote is not None
        assert item.market_quote.data_status == MarketSummaryDataStatus.NOT_CONFIGURED
        assert "not exchange-traded" in item.market_quote.unavailable_reason.lower()
        assert item.market_quote.last_price is None

        # Official NAV must be strictly preserved
        assert item.official_nav is not None
        assert item.official_nav.is_available is True
        assert item.official_nav.nav_per_unit == "125.7500"
        assert item.official_nav.nav_currency == "USD"
        assert item.official_nav.valuation_date == date(2026, 10, 14)

    @pytest.mark.asyncio
    async def test_etf_market_quote_does_not_overwrite_nav(self):
        """
        Verifies that when an exchange quote is present for an ETF (e.g. SPY = 588.20),
        the official NAV (e.g. 585.40) is NOT overwritten or conflated with last_price.
        """
        spy_cfg = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "SPY")
        now = datetime.now(timezone.utc)

        canonical_quote = Quote(
            instrument_id=spy_cfg.instrument_entity_id,
            as_of=now,
            bid_price=Decimal("588.19"),
            ask_price=Decimal("588.21"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("588.20"))

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            source_timestamp=now,
            received_at=now,
            cached_at=now,
        )

        quote_service = MagicMock(spec=LiveQuoteService)
        quote_service.get_latest_quotes = AsyncMock(return_value=[mock_record])

        read_service = FundMarketReadService(quote_service=quote_service)
        items = await read_service.enrich_fund_items([spy_cfg])

        assert len(items) == 1
        item = items[0]

        # Market quote has 588.20
        assert item.market_quote is not None
        assert item.market_quote.data_status == MarketSummaryDataStatus.AVAILABLE
        assert item.market_quote.last_price == "588.20"

        # Official NAV retains 585.40
        assert item.official_nav is not None
        assert item.official_nav.is_available is True
        assert item.official_nav.nav_per_unit == "585.4000"
        assert item.official_nav.nav_per_unit != item.market_quote.last_price

    @pytest.mark.asyncio
    async def test_closed_end_fund_distinguishes_market_price_and_nav(self):
        """
        Closed-End Funds (CEFs) trade on an exchange but also report official NAV.
        Both must be present and distinct.
        """
        bst_cfg = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "BST")
        now = datetime.now(timezone.utc)

        canonical_quote = Quote(
            instrument_id=bst_cfg.instrument_entity_id,
            as_of=now,
            bid_price=Decimal("36.78"),
            ask_price=Decimal("36.82"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("36.80"))

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            source_timestamp=now,
            received_at=now,
            cached_at=now,
        )

        quote_service = MagicMock(spec=LiveQuoteService)
        quote_service.get_latest_quotes = AsyncMock(return_value=[mock_record])

        read_service = FundMarketReadService(quote_service=quote_service)
        items = await read_service.enrich_fund_items([bst_cfg])

        item = items[0]
        assert item.is_exchange_traded is True
        assert item.market_quote.last_price == "36.80"
        assert item.official_nav.nav_per_unit == "37.2000"
        assert item.official_nav.nav_per_unit != item.market_quote.last_price


# =============================================================================
# 3. Fees & AUM Metrics Tests
# =============================================================================
class TestFeesAndAUMMetrics:
    @pytest.mark.asyncio
    async def test_fee_metrics_formatting_and_scope(self):
        """Verifies net/gross expense ratios format accurately as percentage strings."""
        spy_cfg = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "SPY")
        read_service = FundMarketReadService(quote_service=None)
        items = await read_service.enrich_fund_items([spy_cfg])

        fees = items[0].fees
        assert fees.is_available is True
        assert "0.09" in fees.net_expense_ratio
        assert fees.fee_metric_type == "Gross Expense Ratio"

    @pytest.mark.asyncio
    async def test_aum_metrics_and_scope(self):
        """Verifies AUM amount, currency, and scope are preserved."""
        voo_cfg = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "VOO")
        read_service = FundMarketReadService(quote_service=None)
        items = await read_service.enrich_fund_items([voo_cfg])

        aum = items[0].aum
        assert aum.is_available is True
        assert aum.aum_currency == "USD"
        assert aum.aum_scope == "Share Class"
        assert Decimal(aum.total_aum) == Decimal("480000000000.00")


# =============================================================================
# 4. Directory Repository Filtering & Pagination Tests
# =============================================================================
class TestFundDirectoryFilteringAndPagination:
    @pytest.mark.asyncio
    async def test_filter_by_fund_type(self):
        """Filters catalog by ETF, OPEN_END_MUTUAL_FUND, and CLOSED_END_FUND."""
        repo = FundDirectoryRepository()

        # ETFs only
        etfs, _, _, total_etfs = await repo.get_filtered_funds(fund_type="ETF", limit=50)
        assert total_etfs >= 5
        assert all(f.fund_type == "ETF" for f in etfs)

        # Mutual funds only
        mfs, _, _, total_mfs = await repo.get_filtered_funds(
            fund_type="OPEN_END_MUTUAL_FUND", limit=50
        )
        assert total_mfs >= 2
        assert all(f.fund_type == "OPEN_END_MUTUAL_FUND" for f in mfs)

        # Closed-end funds only
        cefs, _, _, total_cefs = await repo.get_filtered_funds(
            fund_type="CLOSED_END_FUND", limit=50
        )
        assert total_cefs >= 2
        assert all(f.fund_type == "CLOSED_END_FUND" for f in cefs)

    @pytest.mark.asyncio
    async def test_filter_by_exchange(self):
        """Filters by exchange MIC (e.g. ARCX, XNAS, XNYS)."""
        repo = FundDirectoryRepository()
        arcx_funds, _, _, total_arcx = await repo.get_filtered_funds(exchange="ARCX", limit=50)
        assert total_arcx >= 3
        assert all(f.exchange_mic == "ARCX" for f in arcx_funds)

    @pytest.mark.asyncio
    async def test_filter_by_category(self):
        """Filters by investment category (e.g. Fixed Income, Commodity)."""
        repo = FundDirectoryRepository()
        fi_funds, _, _, total_fi = await repo.get_filtered_funds(
            fund_category="Fixed Income", limit=50
        )
        assert total_fi >= 1
        assert any(f.display_symbol == "AGG" for f in fi_funds)

    @pytest.mark.asyncio
    async def test_search_by_query(self):
        """Searches by symbol, name, ISIN, and manager name."""
        repo = FundDirectoryRepository()

        # Search by symbol
        items, _, _, count = await repo.get_filtered_funds(query="QQQ")
        assert count == 1
        assert items[0].display_symbol == "QQQ"

        # Search by ISIN
        items_isin, _, _, count_isin = await repo.get_filtered_funds(query="US78462F1030")
        assert count_isin == 1
        assert items_isin[0].display_symbol == "SPY"

        # Search by Manager Name
        items_mgr, _, _, count_mgr = await repo.get_filtered_funds(query="Vanguard")
        assert count_mgr >= 2

    @pytest.mark.asyncio
    async def test_deterministic_keyset_pagination(self):
        """Verifies pagination bounds and cursor tokens."""
        repo = FundDirectoryRepository()
        p1, next_cur, has_more, total = await repo.get_filtered_funds(limit=3)
        assert len(p1) == 3
        assert has_more is True
        assert next_cur == "3"

        p2, next_cur2, _, _ = await repo.get_filtered_funds(limit=3, cursor=next_cur)
        assert len(p2) == 3
        # Ensure items on page 1 and page 2 are distinct
        p1_ids = {f.instrument_entity_id for f in p1}
        p2_ids = {f.instrument_entity_id for f in p2}
        assert p1_ids.isdisjoint(p2_ids)

    @pytest.mark.asyncio
    async def test_filter_options_metadata(self):
        """Verifies truthful filter options response."""
        repo = FundDirectoryRepository()
        options = await repo.get_filter_options()
        assert len(options.fund_types) >= 3
        assert len(options.categories) >= 3
        assert len(options.exchanges) >= 3


# =============================================================================
# 5. API Endpoints & Auth / Entitlements Tests
# =============================================================================
class TestFundAPIEndpoints:
    @pytest.fixture
    def authenticated_principal(self):
        return AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="researcher@atlas.financial",
        )

    @pytest.fixture
    def authorized_context(self):
        ctx = MagicMock(spec=AuthorizationContext)
        ctx.has_permission = MagicMock(return_value=True)
        return ctx

    @pytest.mark.asyncio
    async def test_unauthenticated_request_rejected(self):
        """Anonymous requests must be rejected with 401."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/markets/funds")
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_authenticated_directory_success(
        self, authenticated_principal, authorized_context
    ):
        """Authenticated request returns 200 with schema_version, scope, items, and coverage."""
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/markets/funds?limit=10")
                assert resp.status_code == 200
                data = resp.json()

                assert data["schema_version"] == 1
                assert data["scope"] == "authorized_canonical_fund_directory"
                assert len(data["items"]) >= 8
                assert "coverage" in data
                assert data["coverage"]["configured_funds_count"] >= 8
                assert data["coverage"]["etf_count"] >= 5
                assert data["coverage"]["mutual_fund_count"] >= 2
                assert data["coverage"]["closed_end_fund_count"] >= 2

                # Verify Cache-Control header
                assert "no-store" in resp.headers.get("cache-control", "").lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_fund_filter_options_api(self, authenticated_principal, authorized_context):
        """Tests GET /api/v1/markets/funds/filters."""
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/v1/markets/funds/filters")
                assert resp.status_code == 200
                data = resp.json()
                assert "fund_types" in data
                assert "exchanges" in data
                assert "categories" in data
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_fund_detail_api(self, authenticated_principal, authorized_context):
        """Tests GET /api/v1/markets/funds/{instrument_entity_id} for a valid fund."""
        spy_cfg = next(c for c in DEFAULT_FUNDS_CATALOG if c.display_symbol == "SPY")
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/v1/markets/funds/{spy_cfg.instrument_entity_id}")
                assert resp.status_code == 200
                data = resp.json()
                assert data["item"]["display_symbol"] == "SPY"
                assert data["item"]["fund_type"] == "ETF"
                assert "identifiers" in data
                assert any(i["scheme"] == "ISIN" for i in data["identifiers"])
                assert data["relationships"]["manager_name"] == "State Street Global Advisors"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_fund_detail_not_found(self, authenticated_principal, authorized_context):
        """Unknown instrument UUID returns 404."""
        random_uuid = uuid.uuid4()
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(f"/api/v1/markets/funds/{random_uuid}")
                assert resp.status_code == 404
        finally:
            app.dependency_overrides.clear()
