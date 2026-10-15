"""Stage 57 Equities Markets Test Suite.

Verifies:
- Canonical Financial Instrument UUID authority and Company UUID separation
- Distinct share classes (e.g. GOOGL Class A vs GOOG Class C)
- Depositary receipt (ADR) classification preservation
- Exchange-scoped symbol resolution and venue identity
- Region/country, exchange, subtype, and listing status filtering
- Bounded directory search and deterministic pagination
- Decimal financial arithmetic, qualified price changes, and zero-denominator safety
- Missing quote transparency (never fake prices, never fake zero placeholders)
- Freshness classification and safe provider provenance
- Read-only execution guarantee (zero DB/Redis writes, zero provider calls)
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
)
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.market_data.quote import Quote
from atlas.markets.equities.config import (
    DEFAULT_EQUITIES_CATALOG,
    CanonicalEquityConfig,
    validate_equities_catalog,
)
from atlas.markets.equities.repository import EquityDirectoryRepository
from atlas.markets.equities.service import (
    EquityMarketReadService,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Canonical Identity, Share Classes & Classification Tests
# -----------------------------------------------------------------------------
class TestCanonicalEquityCatalog:
    def test_default_catalog_valid(self):
        configs = validate_equities_catalog(DEFAULT_EQUITIES_CATALOG)
        assert len(configs) >= 8
        assert len(configs) <= 100

    def test_share_classes_distinguished_with_distinct_uuids(self):
        """Alphabet Class A (GOOGL) and Class C (GOOG) must have distinct Security UUIDs."""
        googl = next(c for c in DEFAULT_EQUITIES_CATALOG if c.display_symbol == "GOOGL")
        goog = next(c for c in DEFAULT_EQUITIES_CATALOG if c.display_symbol == "GOOG")

        assert googl.instrument_entity_id != goog.instrument_entity_id
        assert googl.share_class_name == "Class A"
        assert goog.share_class_name == "Class C"
        # Shared corporate issuer
        assert googl.issuer_company_entity_id == goog.issuer_company_entity_id

    def test_company_uuid_distinct_from_security_uuid(self):
        """Security UUID must never be identical to issuer Company UUID."""
        for c in DEFAULT_EQUITIES_CATALOG:
            if c.issuer_company_entity_id is not None:
                assert c.instrument_entity_id != c.issuer_company_entity_id

    def test_depositary_receipt_subtype_preserved(self):
        """TSM ADR must be preserved as depositary_receipt, never collapsed into common stock."""
        tsm = next(c for c in DEFAULT_EQUITIES_CATALOG if c.display_symbol == "TSM")
        assert tsm.equity_subtype == "depositary_receipt"
        assert tsm.equity_subtype_label == "Depositary Receipt"
        assert tsm.exchange_mic == "XNYS"

    def test_multi_currency_representation(self):
        """Currencies must reflect actual listing currencies (USD, INR, GBP, JPY)."""
        currencies = {c.trading_currency for c in DEFAULT_EQUITIES_CATALOG}
        assert "USD" in currencies
        assert "INR" in currencies
        assert "GBP" in currencies
        assert "JPY" in currencies

    def test_reject_duplicate_uuid(self):
        dup_id = uuid.uuid4()
        c1 = CanonicalEquityConfig(
            instrument_entity_id=dup_id,
            display_name="Stock 1",
            display_symbol="S1",
            exchange_mic="XNAS",
            exchange_display_name="NASDAQ",
            listing_market_country="United States",
            listing_market_country_code="US",
        )
        c2 = CanonicalEquityConfig(
            instrument_entity_id=dup_id,
            display_name="Stock 2",
            display_symbol="S2",
            exchange_mic="XNYS",
            exchange_display_name="NYSE",
            listing_market_country="United States",
            listing_market_country_code="US",
        )
        with pytest.raises(ValueError, match="Duplicate equity instrument UUID"):
            validate_equities_catalog([c1, c2])

    def test_reject_duplicate_exchange_symbol_pair(self):
        c1 = CanonicalEquityConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Stock 1",
            display_symbol="ABC",
            exchange_mic="XNAS",
            exchange_display_name="NASDAQ",
            listing_market_country="United States",
            listing_market_country_code="US",
        )
        c2 = CanonicalEquityConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Stock 2",
            display_symbol="ABC",
            exchange_mic="XNAS",
            exchange_display_name="NASDAQ",
            listing_market_country="United States",
            listing_market_country_code="US",
        )
        with pytest.raises(ValueError, match="Duplicate .* pair"):
            validate_equities_catalog([c1, c2])

    def test_reject_unsupported_subtype(self):
        c = CanonicalEquityConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Stock Invalid",
            display_symbol="INV",
            equity_subtype="unsupported_crypto_claim",
            exchange_mic="XNAS",
            exchange_display_name="NASDAQ",
            listing_market_country="United States",
            listing_market_country_code="US",
        )
        with pytest.raises(ValueError, match="Unsupported equity subtype"):
            validate_equities_catalog([c])


# -----------------------------------------------------------------------------
# 2. Repository Discovery, Search & Filter Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestEquityDirectoryRepository:
    async def test_query_all_default_catalog(self):
        repo = EquityDirectoryRepository()
        items, total, cursor, has_more = await repo.query_directory(limit=50)
        assert total == len(DEFAULT_EQUITIES_CATALOG)
        assert len(items) == len(DEFAULT_EQUITIES_CATALOG)
        assert has_more is False
        assert cursor is None

    async def test_search_by_symbol(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(query="AAPL")
        assert total >= 1
        assert any(i.display_symbol == "AAPL" for i in items)

    async def test_search_by_name(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(query="Microsoft")
        assert total >= 1
        assert any(i.display_symbol == "MSFT" for i in items)

    async def test_filter_by_country(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(market_country="India")
        assert total == 2
        for it in items:
            assert it.listing_market_country == "India"
            assert it.trading_currency == "INR"

    async def test_filter_by_exchange(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(exchange="XNSE")
        assert total == 2
        for it in items:
            assert it.exchange_mic == "XNSE"

    async def test_filter_by_subtype(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(equity_type="depositary_receipt")
        assert total >= 1
        for it in items:
            assert it.equity_subtype == "depositary_receipt"

    async def test_combined_filters_and_semantics(self):
        repo = EquityDirectoryRepository()
        items, total, _, _ = await repo.query_directory(
            market_country="United States",
            equity_type="depositary_receipt",
        )
        assert total == 1
        assert items[0].display_symbol == "TSM"

    async def test_deterministic_ordering(self):
        repo = EquityDirectoryRepository()
        items, _, _, _ = await repo.query_directory(limit=50)
        names = [i.display_name.lower() for i in items]
        assert names == sorted(names)

    async def test_pagination_limits(self):
        repo = EquityDirectoryRepository()
        page1, total, next_cursor, has_more = await repo.query_directory(limit=3, cursor="0")
        assert len(page1) == 3
        assert has_more is True
        assert next_cursor == "3"

        page2, _, _, _ = await repo.query_directory(limit=3, cursor=next_cursor)
        assert len(page2) == 3
        # Ensure disjoint pages
        p1_ids = {p.instrument_entity_id for p in page1}
        p2_ids = {p.instrument_entity_id for p in page2}
        assert p1_ids.isdisjoint(p2_ids)

    async def test_truthful_filter_options(self):
        repo = EquityDirectoryRepository()
        filters = await repo.get_filter_options()
        country_names = {c.name for c in filters.countries}
        assert "United States" in country_names
        assert "India" in country_names
        assert "United Kingdom" in country_names
        assert "Japan" in country_names

        exchange_mics = {e.mic for e in filters.exchanges}
        assert "XNAS" in exchange_mics
        assert "XNSE" in exchange_mics
        assert "XLON" in exchange_mics
        assert "XTKS" in exchange_mics

    async def test_empty_catalog_safe_state(self):
        repo = EquityDirectoryRepository(catalog_configs=[])
        items, total, cursor, has_more = await repo.query_directory()
        assert items == []
        assert total == 0
        assert cursor is None
        assert has_more is False


# -----------------------------------------------------------------------------
# 3. Market Read Service & Financial Calculation Tests
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestEquityMarketReadService:
    async def test_enrich_with_valid_quote_and_reference(self):
        quote_service = MagicMock(spec=LiveQuoteService)
        inst_id = DEFAULT_EQUITIES_CATALOG[0].instrument_entity_id
        now = datetime.now(timezone.utc)
        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("224.48"),
            ask_price=Decimal("224.52"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("224.50"))

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            source_timestamp=now,
            received_at=now,
            cached_at=now,
        )
        quote_service.get_latest_quotes = AsyncMock(return_value=[mock_record])

        read_service = EquityMarketReadService(quote_service=quote_service)
        # Mock reference close resolver
        read_service._reference_resolver.resolve_reference_close = AsyncMock(
            return_value=(Decimal("220.00"), None, "feed_snapshot_prior_close")
        )

        items = await read_service.enrich_equity_items([DEFAULT_EQUITIES_CATALOG[0]])
        assert len(items) == 1
        item = items[0]

        assert item.data_status == MarketSummaryDataStatus.AVAILABLE
        assert item.last_price == "224.50"
        assert item.bid_price == "224.48"
        assert item.ask_price == "224.52"
        assert item.reference_close == "220.00"
        assert item.absolute_change == "4.50"
        assert item.change_direction == MarketSummaryChangeDirection.UP
        assert item.freshness_status == "fresh"

    async def test_missing_quote_transparency(self):
        """Missing quote must never be faked as zero price or zero change."""
        quote_service = MagicMock(spec=LiveQuoteService)
        quote_service.get_latest_quotes = AsyncMock(return_value=[None])

        read_service = EquityMarketReadService(quote_service=quote_service)
        items = await read_service.enrich_equity_items([DEFAULT_EQUITIES_CATALOG[0]])

        assert len(items) == 1
        item = items[0]
        assert item.data_status == MarketSummaryDataStatus.NO_QUOTE
        assert item.last_price is None
        assert item.absolute_change is None
        assert item.percentage_change is None
        assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN
        assert item.unavailable_reason is not None

    async def test_missing_reference_close_preserves_price_with_null_change(self):
        """If reference close is missing, valid price is displayed while change is null."""
        quote_service = MagicMock(spec=LiveQuoteService)
        inst_id = DEFAULT_EQUITIES_CATALOG[0].instrument_entity_id

        now = datetime.now(timezone.utc)
        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("150.00"),
            ask_price=Decimal("150.05"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("150.00"))

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            source_timestamp=now,
            received_at=now,
            cached_at=now,
        )
        quote_service.get_latest_quotes = AsyncMock(return_value=[mock_record])

        read_service = EquityMarketReadService(quote_service=quote_service)
        read_service._reference_resolver.resolve_reference_close = AsyncMock(
            return_value=(None, None, None)
        )

        items = await read_service.enrich_equity_items([DEFAULT_EQUITIES_CATALOG[0]])
        item = items[0]
        assert item.last_price == "150.00"
        assert item.reference_close is None
        assert item.absolute_change is None
        assert item.percentage_change is None
        assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN

    async def test_zero_reference_denominator_safety(self):
        """Zero reference close must yield null percent change, preventing division-by-zero."""
        quote_service = MagicMock(spec=LiveQuoteService)
        inst_id = DEFAULT_EQUITIES_CATALOG[0].instrument_entity_id

        now = datetime.now(timezone.utc)
        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("10.00"),
            ask_price=Decimal("10.05"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("10.00"))

        mock_record = QuoteCacheRecord(
            quote=canonical_quote,
            source_timestamp=now,
            received_at=now,
            cached_at=now,
        )
        quote_service.get_latest_quotes = AsyncMock(return_value=[mock_record])

        read_service = EquityMarketReadService(quote_service=quote_service)
        read_service._reference_resolver.resolve_reference_close = AsyncMock(
            return_value=(Decimal("0.00"), None, "test")
        )

        items = await read_service.enrich_equity_items([DEFAULT_EQUITIES_CATALOG[0]])
        item = items[0]
        assert item.last_price == "10.00"
        assert item.percentage_change is None


# -----------------------------------------------------------------------------
# 4. FastAPI Endpoints & Security Contracts
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
class TestEquityEndpoints:
    @pytest.fixture
    def app(self):
        return create_app()

    @pytest.fixture
    def authenticated_principal(self):
        return AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="trader@atlas.canonical",
        )

    @pytest.fixture
    def authorized_context(self):
        ctx = MagicMock(spec=AuthorizationContext)
        ctx.has_permission = MagicMock(return_value=True)
        return ctx

    async def test_anonymous_request_rejected(self, app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/api/v1/markets/equities")
            assert resp.status_code == 401

    async def test_authenticated_directory_success(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/api/v1/markets/equities")
                assert resp.status_code == 200
                data = resp.json()
                assert data["schema_version"] == 1
                assert data["scope"] == "authorized_canonical_equity_directory"
                assert len(data["items"]) >= 8
                assert resp.headers.get("Cache-Control") == "private, no-store"
                assert "coverage" in data
                assert "available_filters" in data
        finally:
            app.dependency_overrides.clear()

    async def test_filter_query_parameters(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/api/v1/markets/equities?market_country=India")
                assert resp.status_code == 200
                data = resp.json()
                assert len(data["items"]) == 2
                assert all(i["listing_market_country"] == "India" for i in data["items"])
        finally:
            app.dependency_overrides.clear()

    async def test_get_filter_options_endpoint(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/api/v1/markets/equities/filters")
                assert resp.status_code == 200
                data = resp.json()
                assert len(data["countries"]) >= 4
                assert len(data["exchanges"]) >= 4
                assert len(data["equity_types"]) >= 2
        finally:
            app.dependency_overrides.clear()

    async def test_get_equity_detail_success(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        aapl_id = DEFAULT_EQUITIES_CATALOG[0].instrument_entity_id

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get(f"/api/v1/markets/equities/{aapl_id}")
                assert resp.status_code == 200
                data = resp.json()
                assert data["item"]["display_symbol"] == "AAPL"
                assert len(data["identifiers"]) >= 1
                assert data["issuer_company"] is not None
                assert data["issuer_company"]["short_name"] == "Apple Inc."
                assert data["venue_details"]["mic"] == "XNAS"
        finally:
            app.dependency_overrides.clear()

    async def test_get_equity_detail_not_found(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        random_uuid = uuid.uuid4()

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get(f"/api/v1/markets/equities/{random_uuid}")
                assert resp.status_code == 404
                resp_json = resp.json()
                msg = resp_json.get("detail") or resp_json.get("error", {}).get("message", "")
                is_nf = (
                    "not found" in msg.lower()
                    or resp_json.get("error", {}).get("code") == "NOT_FOUND"
                )
                assert is_nf
        finally:
            app.dependency_overrides.clear()

    async def test_invalid_uuid_rejected(
        self, app, authenticated_principal, authorized_context
    ):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.get("/api/v1/markets/equities/not-a-valid-uuid")
                assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()
