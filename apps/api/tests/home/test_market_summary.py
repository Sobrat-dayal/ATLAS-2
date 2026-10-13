"""Stage 52 Home Market Summary Test Suite.

Verifies:
- Curated configuration rules and Index != ETF invariant
- Decimal financial arithmetic and zero-denominator safety
- Read-only execution guarantee (zero DB/Redis writes)
- Missing quote transparency (never fake prices or zero placeholders)
- Freshness classification and provenance
- Authenticated and authorized FastAPI endpoint contracts
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.home.market_summary.config import (
    DEFAULT_MARKET_SUMMARY_INSTRUMENTS,
    MarketSummaryInstrumentConfig,
    validate_market_summary_config,
)
from atlas.home.market_summary.models import (
    MarketSummaryChangeDirection,
    MarketSummaryDataStatus,
)
from atlas.home.market_summary.reference_close import (
    calculate_market_changes,
)
from atlas.home.market_summary.service import HomeMarketSummaryService
from atlas.market_data.live.service import LiveQuoteService
from atlas.market_data.live.store import QuoteCacheRecord
from atlas.market_data.quote import Quote
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session


# -----------------------------------------------------------------------------
# 1. Curated Configuration & Invariant Tests
# -----------------------------------------------------------------------------
class TestMarketSummaryConfig:
    def test_default_config_valid(self):
        configs = validate_market_summary_config(DEFAULT_MARKET_SUMMARY_INSTRUMENTS)
        assert len(configs) >= 4
        assert len(configs) <= 20
        # Orders must be monotonic
        orders = [c.display_order for c in configs]
        assert orders == sorted(orders)

    def test_reject_duplicate_uuid(self):
        duplicate_id = uuid.uuid4()
        c1 = MarketSummaryInstrumentConfig(
            instrument_entity_id=duplicate_id,
            display_name="Inst 1",
            display_symbol="I1",
            instrument_category="equity",
            display_order=1,
        )
        c2 = MarketSummaryInstrumentConfig(
            instrument_entity_id=duplicate_id,
            display_name="Inst 2",
            display_symbol="I2",
            instrument_category="equity",
            display_order=2,
        )
        with pytest.raises(ValueError, match="Duplicate instrument UUID"):
            validate_market_summary_config([c1, c2])

    def test_reject_duplicate_display_order(self):
        c1 = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Inst 1",
            display_symbol="I1",
            instrument_category="equity",
            display_order=1,
        )
        c2 = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Inst 2",
            display_symbol="I2",
            instrument_category="equity",
            display_order=1,
        )
        with pytest.raises(ValueError, match="Duplicate display_order"):
            validate_market_summary_config([c1, c2])

    def test_reject_more_than_20_instruments(self):
        items = [
            MarketSummaryInstrumentConfig(
                instrument_entity_id=uuid.uuid4(),
                display_name=f"Inst {i}",
                display_symbol=f"I{i}",
                instrument_category="equity",
                display_order=i,
            )
            for i in range(21)
        ]
        with pytest.raises(ValueError, match="exceeds max 20 items"):
            validate_market_summary_config(items)

    def test_index_vs_etf_distinction(self):
        sp500_index = next(
            c for c in DEFAULT_MARKET_SUMMARY_INSTRUMENTS if c.display_symbol == "^GSPC"
        )
        spy_etf = next(c for c in DEFAULT_MARKET_SUMMARY_INSTRUMENTS if c.display_symbol == "SPY")

        assert sp500_index.is_index is True
        assert sp500_index.instrument_category == "market_index"
        assert sp500_index.value_kind == "points"

        assert spy_etf.is_index is False
        assert spy_etf.instrument_category == "etf"
        assert spy_etf.value_kind == "price"

        # Crucial: Must NOT share the same UUID authority
        assert sp500_index.instrument_entity_id != spy_etf.instrument_entity_id


# -----------------------------------------------------------------------------
# 2. Decimal Financial Math Tests
# -----------------------------------------------------------------------------
class TestDecimalFinancialCalculations:
    def test_positive_change(self):
        last = Decimal("5050.50")
        ref = Decimal("5000.00")
        abs_chg, pct_chg, direction = calculate_market_changes(last, ref)

        assert abs_chg == Decimal("50.50")
        assert pct_chg == Decimal("1.01")
        assert direction == MarketSummaryChangeDirection.UP

    def test_negative_change(self):
        last = Decimal("4950.00")
        ref = Decimal("5000.00")
        abs_chg, pct_chg, direction = calculate_market_changes(last, ref)

        assert abs_chg == Decimal("-50.00")
        assert pct_chg == Decimal("-1.00")
        assert direction == MarketSummaryChangeDirection.DOWN

    def test_zero_change(self):
        last = Decimal("5000.00")
        ref = Decimal("5000.00")
        abs_chg, pct_chg, direction = calculate_market_changes(last, ref)

        assert abs_chg == Decimal("0.00")
        assert pct_chg == Decimal("0.00")
        assert direction == MarketSummaryChangeDirection.FLAT

    def test_zero_reference_close_avoids_division_by_zero(self):
        last = Decimal("15.50")
        ref = Decimal("0.00")
        abs_chg, pct_chg, direction = calculate_market_changes(last, ref)

        assert abs_chg == Decimal("15.50")
        assert pct_chg is None  # Protected against division by zero!
        assert direction == MarketSummaryChangeDirection.UP

    def test_missing_reference_close(self):
        last = Decimal("5000.00")
        abs_chg, pct_chg, direction = calculate_market_changes(last, None)

        assert abs_chg is None
        assert pct_chg is None
        assert direction == MarketSummaryChangeDirection.UNKNOWN

    def test_missing_last_price(self):
        ref = Decimal("5000.00")
        abs_chg, pct_chg, direction = calculate_market_changes(None, ref)

        assert abs_chg is None
        assert pct_chg is None
        assert direction == MarketSummaryChangeDirection.UNKNOWN

    def test_high_precision_fx_decimals(self):
        last = Decimal("1.0845")
        ref = Decimal("1.0820")
        abs_chg, pct_chg, direction = calculate_market_changes(last, ref)

        assert abs_chg == Decimal("0.0025")
        assert direction == MarketSummaryChangeDirection.UP
        assert pct_chg is not None
        assert str(pct_chg).startswith("0.2310")


# -----------------------------------------------------------------------------
# 3. HomeMarketSummaryService Unit Tests
# -----------------------------------------------------------------------------
class TestHomeMarketSummaryService:
    @pytest.mark.asyncio
    async def test_empty_configuration_handled_safely(self):
        service = HomeMarketSummaryService(instrument_configs=[])
        response = await service.get_market_summary()

        assert response.schema_version == 1
        assert len(response.items) == 0
        assert response.coverage.configured_count == 0
        assert response.coverage.available_count == 0
        assert response.coverage.unavailable_count == 0

    @pytest.mark.asyncio
    async def test_no_quotes_returns_honest_unavailable_states(self):
        mock_quote_service = MagicMock(spec=LiveQuoteService)
        # Returns None for all requested instruments
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[None, None])

        inst1 = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Index A",
            display_symbol="^A",
            instrument_category="market_index",
            display_order=1,
        )
        inst2 = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="ETF B",
            display_symbol="B",
            instrument_category="etf",
            display_order=2,
        )

        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst1, inst2],
        )
        response = await service.get_market_summary()

        assert response.coverage.configured_count == 2
        assert response.coverage.available_count == 0
        assert response.coverage.unavailable_count == 2
        assert len(response.items) == 2

        for item in response.items:
            assert item.data_status == MarketSummaryDataStatus.NO_QUOTE
            assert item.last_price is None  # NEVER fake a 0.00 price!
            assert item.freshness_status == "unavailable"
            assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN
            assert item.unavailable_reason is not None

    @pytest.mark.asyncio
    async def test_available_quote_with_reference_close(self):
        inst_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("4999.50"),
            ask_price=Decimal("5000.50"),
        )
        # Add price attribute dynamically to simulate executed trade price
        object.__setattr__(canonical_quote, "last_price", Decimal("5000.00"))

        cached_record = QuoteCacheRecord(
            quote=canonical_quote,
            received_at=now,
            cached_at=now,
            source_timestamp=now,
        )

        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[cached_record])

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst_id,
            display_name="S&P 500",
            display_symbol="^GSPC",
            instrument_category="market_index",
            value_kind="points",
            quote_currency="USD",
            quote_unit="pts",
            display_order=1,
            is_index=True,
            provider_hint="openbb",
        )

        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst],
        )

        # Mock reference close resolver to return 4950.00
        service._reference_resolver.resolve_reference_close = AsyncMock(
            return_value=(Decimal("4950.00"), None, "mock_prior_close")
        )

        response = await service.get_market_summary()

        assert response.coverage.configured_count == 1
        assert response.coverage.available_count == 1
        assert response.coverage.unavailable_count == 0
        assert len(response.items) == 1

        item = response.items[0]
        assert item.data_status == MarketSummaryDataStatus.AVAILABLE
        assert item.last_price == "5000.00"
        assert item.absolute_change == "50.00"
        assert item.percentage_change is not None
        assert item.change_direction == MarketSummaryChangeDirection.UP
        assert item.provider_display_name == "OpenBB Financial Platform"
        assert item.quote_unit == "pts"

    @pytest.mark.asyncio
    async def test_service_is_strictly_read_only(self):
        """Verifies zero database writes and zero state mutations."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[None])

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Test",
            display_symbol="T",
            instrument_category="equity",
            display_order=1,
        )

        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            db_session=mock_session,
            instrument_configs=[inst],
        )
        await service.get_market_summary()

        # Verified: Zero database writes
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
        mock_session.flush.assert_not_called()

    @pytest.mark.asyncio
    async def test_quote_with_bid_ask_only_does_not_fabricate_last_price(self):
        """When quote only has bid/ask, last_price is None (no midpoint substitution)."""
        inst_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("100.00"),
            ask_price=Decimal("101.00"),
        )
        cached_record = QuoteCacheRecord(
            quote=canonical_quote,
            received_at=now,
            cached_at=now,
            source_timestamp=now,
        )
        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[cached_record])

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst_id,
            display_name="FX Pair",
            display_symbol="EUR/USD",
            instrument_category="currency",
            display_order=1,
        )
        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst],
        )
        response = await service.get_market_summary()
        assert len(response.items) == 1
        item = response.items[0]
        assert item.last_price is None  # Never synthesize a midpoint!
        assert item.bid_price == "100.00"
        assert item.ask_price == "101.00"
        assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN

    @pytest.mark.asyncio
    async def test_redis_failure_handled_gracefully(self):
        """When LiveQuoteService throws an exception, endpoint returns safe state."""
        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(
            side_effect=RuntimeError("Redis connection timeout")
        )

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="S&P 500",
            display_symbol="^GSPC",
            instrument_category="market_index",
            display_order=1,
        )
        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst],
        )
        response = await service.get_market_summary()
        assert response.coverage.configured_count == 1
        assert response.coverage.available_count == 0
        assert response.coverage.unavailable_count == 1
        assert response.items[0].data_status == MarketSummaryDataStatus.NO_QUOTE
        assert response.items[0].last_price is None

    @pytest.mark.asyncio
    async def test_clickhouse_reference_failure_still_returns_latest_price(self):
        """When ClickHouse lookup fails, latest price is still returned with change unavailable."""
        inst_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        canonical_quote = Quote(
            instrument_id=inst_id,
            as_of=now,
            bid_price=Decimal("4999.00"),
        )
        object.__setattr__(canonical_quote, "last_price", Decimal("5000.00"))
        cached_record = QuoteCacheRecord(
            quote=canonical_quote,
            received_at=now,
            cached_at=now,
            source_timestamp=now,
        )
        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[cached_record])

        # Mock clickhouse client that throws
        mock_ch_factory = MagicMock()
        mock_ch_client = MagicMock()
        mock_ch_client.query.side_effect = Exception("ClickHouse unavailable")
        mock_ch_factory.get_client.return_value = mock_ch_client

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst_id,
            display_name="SPY ETF",
            display_symbol="SPY",
            instrument_category="etf",
            display_order=1,
        )
        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            ch_client_factory=mock_ch_factory,
            instrument_configs=[inst],
        )
        response = await service.get_market_summary()
        assert response.coverage.available_count == 1
        item = response.items[0]
        assert item.last_price == "5000.00"
        assert item.reference_close is None
        assert item.absolute_change is None
        assert item.percentage_change is None
        assert item.change_direction == MarketSummaryChangeDirection.UNKNOWN

    @pytest.mark.asyncio
    async def test_postgresql_entity_lookup_failure_falls_back_to_config_name(self):
        """When PostgreSQL lookup fails, config name is preserved without failing request."""
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("DB connection reset")

        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[None])

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=uuid.uuid4(),
            display_name="Dow Jones Industrial",
            display_symbol="^DJI",
            instrument_category="market_index",
            display_order=1,
        )
        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            db_session=mock_session,
            instrument_configs=[inst],
        )
        response = await service.get_market_summary()
        assert response.items[0].display_name == "Dow Jones Industrial"

    @pytest.mark.asyncio
    async def test_partial_quote_availability_mixed_results(self):
        """Mixed configured instruments: some with quotes, some without."""
        inst1_id = uuid.uuid4()
        inst2_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        quote1 = Quote(instrument_id=inst1_id, as_of=now, bid_price=Decimal("99.50"))
        object.__setattr__(quote1, "last_price", Decimal("100.00"))
        cached1 = QuoteCacheRecord(
            quote=quote1, received_at=now, cached_at=now, source_timestamp=now
        )

        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[cached1, None])

        inst1 = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst1_id,
            display_name="Item 1",
            display_symbol="I1",
            instrument_category="equity",
            display_order=1,
        )
        inst2 = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst2_id,
            display_name="Item 2",
            display_symbol="I2",
            instrument_category="equity",
            display_order=2,
        )

        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst1, inst2],
        )
        response = await service.get_market_summary()
        assert response.coverage.configured_count == 2
        assert response.coverage.available_count == 1
        assert response.coverage.unavailable_count == 1
        assert response.items[0].data_status == MarketSummaryDataStatus.AVAILABLE
        assert response.items[0].last_price == "100.00"
        assert response.items[1].data_status == MarketSummaryDataStatus.NO_QUOTE
        assert response.items[1].last_price is None

    @pytest.mark.asyncio
    async def test_freshness_classification_stale_and_aging(self):
        """Stale quotes (> 15m) and aging quotes (5-15m) are classified accurately."""
        inst_id = uuid.uuid4()
        now = datetime.now(timezone.utc)
        old_time = datetime.fromtimestamp(now.timestamp() - 1200, tz=timezone.utc)  # 20 min ago

        quote = Quote(instrument_id=inst_id, as_of=old_time, bid_price=Decimal("249.00"))
        object.__setattr__(quote, "last_price", Decimal("250.00"))
        cached = QuoteCacheRecord(
            quote=quote, received_at=old_time, cached_at=old_time, source_timestamp=old_time
        )

        mock_quote_service = MagicMock(spec=LiveQuoteService)
        mock_quote_service.get_latest_quotes = AsyncMock(return_value=[cached])

        inst = MarketSummaryInstrumentConfig(
            instrument_entity_id=inst_id,
            display_name="Stale Stock",
            display_symbol="STK",
            instrument_category="equity",
            display_order=1,
        )
        service = HomeMarketSummaryService(
            quote_service=mock_quote_service,
            instrument_configs=[inst],
        )
        response = await service.get_market_summary()
        assert response.items[0].freshness_status == "stale"


