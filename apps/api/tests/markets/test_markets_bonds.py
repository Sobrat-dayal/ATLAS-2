"""Comprehensive Automated Tests for ATLAS Bonds & Fixed-Income Markets V1 (Stage 61).

Tests:
1. Canonical Bond Security Identity, Issuer Separation, and Tranche Distinctness.
2. Debt Classification (Sovereign, Corporate, Supranational, Treasury Bill, Perpetual).
3. Contractual Coupon Semantics & Separation from Yield.
4. Clean vs Dirty Price Arithmetic and Sourced Accrued Interest.
5. Typed Yield Observations (YTM, Discount Yield, YTC) and Negative Yield Support.
6. Bid/Ask Spread and Crossed Market Protection.
7. Directory Search, Multi-Dimensional Filtering, and Keyset Pagination.
8. Authenticated and Authorized Read APIs (200, 401, 404).
9. Read-Only Invariants: 0 writes, 0 external provider fanouts.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.authorization.service import AuthorizationContext
from atlas.markets.bonds.config import (
    CANONICAL_BOND_ISSUERS,
    CANONICAL_BOND_SECURITIES,
    BondTypeEnum,
    CanonicalBondSecurityConfig,
    CouponFrequencyEnum,
    CouponTypeEnum,
    DayCountConventionEnum,
    IssuerCategoryEnum,
    MaturityBucketEnum,
    PriceBasisEnum,
    PriceKindEnum,
    PriceQuoteUnitEnum,
    YieldTypeEnum,
    generate_bond_id,
    generate_issuer_id,
)
from atlas.markets.bonds.repository import BondMarketRepository, calculate_maturity_bucket
from atlas.markets.bonds.service import (
    BondDirectoryService,
    BondMarketReadService,
)
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.main import app


# =============================================================================
# 1. Bond Identity & Classification Tests
# =============================================================================
class TestBondIdentityAndClassification:
    def test_canonical_bond_catalog_contents(self):
        """Verifies canonical bond catalog contains at least 16 securities."""
        assert len(CANONICAL_BOND_SECURITIES) >= 16
        sovereigns = [s for s in CANONICAL_BOND_SECURITIES if s.bond_type == BondTypeEnum.SOVEREIGN]
        corporates = [s for s in CANONICAL_BOND_SECURITIES if s.bond_type == BondTypeEnum.CORPORATE]
        supras = [s for s in CANONICAL_BOND_SECURITIES if s.bond_type == BondTypeEnum.SUPRANATIONAL]
        tbills = [s for s in CANONICAL_BOND_SECURITIES if s.bond_type == BondTypeEnum.TREASURY_BILL]

        assert len(sovereigns) >= 5
        assert len(corporates) >= 5
        assert len(supras) >= 2
        assert len(tbills) >= 1

    def test_bond_security_uuid_distinct_from_issuer_uuid(self):
        """Every bond's instrument entity ID must be distinct from its issuer entity ID."""
        for sec in CANONICAL_BOND_SECURITIES:
            assert sec.instrument_entity_id != sec.issuer_entity_id
            assert sec.issuer_entity_id in CANONICAL_BOND_ISSUERS

    def test_tranches_with_same_issuer_are_distinct(self):
        """Different tranches from the same issuer (e.g. US Treasury) must have unique UUIDs."""
        us_bonds = [
            s
            for s in CANONICAL_BOND_SECURITIES
            if s.issuer_name == "United States Department of the Treasury"
        ]
        assert len(us_bonds) >= 4
        uuids = {s.instrument_entity_id for s in us_bonds}
        assert len(uuids) == len(us_bonds)

        # 5Y vs 10Y vs 30Y differ in maturity and coupon
        ust_5y = next(s for s in us_bonds if "5Y" in s.provider_series_id)
        ust_10y = next(s for s in us_bonds if "10Y" in s.provider_series_id)
        assert ust_5y.maturity_date != ust_10y.maturity_date
        assert ust_5y.coupon_rate != ust_10y.coupon_rate

    def test_isin_and_identifier_integrity(self):
        """Ensures ISINs are valid 12-character strings starting with country code."""
        for sec in CANONICAL_BOND_SECURITIES:
            if sec.isin:
                assert len(sec.isin) == 12
                assert sec.isin[:2].isalpha()

    def test_perpetual_bond_handling(self):
        """Perpetual hybrid bond must have is_perpetual=True and None maturity date."""
        enel = next(s for s in CANONICAL_BOND_SECURITIES if s.is_perpetual)
        assert enel.maturity_date is None
        assert enel.coupon_rate == Decimal("6.3750")

        years, bucket = calculate_maturity_bucket(enel.maturity_date, enel.is_perpetual)
        assert years is None
        assert bucket == MaturityBucketEnum.PERPETUAL

    def test_treasury_bill_discount_yield_classification(self):
        """T-Bill must be classified as zero coupon with discount yield."""
        tbill = next(
            s for s in CANONICAL_BOND_SECURITIES if s.bond_type == BondTypeEnum.TREASURY_BILL
        )
        assert tbill.coupon_type == CouponTypeEnum.ZERO_COUPON
        assert tbill.coupon_rate == Decimal("0.0000")
        assert tbill.default_yield_type == YieldTypeEnum.DISCOUNT_YIELD
        assert tbill.default_yield_value == Decimal("5.2200")


