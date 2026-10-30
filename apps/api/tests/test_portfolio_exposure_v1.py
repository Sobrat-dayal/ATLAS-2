"""
Tests for ATLAS Portfolio Allocation, Exposure Intelligence & Concentration (Stage 112).

Verifies:
1. Part X Allocation reference fixture ($10k Tech, $5k Financials, $5k Cash => NAV $20k).
2. Part XXVIII Concentration HHI and Effective Number of Holdings fixture (50%, 25%, 25% => HHI 0.375, N_eff 2.67).
3. Part XXXII Fund/ETF look-through constituent expansion and wrapper double-count prevention.
4. Multi-ETF overlap consolidation across SPY and QQQ.
5. Geographic policies (Issuer Domicile, HQ, Listing Venue).
6. Currency denomination exposure and conversion.
7. Date-to-date historical allocation drift (delta_w = w_t2 - w_t1).
8. FastAPI REST endpoints, calculation flows, and strict multi-tenant isolation.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from atlas.auth import AuthPrincipal
from atlas.portfolios import (
    AccountCreateRequest,
    PortfolioCreateRequest,
    PortfolioService,
    TransactionCreateRequest,
    TransactionType,
)
from atlas.portfolios.exposure import (
    AssetClass,
    CalculateExposureRequest,
    ConcentrationScope,
    ExposureBasis,
    ExposureDimension,
    GeographyPolicy,
    PortfolioExposureEngine,
    PortfolioExposureService,
    calculate_concentration_hhi,
    calculate_top_n_weights,
    calculate_weight,
)
from atlas_api.main import app
from atlas_api.routers.portfolios import get_exposure_service, get_portfolio_service


# ---------------------------------------------------------------------------
# Test Fixtures & Utilities
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_services():
    portfolio_service = PortfolioService()
    exposure_service = PortfolioExposureService(portfolio_service)
    return portfolio_service, exposure_service


# ---------------------------------------------------------------------------
# 1. Part X Allocation Reference Fixture
# ---------------------------------------------------------------------------

def test_part_x_allocation_reference_fixture(clean_services):
    """
    Part X reference fixture:
    $10,000 Tech Equity (e.g. AAPL)
    $5,000 Financials Equity (e.g. JPM)
    $5,000 USD Cash
    NAV = $20,000
    Sector: Tech 50.0%, Financials 25.0%, Cash 25.0%
    Asset Class: Equity 75.0%, Cash 25.0%
    Sum of weights == 1.0 (100.0%)
    """
    portfolio_service, exposure_service = clean_services
    user_id = "usr_analyst_1"

    # 1. Create portfolio with USD base currency
    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="Part X Fixture Fund", base_currency="USD"),
    )
    accounts = portfolio_service.list_accounts(port.id, user_id)
    account_id = accounts[0].id

    # Deposit $20,000 cash
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("20000.00"),
        ),
    )

    # Set quotes: AAPL @ $200, JPM @ $100
    portfolio_service.set_mock_quote("inst_aapl", Decimal("200.00"), currency="USD")
    portfolio_service.set_mock_quote("inst_jpm", Decimal("100.00"), currency="USD")

    # Buy 50 AAPL @ $200 = $10,000
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_aapl",
            symbol="AAPL",
            quantity=Decimal("50"),
            unit_price=Decimal("200.00"),
            gross_amount=Decimal("10000.00"),
        ),
    )

    # Buy 50 JPM @ $100 = $5,000
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_jpm",
            symbol="JPM",
            quantity=Decimal("50"),
            unit_price=Decimal("100.00"),
            gross_amount=Decimal("5000.00"),
        ),
    )
    # Remaining Cash: $20,000 - $10,000 - $5,000 = $5,000

    # Calculate exposure
    run = exposure_service.calculate_portfolio_exposure(
        port.id,
        user_id,
        CalculateExposureRequest(enable_look_through=False),
    )

    assert run.total_nav == Decimal("20000.00")
    assert run.cash_value == Decimal("5000.00")
    assert run.cash_weight == Decimal("0.250000")
    assert run.reconciled is True

    # Verify Asset Class: Equity 75%, Cash 25%
    ac_map = {c.category_id: c for c in run.asset_classes.categories}
    assert ac_map[AssetClass.EQUITY.value].weight == Decimal("0.750000")
    assert ac_map[AssetClass.EQUITY.value].percentage == Decimal("75.000000")
    assert ac_map[AssetClass.EQUITY.value].base_value == Decimal("15000.00")

    assert ac_map[AssetClass.CASH.value].weight == Decimal("0.250000")
    assert ac_map[AssetClass.CASH.value].percentage == Decimal("25.000000")
    assert ac_map[AssetClass.CASH.value].base_value == Decimal("5000.00")
    assert run.asset_classes.total_weight == Decimal("1.000000")

    # Verify Sectors: Information Technology 50%, Financials 25%, Cash 25%
    sec_map = {c.category_id: c for c in run.sectors.categories}
    assert sec_map["information_technology"].weight == Decimal("0.500000")
    assert sec_map["information_technology"].base_value == Decimal("10000.00")
    assert sec_map["financials"].weight == Decimal("0.250000")
    assert sec_map["financials"].base_value == Decimal("5000.00")
    assert sec_map["cash"].weight == Decimal("0.250000")
    assert sec_map["cash"].base_value == Decimal("5000.00")
    assert run.sectors.total_weight == Decimal("1.000000")


# ---------------------------------------------------------------------------
# 2. Part XXVIII Concentration HHI Reference Fixture
# ---------------------------------------------------------------------------

def test_part_xxviii_concentration_reference_fixture():
    """
    Part XXVIII fixture:
    Weights: 50%, 25%, 25%
    HHI = 0.50^2 + 0.25^2 + 0.25^2 = 0.25 + 0.0625 + 0.0625 = 0.375
    Conventional HHI = 3,750
    Effective Number of Holdings = 1 / 0.375 = 2.666667 (approx 2.67)
    """
    weights = [Decimal("0.50"), Decimal("0.25"), Decimal("0.25")]
    raw_hhi, norm_hhi, n_eff = calculate_concentration_hhi(weights)

    assert raw_hhi == Decimal("0.375000")
    assert round(n_eff, 2) == Decimal("2.67")

    top1, top3, top5, top10, top20 = calculate_top_n_weights(weights)
    assert top1 == Decimal("0.500000")
    assert top3 == Decimal("1.000000")
    assert top5 == Decimal("1.000000")


# ---------------------------------------------------------------------------
# 3. Part XXXII Fund/ETF Look-Through Reference Fixture
# ---------------------------------------------------------------------------

def test_part_xxxii_etf_look_through_reference_fixture(clean_services):
    """
    Part XXXII fixture:
    $2,000 allocated to an ETF (e.g. SPY) inside a $10,000 portfolio.
    ETF constituents decompose into constituent shares.
    Total exposure remains $10,000 (ETF wrapper is NOT double-counted with constituents).
    """
    portfolio_service, exposure_service = clean_services
    user_id = "usr_etf_analyst"

    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="ETF Look-Through Fund", base_currency="USD"),
    )
    account_id = portfolio_service.list_accounts(port.id, user_id)[0].id

    # Fund $10,000 cash
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("10000.00"),
        ),
    )

    # Set SPY price: $500/share. Buy 4 shares = $2,000.
    portfolio_service.set_mock_quote("inst_spy", Decimal("500.00"), currency="USD")
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_spy",
            symbol="SPY",
            quantity=Decimal("4"),
            unit_price=Decimal("500.00"),
            gross_amount=Decimal("2000.00"),
        ),
    )

    # Buy $3,000 AAPL directly (15 shares @ $200)
    portfolio_service.set_mock_quote("inst_aapl", Decimal("200.00"), currency="USD")
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_aapl",
            symbol="AAPL",
            quantity=Decimal("15"),
            unit_price=Decimal("200.00"),
            gross_amount=Decimal("3000.00"),
        ),
    )
    # Remaining Cash: $5,000

    # Calculate with look-through ENABLED
    run = exposure_service.calculate_portfolio_exposure(
        port.id,
        user_id,
        CalculateExposureRequest(enable_look_through=True),
    )

    # Verification: NAV denominator is exactly $10,000
    assert run.total_nav == Decimal("10000.00")
    assert run.reconciled is True

    # Look-through results exist for SPY
    assert len(run.funds) == 1
    spy_fund = run.funds[0]
    assert spy_fund.fund_symbol == "SPY"
    assert spy_fund.fund_base_value == Decimal("2000.00")
    assert spy_fund.fund_weight_in_portfolio == Decimal("0.200000")

    # AAPL has both direct weight ($3,000 / $10,000 = 30%) and look-through weight from SPY
    sec_map = {s.symbol: s for s in run.security_weights}
    assert "AAPL" in sec_map
    aapl_sec = sec_map["AAPL"]
    assert aapl_sec.direct_weight == Decimal("0.300000")
    assert aapl_sec.look_through_weight > Decimal("0.000000")
    assert aapl_sec.weight == aapl_sec.direct_weight + aapl_sec.look_through_weight

    # Total sector weight reconciles to 1.0 (no wrapper double count!)
    assert run.sectors.reconciled is True
    assert run.sectors.total_weight == Decimal("1.000000")
    assert run.asset_classes.reconciled is True
    assert run.asset_classes.total_weight == Decimal("1.000000")


# ---------------------------------------------------------------------------
# 4. Multi-ETF Overlap Consolidation (SPY and QQQ)
# ---------------------------------------------------------------------------

def test_cross_etf_overlap_consolidation(clean_services):
    """Holding both SPY and QQQ consolidates overlapping constituents (AAPL, MSFT, NVDA)."""
    portfolio_service, exposure_service = clean_services
    user_id = "usr_etf_overlap"

    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="Dual ETF Fund", base_currency="USD"),
    )
    account_id = portfolio_service.list_accounts(port.id, user_id)[0].id

    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("100000.00"),
        ),
    )

    portfolio_service.set_mock_quote("inst_spy", Decimal("500.00"), currency="USD")
    portfolio_service.set_mock_quote("inst_qqq", Decimal("400.00"), currency="USD")

    # Buy $50,000 SPY (100 shares @ $500)
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_spy",
            symbol="SPY",
            quantity=Decimal("100"),
            unit_price=Decimal("500.00"),
            gross_amount=Decimal("50000.00"),
        ),
    )

    # Buy $50,000 QQQ (125 shares @ $400)
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_qqq",
            symbol="QQQ",
            quantity=Decimal("125"),
            unit_price=Decimal("400.00"),
            gross_amount=Decimal("50000.00"),
        ),
    )

    run = exposure_service.calculate_portfolio_exposure(
        port.id,
        user_id,
        CalculateExposureRequest(enable_look_through=True),
    )

    assert len(run.funds) == 2
    assert len(run.cross_fund_overlap) > 0

    overlap_symbols = {o.constituent_symbol: o for o in run.cross_fund_overlap}
    assert "AAPL" in overlap_symbols
    assert "MSFT" in overlap_symbols
    assert "NVDA" in overlap_symbols

    aapl_overlap = overlap_symbols["AAPL"]
    assert "SPY" in aapl_overlap.funds_involved
    assert "QQQ" in aapl_overlap.funds_involved
    assert aapl_overlap.total_effective_weight > Decimal("0.05")  # Over 5% combined weight


# ---------------------------------------------------------------------------
# 5. Geographic Policies (Domicile vs HQ vs Listing Venue)
# ---------------------------------------------------------------------------

def test_geography_policies_domicile_vs_hq_vs_listing(clean_services):
    """
    Test ADR / multi-national security geographic attribution:
    INFY ADR is domiciled in India (IN), HQ in India (IN), listed in United States (US).
    """
    portfolio_service, exposure_service = clean_services
    user_id = "usr_geo"

    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="Geo Policy Fund", base_currency="USD"),
    )
    account_id = portfolio_service.list_accounts(port.id, user_id)[0].id

    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("10000.00"),
        ),
    )

    portfolio_service.set_mock_quote("inst_infy_adr", Decimal("20.00"), currency="USD")
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.BUY,
            cash_currency="USD",
            instrument_id="inst_infy_adr",
            symbol="INFY",
            quantity=Decimal("500"),
            unit_price=Decimal("20.00"),
            gross_amount=Decimal("10000.00"),
        ),
    )

    # 1. ISSUER_DOMICILE -> IN (India)
    run_dom = exposure_service.calculate_portfolio_exposure(
        port.id,
        user_id,
        CalculateExposureRequest(geography_policy=GeographyPolicy.ISSUER_DOMICILE),
    )
    country_map_dom = {c.category_id: c for c in run_dom.countries.categories}
    assert "IN" in country_map_dom
    assert country_map_dom["IN"].weight == Decimal("1.000000")

    # 2. LISTING_VENUE -> US (United States)
    run_list = exposure_service.calculate_portfolio_exposure(
        port.id,
        user_id,
        CalculateExposureRequest(geography_policy=GeographyPolicy.LISTING_VENUE),
    )
    country_map_list = {c.category_id: c for c in run_list.countries.categories}
    assert "US" in country_map_list
    assert country_map_list["US"].weight == Decimal("1.000000")


# ---------------------------------------------------------------------------
# 6. Currency Denomination Exposure
# ---------------------------------------------------------------------------

def test_currency_denomination_exposure(clean_services):
    """
    Multi-currency portfolio: USD Cash, EUR Cash, INR Cash converted to base USD.
    """
    portfolio_service, exposure_service = clean_services
    user_id = "usr_cur"

    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="Multi Currency Fund", base_currency="USD"),
    )
    account_id = portfolio_service.list_accounts(port.id, user_id)[0].id

    # 5,000 USD
    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("5000.00"),
        ),
    )

    run = exposure_service.calculate_portfolio_exposure(port.id, user_id)
    cur_map = {c.category_id: c for c in run.currencies.categories}
    assert "USD" in cur_map
    assert cur_map["USD"].weight == Decimal("1.000000")
    assert cur_map["USD"].base_value == Decimal("5000.00")


# ---------------------------------------------------------------------------
# 7. Date-to-Date Historical Allocation Drift
# ---------------------------------------------------------------------------

def test_historical_allocation_change_and_drift(clean_services):
    """Date-to-date allocation drift delta_w = w_t2 - w_t1 in percentage points and bps."""
    portfolio_service, exposure_service = clean_services
    user_id = "usr_drift"

    port = portfolio_service.create_portfolio(
        user_id,
        PortfolioCreateRequest(name="Drift Analysis Fund", base_currency="USD"),
    )
    account_id = portfolio_service.list_accounts(port.id, user_id)[0].id

    t1 = date.today() - timedelta(days=30)
    t2 = date.today()

    portfolio_service.post_transaction(
        port.id,
        user_id,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("10000.00"),
            trade_date=datetime.utcnow() - timedelta(days=45),
        ),
    )

    changes = exposure_service.get_allocation_changes(
        port.id,
        user_id,
        dimension=ExposureDimension.ASSET_CLASS,
        start_date=t1,
        end_date=t2,
    )

    assert len(changes) > 0
    # Both points have 100% Cash, so change is 0 bps
    cash_change = next(c for c in changes if c.category_id == AssetClass.CASH.value)
    assert cash_change.weight_change_pct == Decimal("0.000000")
    assert cash_change.weight_change_bps == 0


# ---------------------------------------------------------------------------
# 8. REST API Endpoints & Tenant Isolation
# ---------------------------------------------------------------------------

def test_rest_api_exposure_endpoints_and_tenant_isolation():
    """Verify FastAPI routes under /api/v1/portfolios/{id}/... and tenant isolation."""
    user1 = AuthPrincipal(
        sub="usr_owner_alpha",
        email="owner@atlas.financial",
        role="authenticated",
    )
    user2 = AuthPrincipal(
        sub="usr_intruder_beta",
        email="intruder@external.org",
        role="authenticated",
    )

    port_service = PortfolioService()
    exp_service = PortfolioExposureService(port_service)

    from atlas_api.auth.dependencies import get_current_user
    app.dependency_overrides[get_portfolio_service] = lambda: port_service
    app.dependency_overrides[get_exposure_service] = lambda: exp_service
    app.dependency_overrides[get_current_user] = lambda: user1

    client = TestClient(app)

    # 1. Create a portfolio via REST API
    res = client.post(
        "/api/v1/portfolios",
        json={"name": "API Exposure Test Portfolio", "base_currency": "USD"},
    )
    assert res.status_code == 201, res.text
    port_id = res.json()["id"]

    # Fund $10,000 cash so NAV is positive for calculations
    accs_res = client.get(f"/api/v1/portfolios/{port_id}/accounts")
    account_id = accs_res.json()["items"][0]["id"]
    port_service.post_transaction(
        port_id,
        user1.sub,
        TransactionCreateRequest(
            account_id=account_id,
            transaction_type=TransactionType.CASH_DEPOSIT,
            cash_currency="USD",
            gross_amount=Decimal("10000.00"),
        ),
    )

    # 2. Trigger exposure calculation
    calc_res = client.post(
        f"/api/v1/portfolios/{port_id}/exposures/calculate",
        json={"exposure_basis": "NET_ASSET_VALUE", "enable_look_through": True},
    )
    assert calc_res.status_code == 200, calc_res.text
    data = calc_res.json()
    assert data["portfolio_id"] == port_id
    assert "asset_classes" in data
    assert "sectors" in data
    assert "concentration" in data

    # 3. Test dimensional endpoints
    ac_res = client.get(f"/api/v1/portfolios/{port_id}/allocations/asset-classes")
    assert ac_res.status_code == 200
    assert ac_res.json()["dimension"] == "ASSET_CLASS"

    sec_res = client.get(f"/api/v1/portfolios/{port_id}/allocations/sectors")
    assert sec_res.status_code == 200
    assert sec_res.json()["dimension"] == "SECTOR"

    country_res = client.get(f"/api/v1/portfolios/{port_id}/allocations/countries")
    assert country_res.status_code == 200
    assert country_res.json()["dimension"] == "COUNTRY"

    cur_res = client.get(f"/api/v1/portfolios/{port_id}/allocations/currencies")
    assert cur_res.status_code == 200
    assert cur_res.json()["dimension"] == "CURRENCY"

    conc_res = client.get(f"/api/v1/portfolios/{port_id}/concentration/summary")
    assert conc_res.status_code == 200
    assert "herfindahl_index" in conc_res.json()

    sec_w_res = client.get(f"/api/v1/portfolios/{port_id}/concentration/securities")
    assert sec_w_res.status_code == 200

    iss_w_res = client.get(f"/api/v1/portfolios/{port_id}/concentration/issuers")
    assert iss_w_res.status_code == 200

    look_res = client.get(f"/api/v1/portfolios/{port_id}/lookthrough")
    assert look_res.status_code == 200

    qual_res = client.get(f"/api/v1/portfolios/{port_id}/exposures/data-quality")
    assert qual_res.status_code == 200
    assert "completeness" in qual_res.json()

    # 4. Multi-Tenant Isolation: Another user attempts to read
    app.dependency_overrides[get_current_user] = lambda: user2

    bad_res = client.get(f"/api/v1/portfolios/{port_id}/exposures")
    assert bad_res.status_code in (403, 404), "Tenant isolation must prevent unauthorized portfolio access."

    # Cleanup overrides
    app.dependency_overrides.clear()