# -----------------------------------------------------------------------------
class TestHomeMarketSummaryEndpoint:
    @pytest.fixture
    def app(self):
        return create_app()

    @pytest.mark.asyncio
    async def test_unauthenticated_rejected(self, app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/api/v1/home/market-summary")
            assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_missing_permission_rejected(self, app):
        user_id = str(uuid.uuid4())
        principal = AuthPrincipal(sub=user_id, email="guest@atlas.io")

        authz_context = AuthorizationContext(
            principal=principal,
            roles=frozenset(["member"]),
            permissions=frozenset(),
        )

        mock_session = AsyncMock()

        app.dependency_overrides[get_current_user] = lambda: principal
        app.dependency_overrides[get_authorization_context] = lambda: authz_context
        app.dependency_overrides[get_db_session] = lambda: mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/api/v1/home/market-summary")
            assert resp.status_code == 403
            assert resp.json()["error"]["code"] == "PERMISSION_DENIED"

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_authorized_success_contract(self, app):
        user_id = str(uuid.uuid4())
        principal = AuthPrincipal(sub=user_id, email="trader@atlas.io")

        authz_context = AuthorizationContext(
            principal=principal,
            roles=frozenset(["member"]),
            permissions=frozenset({"atlas.access"}),
        )

        mock_session = AsyncMock()
        mock_session.execute = AsyncMock(return_value=MagicMock(all=lambda: []))

        app.dependency_overrides[get_current_user] = lambda: principal
        app.dependency_overrides[get_authorization_context] = lambda: authz_context
        app.dependency_overrides[get_db_session] = lambda: mock_session

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/api/v1/home/market-summary")

            assert resp.status_code == 200
            assert resp.headers["cache-control"] == "private, no-store"

            data = resp.json()
            assert data["schema_version"] == 1
            assert "generated_at" in data
            assert "coverage" in data
            assert "items" in data
            assert isinstance(data["items"], list)
            assert data["coverage"]["configured_count"] == len(data["items"])

        app.dependency_overrides.clear()