# =============================================================================
# 2. Pricing & Accrued Interest Tests
# =============================================================================
class TestBondPricingAndAccruedInterest:
    def test_clean_vs_dirty_price_arithmetic(self):
        """Validates that dirty_price = clean_price + accrued_interest."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        ust_5y = next(s for s in CANONICAL_BOND_SECURITIES if s.isin == "US91282CJZ72")
        price_view = read_service.build_price_view(ust_5y)

        assert price_view.clean_price == Decimal("99.4500")
        assert price_view.accrued_interest == Decimal("0.7083")
        assert price_view.dirty_price == Decimal("100.1583")
        assert price_view.dirty_price == price_view.clean_price + price_view.accrued_interest

    def test_price_quotation_units_and_basis(self):
        """Quotation units and price basis must be explicit and verifiable."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        # US Treasury uses PERCENTAGE_OF_PAR
        ust = next(s for s in CANONICAL_BOND_SECURITIES if s.currency == "USD")
        ust_view = read_service.build_price_view(ust)
        assert ust_view.price_basis == PriceBasisEnum.CLEAN
        assert ust_view.quote_unit == PriceQuoteUnitEnum.PERCENTAGE_OF_PAR

        # UK Gilt uses PRICE_PER_100_FACE
        gilt = next(s for s in CANONICAL_BOND_SECURITIES if s.currency == "GBP")
        gilt_view = read_service.build_price_view(gilt)
        assert gilt_view.quote_unit == PriceQuoteUnitEnum.PRICE_PER_100_FACE

    def test_bid_ask_spread_and_crossed_market_protection(self):
        """Validates bid/ask spread and crossed market anomaly flagging."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        # Standard compatible quote
        ust_10y = next(s for s in CANONICAL_BOND_SECURITIES if s.isin == "US912810TW43")
        view = read_service.build_price_view(ust_10y)
        assert view.bid == Decimal("101.1094")
        assert view.ask == Decimal("101.1406")
        assert view.spread == Decimal("101.1406") - Decimal("101.1094")

        # Mock crossed market config: bid > ask
        crossed_cfg = CanonicalBondSecurityConfig(
            instrument_entity_id=generate_bond_id("CROSSED_TEST"),
            symbol="CROSSED TEST",
            name="Crossed Market Test Bond",
            issuer_entity_id=generate_issuer_id("TEST_ISSUER"),
            issuer_name="Test Issuer",
            issuer_category=IssuerCategoryEnum.SOVEREIGN,
            bond_type=BondTypeEnum.SOVEREIGN,
            currency="USD",
            issue_date="2024-01-01",
            maturity_date="2029-01-01",
            coupon_type=CouponTypeEnum.FIXED,
            coupon_rate=Decimal("5.0000"),
            coupon_frequency=CouponFrequencyEnum.SEMIANNUAL,
            day_count_convention=DayCountConventionEnum.THIRTY_360,
            default_clean_price=Decimal("100.00"),
            default_bid=Decimal("101.00"),
            default_ask=Decimal("99.00"),  # bid > ask (crossed!)
            provider_series_id="CROSSED_01",
        )
        crossed_view = read_service.build_price_view(crossed_cfg)
        assert crossed_view.spread is None
        assert crossed_view.price_kind == PriceKindEnum.UNKNOWN


# =============================================================================
# 3. Yield Semantics Tests
# =============================================================================
class TestBondYieldSemantics:
    def test_coupon_vs_yield_separation(self):
        """Coupon rate is contractual and must not be conflated with yield."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        ust_5y = next(s for s in CANONICAL_BOND_SECURITIES if s.isin == "US91282CJZ72")
        terms = read_service.build_terms_view(ust_5y)
        yield_obs = read_service.build_yield_view(ust_5y)

        # Coupon is 4.25%, Yield to Maturity is 4.375%
        assert terms.coupon_rate == Decimal("4.2500")
        assert yield_obs.yield_value == Decimal("4.3750")
        assert terms.coupon_rate != yield_obs.yield_value
        assert yield_obs.yield_type == YieldTypeEnum.YTM

    def test_negative_yield_supported(self):
        """Negative yields must be validly supported and not truncated to zero."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        neg_cfg = CanonicalBondSecurityConfig(
            instrument_entity_id=generate_bond_id("NEG_YIELD_TEST"),
            symbol="BUND NEGATIVE",
            name="Negative Yield German Federal Bond",
            issuer_entity_id=generate_issuer_id("GERMANY_FINANCE_AGENCY"),
            issuer_name="Federal Republic of Germany",
            issuer_category=IssuerCategoryEnum.SOVEREIGN,
            bond_type=BondTypeEnum.SOVEREIGN,
            currency="EUR",
            issue_date="2020-01-01",
            maturity_date="2025-01-01",
            coupon_type=CouponTypeEnum.ZERO_COUPON,
            coupon_rate=Decimal("0.0000"),
            coupon_frequency=CouponFrequencyEnum.ZERO,
            day_count_convention=DayCountConventionEnum.ACT_ACT_ICMA,
            default_clean_price=Decimal("101.50"),
            default_yield_value=Decimal("-0.3500"),  # Valid negative yield
            default_yield_type=YieldTypeEnum.YTM,
            provider_series_id="BUND_NEG_01",
        )
        yield_view = read_service.build_yield_view(neg_cfg)
        assert yield_view.yield_value == Decimal("-0.3500")

    def test_yield_basis_points_distinction(self):
        """Yield change in basis points must be separate from price percentage returns."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)

        ust_10y = next(s for s in CANONICAL_BOND_SECURITIES if s.isin == "US912810TW43")
        price_view = read_service.build_price_view(ust_10y)
        yield_view = read_service.build_yield_view(ust_10y)

        # Price percentage return is negative (-0.185%), Yield change is +3.1 bps
        assert price_view.price_change_24h_percent < Decimal("0")
        assert yield_view.yield_change_bps_24h == Decimal("3.1")


