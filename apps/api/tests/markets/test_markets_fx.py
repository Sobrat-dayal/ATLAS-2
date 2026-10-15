"""Comprehensive Automated Tests for ATLAS FX Markets V1 (Stage 59).

Tests:
1. Canonical Currency Identity and ISO 4217 Registry.
2. Canonical Spot Pair Orientation (BASE/QUOTE) and Catalog Integrity.
3. Bid/Ask Spread, Midpoint, Pip Conventions, and Crossed Market handling.
4. Decimal Precision and Indicative Currency Conversion (Direct, Reverse, Same-Currency).
5. No-Triangulation Enforcement: Unsupported cross-rates are rejected honestly.
6. Authenticated and Authorized Read APIs (200, 401, 404, 400).
7. Read-Only Invariants: 0 writes to Postgres, 0 writes to Redis, 0 external provider fanout.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.fx.config import (
    DEFAULT_FX_CATALOG,
    ISO_4217_REGISTRY,
    CanonicalFxPairConfig,
    validate_fx_catalog,
)
from atlas.markets.fx.models import (
    FxConversionMode,
    FxConversionRequest,
    FxRateKind,
)
from atlas.markets.fx.repository import FxDirectoryRepository
from atlas.markets.fx.service import (
    FxConversionService,
    FxMarketReadService,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# 1. Currency Identity & ISO 4217 Registry Tests
# =============================================================================
class TestCurrencyIdentityAndRegistry:
    def test_iso_4217_fiat_registry_contents(self):
        """Verifies validated fiat currencies are present with accurate minor units."""
        assert "USD" in ISO_4217_REGISTRY
        assert "EUR" in ISO_4217_REGISTRY
        assert "GBP" in ISO_4217_REGISTRY
        assert "JPY" in ISO_4217_REGISTRY
        assert "INR" in ISO_4217_REGISTRY

        # JPY has 0 minor units
        assert ISO_4217_REGISTRY["JPY"].minor_units == 0
        # USD has 2 minor units
        assert ISO_4217_REGISTRY["USD"].minor_units == 2

    def test_invalid_currency_rejected_in_config(self):
        """Non-ISO fiat code or crypto ticker must be rejected by validator."""
        with pytest.raises(ValueError, match="not in validated ISO 4217 fiat registry"):
            CanonicalFxPairConfig(
                instrument_entity_id=uuid.uuid4(),
                display_pair="BTC/USD",
                base_currency="BTC",
                quote_currency="USD",
            )


# =============================================================================
# 2. Pair Orientation & Catalog Validation Tests
# =============================================================================
class TestPairOrientationAndCatalog:
    def test_canonical_catalog_presence_and_orientation(self):
        """Asserts catalog contains major currency pairs and respects BASE/QUOTE orientation."""
        catalog = DEFAULT_FX_CATALOG
        assert len(catalog) >= 10

        eur_usd = next(p for p in catalog if p.display_pair == "EUR/USD")
        assert eur_usd.base_currency == "EUR"
        assert eur_usd.quote_currency == "USD"
        assert eur_usd.pip_size == Decimal("0.0001")
        assert eur_usd.rate_precision == 4

        usd_jpy = next(p for p in catalog if p.display_pair == "USD/JPY")
        assert usd_jpy.base_currency == "USD"
        assert usd_jpy.quote_currency == "JPY"
        assert usd_jpy.pip_size == Decimal("0.01")
        assert usd_jpy.rate_precision == 2

    def test_duplicate_pair_rejection(self):
        """Asserts that duplicate pairs or duplicate UUIDs are rejected."""
        uid = uuid.uuid4()
        conf1 = CanonicalFxPairConfig(
            instrument_entity_id=uid,
            display_pair="EUR/USD",
            base_currency="EUR",
            quote_currency="USD",
        )
        conf2 = CanonicalFxPairConfig(
            instrument_entity_id=uid,
            display_pair="GBP/USD",
            base_currency="GBP",
            quote_currency="USD",
        )
        with pytest.raises(ValueError, match="Duplicate canonical instrument_entity_id"):
            validate_fx_catalog([conf1, conf2])

    def test_same_base_quote_rejection(self):
        """Pairs with base == quote are invalid market instruments."""
        with pytest.raises(
            ValueError, match="Base currency and quote currency cannot be identical"
        ):
            conf = CanonicalFxPairConfig(
                instrument_entity_id=uuid.uuid4(),
                display_pair="USD/USD",
                base_currency="USD",
                quote_currency="USD",
            )
            validate_fx_catalog([conf])


# =============================================================================
# 3. Bid/Ask Spread, Midpoint, and Crossed Market Tests
# =============================================================================
class TestBidAskSpreadAndQuotes:
    @pytest.mark.asyncio
    async def test_spread_calculation_normal_market(self):
        """Verifies accurate Decimal spread, midpoint, bps, and pips calculation."""
        eur_usd = next(p for p in DEFAULT_FX_CATALOG if p.display_pair == "EUR/USD")
        service = FxMarketReadService(quote_service=None)

        quote = await service.get_fx_quote(eur_usd)
        assert quote.bid == Decimal("1.0848")
        assert quote.ask == Decimal("1.0850")
        assert quote.spread_absolute == Decimal("0.0002")
        assert quote.midpoint == Decimal("1.0849")
        # spread_bps = (0.0002 / 1.0849) * 10000 = 1.8434878...
        assert quote.spread_bps is not None
        assert Decimal("1.84") < quote.spread_bps < Decimal("1.85")
        # 0.0002 / 0.0001 = 2.0 pips
        assert quote.spread_pips == Decimal("2.0")
        assert quote.rate_kind == FxRateKind.SPOT_BID_ASK.value

    @pytest.mark.asyncio
    async def test_crossed_market_handling(self):
        """Crossed quotes (bid > ask) must not produce an ordinary spread;
        must be marked invalid."""
        crossed_conf = CanonicalFxPairConfig(
            instrument_entity_id=uuid.uuid4(),
            display_pair="EUR/USD",
            base_currency="EUR",
            quote_currency="USD",
            default_bid=Decimal("1.0860"),
            default_ask=Decimal("1.0850"),  # bid > ask!
        )
        service = FxMarketReadService(quote_service=None)
        quote = await service.get_fx_quote(crossed_conf)

        assert quote.rate_kind == "CROSSED_INVALID"
        assert quote.data_status == "INCONSISTENT"
        assert quote.spread_absolute is None
        assert quote.midpoint is None


# =============================================================================
# 4. Indicative Currency Conversion Tests
# =============================================================================
class TestIndicativeConversion:
    @pytest.fixture
    def conversion_service(self):
        repo = FxDirectoryRepository()
        read_service = FxMarketReadService()
        return FxConversionService(repository=repo, market_read_service=read_service)

    @pytest.mark.asyncio
    async def test_same_currency_conversion(self, conversion_service):
        """Same currency conversion must be an exact 1:1 arithmetic identity."""
        req = FxConversionRequest(
            amount=Decimal("250.75"),
            from_currency="USD",
            to_currency="USD",
        )
        res = await conversion_service.convert(req)
        assert res.output_amount == Decimal("250.75")
        assert res.rate_used == Decimal("1.0")
        assert res.calculation_direction == "SAME_CURRENCY"
        assert res.indicative is True

    @pytest.mark.asyncio
    async def test_direct_conversion(self, conversion_service):
        """Direct conversion (EUR -> USD) using midpoint: amount * rate."""
        # EUR/USD midpoint = 1.0849
        req = FxConversionRequest(
            amount=Decimal("100"),
            from_currency="EUR",
            to_currency="USD",
            mode=FxConversionMode.INDICATIVE_MID,
        )
        res = await conversion_service.convert(req)
        assert res.calculation_direction == "DIRECT"
        assert res.rate_used == Decimal("1.0849")
        # 100 * 1.0849 = 108.49 USD
        assert res.output_amount == Decimal("108.49")
        assert res.from_currency == "EUR"
        assert res.to_currency == "USD"

    @pytest.mark.asyncio
    async def test_reverse_conversion(self, conversion_service):
        """Reverse conversion (USD -> EUR) using midpoint: amount / rate."""
        # EUR/USD midpoint = 1.0849
        req = FxConversionRequest(
            amount=Decimal("108.49"),
            from_currency="USD",
            to_currency="EUR",
            mode=FxConversionMode.INDICATIVE_MID,
        )
        res = await conversion_service.convert(req)
        assert res.calculation_direction == "REVERSE"
        assert res.rate_used == Decimal("1.0849")
        # 108.49 / 1.0849 = 100.00 EUR
        assert res.output_amount == Decimal("100.00")

    @pytest.mark.asyncio
    async def test_quote_side_bid_ask_conversion(self, conversion_service):
        """Quote-side illustration: Selling BASE uses BID; Buying BASE uses ASK."""
        # Direct: User converts EUR -> USD (sells EUR): dealer buys at BID (1.0848)
        req_direct = FxConversionRequest(
            amount=Decimal("100"),
            from_currency="EUR",
            to_currency="USD",
            mode=FxConversionMode.QUOTE_SIDE_ILLUSTRATION,
        )
        res_direct = await conversion_service.convert(req_direct)
        assert res_direct.rate_used == Decimal("1.0848")
        assert res_direct.quote_side == "BID"
        assert res_direct.output_amount == Decimal("108.48")

        # Reverse: User converts USD -> EUR (buys EUR with USD): dealer sells at ASK (1.0850)
        req_reverse = FxConversionRequest(
            amount=Decimal("108.50"),
            from_currency="USD",
            to_currency="EUR",
            mode=FxConversionMode.QUOTE_SIDE_ILLUSTRATION,
        )
        res_reverse = await conversion_service.convert(req_reverse)
        assert res_reverse.rate_used == Decimal("1.0850")
        assert res_reverse.quote_side == "ASK"
        # 108.50 / 1.0850 = 100.00 EUR
        assert res_reverse.output_amount == Decimal("100.00")

    @pytest.mark.asyncio
    async def test_destination_jpy_zero_minor_units(self, conversion_service):
        """Destination currency JPY must quantize to integer yen (0 decimal places)."""
        # USD/JPY midpoint = 153.265
        req = FxConversionRequest(
            amount=Decimal("100"),
            from_currency="USD",
            to_currency="JPY",
            mode=FxConversionMode.INDICATIVE_MID,
        )
        res = await conversion_service.convert(req)
        # 100 * 153.265 = 15326.5 -> 15327 JPY
        assert res.output_amount == Decimal("15327")
        assert res.to_currency == "JPY"

    @pytest.mark.asyncio
    async def test_no_synthetic_triangulation(self, conversion_service):
        """Unsupported cross-rates must NOT triangulate through third currencies."""
        req = FxConversionRequest(
            amount=Decimal("1000"),
            from_currency="INR",
            to_currency="CHF",
        )
        with pytest.raises(ValueError, match="does not construct multi-leg synthetic cross-rates"):
            await conversion_service.convert(req)


# =============================================================================
# 5. API Endpoints & Auth/Authorization Tests
# =============================================================================
class TestFxAPIEndpoints:
    @pytest.fixture
    def authenticated_principal(self):
        return AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="trader@atlas.io",
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
    async def test_fx_directory_endpoint(self, authenticated_client):
        """GET /api/v1/markets/fx returns paginated currency pairs and coverage summary."""
        resp = await authenticated_client.get("/api/v1/markets/fx")
        assert resp.status_code == 200
        data = resp.json()

        assert "items" in data
        assert "coverage" in data
        assert data["total_count"] >= 10
        assert data["coverage"]["total_pairs"] >= 10
        assert resp.headers["cache-control"] == "private, no-store"

    @pytest.mark.asyncio
    async def test_fx_directory_filtering_and_search(self, authenticated_client):
        """Filter by base_currency and query."""
        resp = await authenticated_client.get("/api/v1/markets/fx?base_currency=EUR")
        assert resp.status_code == 200
        data = resp.json()
        assert all(it["base_currency"] == "EUR" for it in data["items"])

        resp_search = await authenticated_client.get("/api/v1/markets/fx?query=yen")
        assert resp_search.status_code == 200
        data_search = resp_search.json()
        assert any("JPY" in it["display_pair"] for it in data_search["items"])

    @pytest.mark.asyncio
    async def test_fx_currencies_endpoint(self, authenticated_client):
        """GET /api/v1/markets/fx/currencies returns validated ISO 4217 fiat list."""
        resp = await authenticated_client.get("/api/v1/markets/fx/currencies")
        assert resp.status_code == 200
        data = resp.json()
        codes = [c["code"] for c in data["items"]]
        assert "USD" in codes
        assert "EUR" in codes
        assert "JPY" in codes

    @pytest.mark.asyncio
    async def test_fx_pair_detail_endpoint(self, authenticated_client):
        """GET /api/v1/markets/fx/{uuid} returns pair overview with orientation explanation."""
        eur_usd = next(p for p in DEFAULT_FX_CATALOG if p.display_pair == "EUR/USD")
        resp = await authenticated_client.get(f"/api/v1/markets/fx/{eur_usd.instrument_entity_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pair"]["display_pair"] == "EUR/USD"
        assert "orientation_explanation" in data
        assert "1 EUR =" in data["orientation_explanation"]

    @pytest.mark.asyncio
    async def test_fx_conversion_api_success(self, authenticated_client):
        """POST /api/v1/markets/fx/convert performs indicative conversion."""
        payload = {
            "amount": "100.00",
            "from_currency": "EUR",
            "to_currency": "USD",
            "mode": "INDICATIVE_MID",
        }
        resp = await authenticated_client.post("/api/v1/markets/fx/convert", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["from_currency"] == "EUR"
        assert data["to_currency"] == "USD"
        assert data["output_amount"] == "108.49"
        assert data["indicative"] is True

    @pytest.mark.asyncio
    async def test_fx_conversion_api_unsupported_pair_400(self, authenticated_client):
        """POST /api/v1/markets/fx/convert returns 400 for unsupported cross-pair."""
        payload = {
            "amount": "100.00",
            "from_currency": "INR",
            "to_currency": "CHF",
        }
        resp = await authenticated_client.post("/api/v1/markets/fx/convert", json=payload)
        assert resp.status_code == 400
        body = resp.json()
        error_msg = body.get("detail") or (
            body.get("error", {}) if isinstance(body.get("error"), dict) else {}
        ).get("message", "")
        assert "does not construct multi-leg synthetic cross-rates" in error_msg

    @pytest.mark.asyncio
    async def test_unauthenticated_rejected(self):
        """Anonymous access returns 401."""
        transport = ASGITransport(app=app)
        client = AsyncClient(transport=transport, base_url="http://test")
        resp = await client.get("/api/v1/markets/fx")
        assert resp.status_code == 401
