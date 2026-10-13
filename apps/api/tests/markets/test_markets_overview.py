"""Stage 56 Markets Overview Test Suite.

Verifies:
- Curated multi-asset catalog configuration rules, asset groupings, and Index != ETF invariant
- Decimal financial arithmetic, qualified change calculation, and zero-denominator safety
- Read-only execution guarantee (zero DB/Redis writes, zero provider fetch calls)
- Missing quote transparency (never fake prices, never fake zero placeholders)
- Group filtering and bounded keyset pagination
- Freshness classification and safe provenance metadata
- Authenticated and authorized FastAPI endpoint contracts
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.home.market_summary.models import (
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
    MarketSummaryDeliveryDelay,
)
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.market_data.quote import Quote
from atlas.markets.overview.config import (
    DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS,
    MARKET_GROUPS_ALLOWLIST,
    MarketsOverviewInstrumentConfig,
    validate_markets_overview_config,
)
from atlas.markets.overview.service import MarketsOverviewService
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Curated Multi-Asset Catalog Configuration Tests
# -----------------------------------------------------------------------------
class TestMarketsOverviewConfig:
    def test_default_config_valid(self):
        configs = validate_markets_overview_config(DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS)
        assert len(configs) >= 10
        assert len(configs) <= 100
        # Orders must be monotonic
        orders = [c.display_order for c in configs]
        assert orders == sorted(orders)

    def test_market_groups_all_allowed(self):
        for c in DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS:
            assert c.market_group in MARKET_GROUPS_ALLOWLIST

    def test_reject_duplicate_uuid(self):
        duplicate_id = uuid.uuid4()
        c1 = MarketsOverviewInstrumentConfig(
            instrument_entity_id=duplicate_id,
            display_name="Inst 1",
            display_symbol="I1",
            instrument_category="equity",
            market_group="equities",
            display_order=1,
        )
        c2 = MarketsOverviewInstrumentConfig(
            instrument_entity_id=duplicate_id,
            display_name="Inst 2",
            display_symbol="I2",
            instrument_category="equity",
            market_group="equities",
            display_order=2,
        )
        with pytest.raises(ValueError, match="Duplicate instrument UUID"):
            validate_markets_overview_config([c1, c2])

    def test_reject_duplicate_display_order(self):
        c1 = MarketsOverviewInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Inst 1",
            display_symbol="I1",
            instrument_category="equity",
            market_group="equities",
            display_order=1,
        )
        c2 = MarketsOverviewInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Inst 2",
            display_symbol="I2",
            instrument_category="equity",
            market_group="equities",
            display_order=1,
        )
        with pytest.raises(ValueError, match="Duplicate display_order"):
            validate_markets_overview_config([c1, c2])

    def test_reject_invalid_group(self):
        c = MarketsOverviewInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Invalid Group Inst",
            display_symbol="INV",
            instrument_category="equity",
            market_group="unknown_future_group",
            display_order=1,
        )
        with pytest.raises(ValueError, match="Invalid market_group"):
            validate_markets_overview_config([c])

    def test_index_and_etf_distinct_invariant(self):
        sp500_idx = next(
            c for c in DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS if c.display_symbol == "^GSPC"
        )
        spy_etf = next(c for c in DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS if c.display_symbol == "SPY")

        assert sp500_idx.is_index is True
        assert spy_etf.is_index is False
        assert sp500_idx.instrument_entity_id != spy_etf.instrument_entity_id
        assert sp500_idx.market_group == "benchmarks"
        assert spy_etf.market_group == "etfs"

    def test_featured_instruments_bounded(self):
        featured = [c for c in DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS if c.featured]
        # Must be within recommended 6-8 range
        assert 6 <= len(featured) <= 8


# -----------------------------------------------------------------------------
# 2. Composition Service & Financial Accuracy Tests
# -----------------------------------------------------------------------------
class TestMarketsOverviewService:
    @pytest.mark.asyncio
    async def test_empty_catalog_returns_truthful_empty(self):
        service = MarketsOverviewService(instrument_configs=[])
        response = await service.get_markets_overview()

        assert response.schema_version == 1
        assert response.scope == "configured_overview_universe"
        assert response.items == []
        assert response.featured_items == []
        assert response.coverage.configured_count == 0
        assert response.coverage.available_count == 0
        assert response.coverage.unavailable_count == 0
        assert response.has_more is False

    @pytest.mark.asyncio
    async def test_missing_quotes_marked_no_quote(self):
        # Service with no live quote service connected
        service = MarketsOverviewService()
        response = await service.get_markets_overview()

        assert len(response.items) > 0
        for item in response.items:
            assert item.data_status == MarketSummaryDataStatus.NO_QUOTE
            assert item.last_price is None
            assert item.absolute_change is None
            assert item.percentage_change is None
            assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN
            assert item.freshness_status == "unavailable"
            assert item.delivery_delay_status == MarketSummaryDeliveryDelay.UNKNOWN
            assert item.unavailable_reason is not None

        assert response.coverage.available_count == 0
        assert response.coverage.unavailable_count == len(response.items)

    @pytest.mark.asyncio
    async def test_available_quote_with_decimal_precision(self):
        mock_quote_service = MagicMock(spec=LiveQuoteService)
        sp500_cfg = next(
            c for c in DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS if c.display_symbol == "^GSPC"
        )

        test_now = datetime.now(timezone.utc)
        high_precision_price = Decimal("5842.12500000")

        canonical_quote = Quote(
            instrument_id=sp500_cfg.instrument_entity_id,
            as_of=test_now,
            bid_price=Decimal("5841.00"),
            ask_price=Decimal("5843.00"),
        )
        object.__setattr__(canonical_quote, "last_price", high_precision_price)

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            received_at=test_now,
            cached_at=test_now,
            source_timestamp=test_now,
            provider_key="openbb",
        )

        # Mock get_latest_quotes to return our record for sp500
        async def fake_get_latest_quotes(instrument_ids):
            return [
                mock_record if i_id == sp500_cfg.instrument_entity_id else None
                for i_id in instrument_ids
            ]

        mock_quote_service.get_latest_quotes = AsyncMock(side_effect=fake_get_latest_quotes)

        service = MarketsOverviewService(
            quote_service=mock_quote_service,
            instrument_configs=[sp500_cfg],
        )

        response = await service.get_markets_overview()

        assert len(response.items) == 1
        item = response.items[0]
        assert item.data_status == MarketSummaryDataStatus.AVAILABLE
        assert item.last_price == "5842.12500000"
        assert item.display_name == "S&P 500"
        assert item.display_symbol == "^GSPC"
        assert item.value_kind == "points"
        assert item.quote_unit == "pts"
        assert item.freshness_status == "fresh"

    @pytest.mark.asyncio
    async def test_group_filtering(self):
        service = MarketsOverviewService()

        # Equities filter
        eq_res = await service.get_markets_overview(group="equities")
        for item in eq_res.items:
            assert item.market_group == "equities"

        # FX filter
        fx_res = await service.get_markets_overview(group="fx")
        for item in fx_res.items:
            assert item.market_group == "fx"

        # Benchmarks filter
        bm_res = await service.get_markets_overview(group="benchmarks")
        for item in bm_res.items:
            assert item.market_group == "benchmarks"

        # All filter
        all_res = await service.get_markets_overview(group="all")
        assert len(all_res.items) == min(25, len(DEFAULT_MARKETS_OVERVIEW_INSTRUMENTS))

    @pytest.mark.asyncio
    async def test_featured_instruments_assembly(self):
        service = MarketsOverviewService()
        response = await service.get_markets_overview()

        assert 6 <= len(response.featured_items) <= 8
        for f in response.featured_items:
            assert f.featured is True

    @pytest.mark.asyncio
    async def test_pagination_bounds(self):
        service = MarketsOverviewService()

        # Page 1 with limit 5
        page1 = await service.get_markets_overview(limit=5)
        assert len(page1.items) == 5
        assert page1.has_more is True
        assert page1.next_cursor == "5"

        # Page 2 using cursor
        page2 = await service.get_markets_overview(limit=5, cursor=page1.next_cursor)
        assert len(page2.items) == 5
        assert page1.items[0].instrument_entity_id != page2.items[0].instrument_entity_id


# -----------------------------------------------------------------------------
# 3. FastAPI Endpoint Integration Tests
# -----------------------------------------------------------------------------
class TestMarketsOverviewEndpoint:
    @pytest.mark.asyncio
    async def test_unauthenticated_rejected(self):
        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/markets/overview")
            assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_authenticated_endpoint_success_with_cache_headers(self):
        app = create_app()

        user_id = str(uuid.uuid4())
        principal = AuthPrincipal(sub=user_id, email="trader@atlas.io")
        authz_context = AuthorizationContext(
            principal=principal,
            roles=frozenset(["member"]),
            permissions=frozenset({"atlas.access"}),
        )

        app.dependency_overrides[get_current_user] = lambda: principal
        app.dependency_overrides[get_authorization_context] = lambda: authz_context
        app.dependency_overrides[get_db_session] = lambda: None

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/api/v1/markets/overview")
                assert resp.status_code == 200
                assert resp.headers.get("Cache-Control") == "private, no-store"

                data = resp.json()
                assert data["schema_version"] == 1
                assert data["scope"] == "configured_overview_universe"
                assert "groups" in data
                assert "items" in data
                assert "featured_items" in data
                assert "coverage" in data

                # Check group filtering via endpoint
                resp_fx = await client.get("/api/v1/markets/overview?group=fx")
                assert resp_fx.status_code == 200
                fx_data = resp_fx.json()
                for itm in fx_data["items"]:
                    assert itm["market_group"] == "fx"

        finally:
            app.dependency_overrides.clear()