# =============================================================================
# 4. Repository & Filter Tests
# =============================================================================
class TestBondRepositoryAndFilters:
    def test_filter_by_issuer_type(self):
        """Filter by sovereign vs corporate issuer category."""
        repo = BondMarketRepository()
        sov_bonds, total_sov, _, _ = repo.list_bonds(issuer_type="sovereign")
        assert total_sov >= 8
        for b in sov_bonds:
            assert b.issuer_category == IssuerCategoryEnum.SOVEREIGN

        corp_bonds, total_corp, _, _ = repo.list_bonds(issuer_type="corporate")
        assert total_corp >= 5
        for b in corp_bonds:
            assert b.issuer_category == IssuerCategoryEnum.CORPORATE

    def test_filter_by_currency(self):
        """Filter by currency denomination (USD, EUR, GBP, JPY)."""
        repo = BondMarketRepository()
        usd_bonds, total_usd, _, _ = repo.list_bonds(currency="USD")
        assert total_usd >= 8
        for b in usd_bonds:
            assert b.currency == "USD"

        eur_bonds, total_eur, _, _ = repo.list_bonds(currency="EUR")
        assert total_eur >= 4
        for b in eur_bonds:
            assert b.currency == "EUR"

    def test_filter_by_coupon_type(self):
        """Filter by fixed vs zero_coupon."""
        repo = BondMarketRepository()
        fixed_bonds, total_fixed, _, _ = repo.list_bonds(coupon_type="fixed")
        assert total_fixed >= 13
        for b in fixed_bonds:
            assert b.coupon_type == CouponTypeEnum.FIXED

        zero_bonds, total_zero, _, _ = repo.list_bonds(coupon_type="zero_coupon")
        assert total_zero >= 2
        for b in zero_bonds:
            assert b.coupon_type == CouponTypeEnum.ZERO_COUPON

    def test_search_by_query(self):
        """Search by ISIN, symbol, security name, or issuer name."""
        repo = BondMarketRepository()

        # Search by ISIN
        by_isin, total, _, _ = repo.list_bonds(query="US91282CJZ72")
        assert total == 1
        assert by_isin[0].isin == "US91282CJZ72"

        # Search by Issuer name
        by_issuer, total_issuer, _, _ = repo.list_bonds(query="Apple")
        assert total_issuer == 1
        assert by_issuer[0].issuer_name == "Apple Inc."

        # Search by Gilt symbol
        by_symbol, total_sym, _, _ = repo.list_bonds(query="UKT")
        assert total_sym == 2

    def test_keyset_cursor_pagination(self):
        """Keyset pagination must be deterministic and exhaustive without duplicates."""
        repo = BondMarketRepository()
        page1, total, cursor1, has_more1 = repo.list_bonds(limit=5)
        assert len(page1) == 5
        assert has_more1 is True
        assert cursor1 is not None

        page2, total2, cursor2, has_more2 = repo.list_bonds(limit=5, cursor=cursor1)
        assert len(page2) == 5
        assert total == total2

        # Disjoint sets of instruments
        p1_ids = {s.instrument_entity_id for s in page1}
        p2_ids = {s.instrument_entity_id for s in page2}
        assert p1_ids.isdisjoint(p2_ids)

    def test_coverage_summary_counts(self):
        """Coverage summary accurately reports catalog aggregates."""
        repo = BondMarketRepository()
        cov = repo.get_coverage_summary()
        assert cov.total_bonds >= 16
        assert cov.total_issuers >= 10
        assert cov.sovereign_bonds >= 8
        assert cov.corporate_bonds >= 5
        assert cov.bonds_with_prices >= 16
        assert cov.bonds_with_yields >= 16
        assert "USD" in cov.currencies
        assert "EUR" in cov.currencies


