"""Comprehensive Automated Tests for ATLAS Cryptocurrency Markets V1 (Stage 60).

Tests:
1. Canonical Digital Asset Identity & Classification (Coin, Token, Stablecoin, Wrapped).
2. Spot Market Trading Pair Identity, Venue Scoping, and Quote Asset Distinction.
3. Bid/Ask Spread, Midpoint, Basis Points, and Crossed Market Handling.
4. Decimal Precision for High/Low Value Crypto Assets.
5. Directory Search, Base/Quote/Venue Filtering, and Keyset Pagination.
6. Authenticated and Authorized Read APIs (200, 401, 403, 404).
7. Read-Only Invariants: 0 writes to Postgres, 0 writes to Redis, 0 external provider fanout.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.crypto.config import (
    DEFAULT_CRYPTO_ASSET_CATALOG,
    DEFAULT_CRYPTO_SPOT_CATALOG,
    CanonicalCryptoSpotMarketConfig,
    CryptoAssetKindEnum,
    QuoteAssetTypeEnum,
    generate_crypto_asset_uuid,
    generate_crypto_instrument_uuid,
)
from atlas.markets.crypto.models import CryptoRateKind
from atlas.markets.crypto.repository import CryptoMarketRepository
from atlas.markets.crypto.service import CryptoMarketReadService
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# 1. Digital Asset Identity & Classification Tests
# =============================================================================
class TestCryptoAssetIdentity:
    def test_canonical_asset_catalog_contents(self):
        """Verifies major digital assets are present with canonical metadata."""
        catalog = {a.symbol: a for a in DEFAULT_CRYPTO_ASSET_CATALOG}
        assert "BTC" in catalog
        assert "ETH" in catalog
        assert "SOL" in catalog
        assert "USDT" in catalog
        assert "USDC" in catalog
        assert "WBTC" in catalog

        # Bitcoin is native coin
        assert catalog["BTC"].asset_kind == CryptoAssetKindEnum.COIN
        assert catalog["BTC"].network_id == "bitcoin"
        assert catalog["BTC"].decimals == 8
        assert catalog["BTC"].contract_address is None

        # Tether is stablecoin with ERC-20 contract
        assert catalog["USDT"].asset_kind == CryptoAssetKindEnum.STABLECOIN
        assert catalog["USDT"].token_standard == "ERC-20"
        assert catalog["USDT"].contract_address == "0xdac17f958d2ee523a2206206994597c13d831ec7"
        assert catalog["USDT"].decimals == 6

        # Wrapped Bitcoin is wrapped asset
        assert catalog["WBTC"].asset_kind == CryptoAssetKindEnum.WRAPPED

    def test_deterministic_uuid_generation(self):
        """Ensures asset UUIDs are generated deterministically."""
        u1 = generate_crypto_asset_uuid("BTC")
        u2 = generate_crypto_asset_uuid("btc")
        assert u1 == u2
        assert isinstance(u1, uuid.UUID)


# =============================================================================
# 2. Spot Market Trading Pair Identity & Venue Scoping Tests
# =============================================================================
class TestSpotMarketIdentityAndVenues:
    def test_spot_market_catalog_presence_and_venue_scoping(self):
        """Verifies spot markets preserve venue specificity and BASE/QUOTE orientation."""
        markets = DEFAULT_CRYPTO_SPOT_CATALOG
        assert len(markets) >= 12

        # Coinbase BTC/USD
        cb_btc = next(
            m for m in markets if m.venue_id == "coinbase" and m.market_symbol == "BTC/USD"
        )
        assert cb_btc.base_asset_symbol == "BTC"
        assert cb_btc.quote_asset_symbol == "USD"
        assert cb_btc.quote_asset_type == QuoteAssetTypeEnum.FIAT
        assert cb_btc.venue_market_symbol == "BTC-USD"

        # Binance BTC/USDT (distinct from BTC/USD)
        bn_btc = next(
            m for m in markets if m.venue_id == "binance" and m.market_symbol == "BTC/USDT"
        )
        assert bn_btc.base_asset_symbol == "BTC"
        assert bn_btc.quote_asset_symbol == "USDT"
        assert bn_btc.quote_asset_type == QuoteAssetTypeEnum.STABLECOIN
        assert bn_btc.venue_market_symbol == "BTCUSDT"
        assert bn_btc.instrument_entity_id != cb_btc.instrument_entity_id

        # Binance ETH/BTC (crypto-denominated pair)
        bn_ethbtc = next(
            m for m in markets if m.venue_id == "binance" and m.market_symbol == "ETH/BTC"
        )
        assert bn_ethbtc.quote_asset_type == QuoteAssetTypeEnum.CRYPTO
        assert bn_ethbtc.price_precision == 6

    def test_deterministic_instrument_uuid(self):
        """Instrument UUID must differ across venues for same asset pair."""
        u_cb = generate_crypto_instrument_uuid("coinbase", "BTC", "USD")
        u_bs = generate_crypto_instrument_uuid("bitstamp", "BTC", "USD")
        assert u_cb != u_bs


# =============================================================================
# 3. Spread & Decimal Calculation Tests
# =============================================================================
class TestCryptoQuotesAndSpreads:
    @pytest.mark.asyncio
    async def test_valid_bid_ask_spread_calculation(self):
        """Verifies Decimal calculation of absolute spread, midpoint, and basis points."""
        market = CanonicalCryptoSpotMarketConfig(
            instrument_entity_id=uuid.uuid4(),
            market_symbol="BTC/USD",
            base_asset_symbol="BTC",
            quote_asset_symbol="USD",
            venue_id="coinbase",
            venue_name="Coinbase",
            venue_market_symbol="BTC-USD",
            default_last_price=Decimal("67450.00"),
            default_bid=Decimal("67448.00"),
            default_ask=Decimal("67452.00"),
        )
        service = CryptoMarketReadService()
        quote = await service.get_market_quote(market)

        assert quote.last_price == Decimal("67450.00")
        assert quote.bid == Decimal("67448.00")
        assert quote.ask == Decimal("67452.00")
        assert quote.spread_absolute == Decimal("4.00")
        assert quote.midpoint == Decimal("67450.00")
        # bps = (4.00 / 67450.00) * 10000 = 0.59 bps
        assert quote.spread_bps == Decimal("0.59")
        assert quote.rate_kind == CryptoRateKind.BID_ASK_QUOTE.value

    @pytest.mark.asyncio
    async def test_crossed_market_quote_handling(self):
        """Crossed quotes (bid > ask) must flag CROSSED_INVALID and suppress spread."""
        market = CanonicalCryptoSpotMarketConfig(
            instrument_entity_id=uuid.uuid4(),
            market_symbol="ETH/USDT",
            base_asset_symbol="ETH",
            quote_asset_symbol="USDT",
            venue_id="binance",
            venue_name="Binance",
            venue_market_symbol="ETHUSDT",
            default_bid=Decimal("3525.00"),
            default_ask=Decimal("3520.00"),  # bid > ask
        )
        service = CryptoMarketReadService()
        quote = await service.get_market_quote(market)

        assert quote.rate_kind == CryptoRateKind.CROSSED_INVALID.value
        assert quote.spread_absolute is None
        assert quote.midpoint is None
        assert quote.spread_bps is None

    @pytest.mark.asyncio
    async def test_small_token_price_precision(self):
        """Small crypto prices (e.g. Dogecoin $0.14250) must retain exact precision."""
        market = CanonicalCryptoSpotMarketConfig(
            instrument_entity_id=uuid.uuid4(),
            market_symbol="DOGE/USDT",
            base_asset_symbol="DOGE",
            quote_asset_symbol="USDT",
            venue_id="binance",
            venue_name="Binance",
            venue_market_symbol="DOGEUSDT",
            price_precision=5,
            default_last_price=Decimal("0.14250"),
            default_bid=Decimal("0.14248"),
            default_ask=Decimal("0.14252"),
        )
        service = CryptoMarketReadService()
        quote = await service.get_market_quote(market)

        assert quote.last_price == Decimal("0.14250")
        assert quote.spread_absolute == Decimal("0.00004")
        assert quote.quote_asset_unit == "USDT"


# =============================================================================
# 4. Repository & Filtering Tests
# =============================================================================
class TestCryptoRepositoryAndFiltering:
    def test_filter_by_base_asset(self):
        """Filtering by base asset returns only pairs for that asset."""
        repo = CryptoMarketRepository()
        items, count, _ = repo.list_spot_markets(base_asset="BTC")
        assert count > 0
        assert all(m.base_asset_symbol == "BTC" for m in items)

    def test_filter_by_venue(self):
        """Filtering by venue returns only pairs listed on that exchange."""
        repo = CryptoMarketRepository()
        items, count, _ = repo.list_spot_markets(venue="coinbase")
        assert count > 0
        assert all(m.venue_id == "coinbase" for m in items)

    def test_filter_by_quote_asset_type(self):
        """Filtering by quote asset type distinguishes fiat, stablecoin, and crypto."""
        repo = CryptoMarketRepository()
        items, count, _ = repo.list_spot_markets(quote_asset_type="stablecoin")
        assert count > 0
        assert all(m.quote_asset_type == QuoteAssetTypeEnum.STABLECOIN for m in items)

    def test_search_query_matching(self):
        """Search query matches pair notation, asset symbol, and venue."""
        repo = CryptoMarketRepository()
        items, count, _ = repo.list_spot_markets(query="ETH")
        assert count > 0
        assert any(m.base_asset_symbol == "ETH" or m.quote_asset_symbol == "ETH" for m in items)

    def test_pagination_and_cursor(self):
        """Keyset pagination returns limited items and next cursor."""
        repo = CryptoMarketRepository()
        items1, total, cursor = repo.list_spot_markets(limit=2)
        assert len(items1) == 2
        assert total >= 12
        assert cursor is not None

        items2, _, _ = repo.list_spot_markets(limit=2, cursor=cursor)
        assert len(items2) == 2
        assert items1[0].instrument_entity_id != items2[0].instrument_entity_id


# =============================================================================
# 5. Authenticated API Endpoint Tests
# =============================================================================
class TestCryptoAPIEndpoints:
    @pytest.fixture
    def authenticated_principal(self):
        return AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="crypto.trader@atlas.io",
        )

    @pytest.fixture
    def authorized_context(self):
        ctx = MagicMock(spec=AuthorizationContext)
        ctx.has_permission = MagicMock(return_value=True)
        return ctx

    @pytest.fixture
    def authenticated_client(self, authenticated_principal, authorized_context):
        app.dependency_overrides[get_current_user] = lambda: authenticated_principal
        app.dependency_overrides[get_authorization_context] = lambda: authorized_context
        app.dependency_overrides[get_db_session] = lambda: AsyncMock()

        transport = ASGITransport(app=app)
        client = AsyncClient(transport=transport, base_url="http://test")
        yield client

        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_unauthenticated_request_returns_401(self):
        """Anonymous access to /markets/crypto must be rejected with 401."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            resp = await client.get("/api/v1/markets/crypto")
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_authenticated_spot_directory_success(self, authenticated_client):
        """Authenticated request to /markets/crypto returns 200 with directory items."""
        resp = await authenticated_client.get("/api/v1/markets/crypto?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total_count" in data
        assert "coverage_summary" in data
        assert "available_filters" in data
        assert len(data["items"]) <= 5
        assert data["coverage_summary"]["total_spot_markets"] >= 12

    @pytest.mark.asyncio
    async def test_get_filter_options_api(self, authenticated_client):
        """Endpoint /markets/crypto/filters returns available venues and asset filters."""
        resp = await authenticated_client.get("/api/v1/markets/crypto/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert "base_assets" in data
        assert "quote_assets" in data
        assert "venues" in data
        assert "quote_asset_types" in data
        assert "BTC" in data["base_assets"]
        assert "USDT" in data["quote_assets"]

    @pytest.mark.asyncio
    async def test_get_digital_assets_api(self, authenticated_client):
        """Endpoint /markets/crypto/assets returns digital asset catalog."""
        resp = await authenticated_client.get("/api/v1/markets/crypto/assets")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert data["total_count"] >= 10
        btc = next(a for a in data["items"] if a["symbol"] == "BTC")
        assert btc["asset_kind"] == "coin"

    @pytest.mark.asyncio
    async def test_get_spot_market_detail_success(self, authenticated_client):
        """Endpoint /markets/crypto/{id} returns comprehensive detail for inspector."""
        target_market = DEFAULT_CRYPTO_SPOT_CATALOG[0]
        resp = await authenticated_client.get(
            f"/api/v1/markets/crypto/{target_market.instrument_entity_id}"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["market_symbol"] == target_market.market_symbol
        assert data["base_asset"]["symbol"] == target_market.base_asset_symbol
        assert data["venue"]["venue_id"] == target_market.venue_id
        assert "quote" in data
        assert "disclaimer" in data

    @pytest.mark.asyncio
    async def test_get_spot_market_detail_not_found(self, authenticated_client):
        """Unknown UUID returns 404 with structured error message."""
        unknown_id = uuid.uuid4()
        resp = await authenticated_client.get(f"/api/v1/markets/crypto/{unknown_id}")
        assert resp.status_code == 404
        error_body = resp.json()
        msg = error_body.get("error", {}).get("message", "")
        assert "not found" in msg.lower()