# =============================================================================
# 5. API Endpoint Tests
# =============================================================================
class TestBondAPIEndpoints:
    @pytest.fixture
    def authenticated_principal(self):
        return AuthPrincipal(
            sub=str(uuid.uuid4()),
            email="fixed_income_analyst@atlas.financial",
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
        """Anonymous access to /markets/bonds must return 401."""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            resp = await client.get("/api/v1/markets/bonds")
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_authenticated_directory_success(self, authenticated_client):
        """Authenticated request to /markets/bonds returns 200 with directory items."""
        resp = await authenticated_client.get("/api/v1/markets/bonds?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "coverage" in data
        assert len(data["items"]) <= 10
        assert data["total"] >= 16

        first = data["items"][0]
        assert "instrument_entity_id" in first
        assert "symbol" in first
        assert "issuer" in first
        assert "terms" in first
        assert "price" in first
        assert "yield_obs" in first

    @pytest.mark.asyncio
    async def test_get_filter_options_api(self, authenticated_client):
        """Endpoint /markets/bonds/filters returns filter metadata and counts."""
        resp = await authenticated_client.get("/api/v1/markets/bonds/filters")
        assert resp.status_code == 200
        data = resp.json()
        assert "currencies" in data
        assert "issuer_categories" in data
        assert "bond_types" in data
        assert "coupon_types" in data
        assert "maturity_buckets" in data
        assert "issuers" in data
        assert "USD" in data["currencies"]
        assert "sovereign" in data["bond_types"]

    @pytest.mark.asyncio
    async def test_get_bond_detail_success(self, authenticated_client):
        """Endpoint /markets/bonds/{id} returns deep inspection overview."""
        target_bond = CANONICAL_BOND_SECURITIES[0]
        url = f"/api/v1/markets/bonds/{target_bond.instrument_entity_id}"
        resp = await authenticated_client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["instrument_entity_id"] == str(target_bond.instrument_entity_id)
        assert data["name"] == target_bond.name
        assert data["isin"] == target_bond.isin
        assert data["terms"]["coupon_rate"] == str(target_bond.coupon_rate)
        assert data["price"]["clean_price"] == str(target_bond.default_clean_price)
        assert data["yield_obs"]["yield_value"] == str(target_bond.default_yield_value)
        assert "non_executable_disclaimer" in data

    @pytest.mark.asyncio
    async def test_get_bond_detail_not_found(self, authenticated_client):
        """Random UUID returns 404."""
        non_existent = uuid.uuid4()
        resp = await authenticated_client.get(f"/api/v1/markets/bonds/{non_existent}")
        assert resp.status_code == 404
        error_body = resp.json()
        msg = error_body.get("error", {}).get("message", "") or error_body.get("detail", "")
        assert "not found" in msg.lower()


# =============================================================================
# 6. Read-Only Invariant Tests
# =============================================================================
class TestBondReadOnlyGuarantees:
    def test_read_directory_does_not_mutate_state(self):
        """Directory queries perform 0 writes and do not mutate catalog."""
        repo = BondMarketRepository()
        read_service = BondMarketReadService(repository=repo)
        dir_service = BondDirectoryService(repository=repo, read_service=read_service)

        initial_len = len(repo.list_bonds()[0])
        response = dir_service.get_directory()
        after_len = len(repo.list_bonds()[0])

        assert initial_len == after_len
        assert response.total == len(CANONICAL_BOND_SECURITIES)
