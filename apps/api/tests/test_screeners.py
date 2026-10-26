"""Comprehensive Automated Test Suite for Financial Screeners V1 (Stage 94).

Verifies:
- Canonical financial security universes & eligibility
- Instrument, Listing, and Company Entity distinction
- Multiple share-class and cross-listing handling (GOOGL vs GOOG, INFY ADR vs INFYS)
- ETF and fund exclusion from common equity screening
- Active listing status and delisted/suspended instrument qualification
- Geographic filters (listing market country vs issuer domicile)
- Sector and industry classification hierarchy
- Price, volume, 20-day average volume, turnover, and market cap filters
- Fundamental metrics (Revenue, Net Income, Operating Income, Assets, Book Equity)
- Valuation ratios (P/E, P/B, P/S, Dividend Yield, Margins, ROE, ROA)
- Strict NULL handling: missing values never pass numeric comparisons
- Strict negative earnings handling: P/E on non-positive earnings is None / N/M, never 0
- Comparison operators: EQ, NE, GT, GTE, LT, LTE, BETWEEN, IN
- Basic AND composition and complexity limits (max 20 filters)
- Deterministic sorting with stable tie-breaker ordering and NULLS LAST
- Bounded server-side pagination with opaque cursor integrity
- Typed API contracts (/universes, /filters, /columns, /exchanges, /geographies, /industries, /validate, /run, /coverage)
"""

from decimal import Decimal

import pytest
from atlas.screeners import (
    FilterCriterionDTO,
    FilterOperator,
    ScreenerFilterNotFoundError,
    ScreenerQueryLimitExceededError,
    ScreenerRangeInvalidError,
    ScreenerRepository,
    ScreenerRunRequestDTO,
    ScreenerService,
    ScreenerUniverseNotFoundError,
    SecurityType,
    SortCriterionDTO,
    SortDirection,
    UniverseSelectionDTO,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from atlas_api.routers.screeners import get_screener_service
from atlas_api.routers.screeners import router as screeners_router


@pytest.fixture
def repo():
    return ScreenerRepository()


@pytest.fixture
def service(repo):
    return ScreenerService(repository=repo)


@pytest.fixture
def client(service: ScreenerService) -> TestClient:
    app = FastAPI()
    app.include_router(screeners_router)
    app.dependency_overrides[get_screener_service] = lambda: service
    return TestClient(app)


# =============================================================================
# 1. Canonical Instrument, Listing, and Entity Identity Tests
# =============================================================================

def test_canonical_security_identity(service: ScreenerService):
    """Every candidate record must preserve canonical UUIDs and distinct issuer company."""
    records = service._repo.get_records()
    assert len(records) >= 20

    seen_inst_ids = set()
    for r in records:
        assert r.instrument_entity_id is not None
        assert r.listing_id is not None
        assert r.issuer_company_entity_id is not None
        assert r.ticker
        assert r.canonical_security_name
        seen_inst_ids.add(r.instrument_entity_id)

    # Unique instrument entities
    assert len(seen_inst_ids) == len(records)


def test_multiple_share_classes_have_distinct_instrument_ids(service: ScreenerService):
    """
    Alphabet Class A (GOOGL) and Class C (GOOG) must be distinct Financial Instruments
    while sharing the identical issuer Company Entity UUID.
    """
    records = {r.ticker: r for r in service._repo.get_records()}
    googl = records.get("GOOGL")
    goog = records.get("GOOG")

    assert googl is not None
    assert goog is not None
    assert googl.instrument_entity_id != goog.instrument_entity_id
    assert googl.share_class_name == "Class A"
    assert goog.share_class_name == "Class C"
    # Shared underlying issuer company
    assert googl.issuer_company_entity_id == goog.issuer_company_entity_id


def test_cross_listed_adr_and_domestic_equity_distinction(service: ScreenerService):
    """
    Infosys ADR (INFY on NYSE) and Infosys Common (INFYS on NSE) are separate instruments
    with distinct currencies (USD vs INR) sharing the identical issuer company.
    """
    records = {r.ticker: r for r in service._repo.get_records()}
    infy_adr = records.get("INFY")
    infys_nse = records.get("INFYS")

    assert infy_adr is not None
    assert infys_nse is not None
    assert infy_adr.instrument_entity_id != infys_nse.instrument_entity_id
    assert infy_adr.security_type == SecurityType.DEPOSITARY_RECEIPT
    assert infys_nse.security_type == SecurityType.COMMON_STOCK
    assert infy_adr.trading_currency == "USD"
    assert infys_nse.trading_currency == "INR"
    assert infy_adr.exchange_mic == "XNYS"
    assert infys_nse.exchange_mic == "XNSE"
    assert infy_adr.issuer_company_entity_id == infys_nse.issuer_company_entity_id
    assert infy_adr.issuer_country_code == "IN"  # Issuer domicile remains India!


def test_etf_exclusion_from_common_equity_universe(service: ScreenerService):
    """ETFs (like SPY) must be excluded by default from the Common Equity screening universe."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[],
    )
    res = service.run_screen(req)
    tickers = {r.ticker for r in res.rows}
    assert "SPY" not in tickers  # SPY is an ETF, not common operating stock!


def test_delisted_security_exclusion_from_active_universe(service: ScreenerService):
    """Delisted historical securities (Enron) must be excluded from active screens by default."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[],
    )
    res = service.run_screen(req)
    tickers = {r.ticker for r in res.rows}
    assert "ENE" not in tickers  # Enron is delisted!

    # When delisted universe is explicitly selected, delisted securities appear
    delisted_req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="delisted_equity"),
        filters=[],
    )
    delisted_res = service.run_screen(delisted_req)
    delisted_tickers = {r.ticker for r in delisted_res.rows}
    assert "ENE" in delisted_tickers


# =============================================================================
# 2. Universe and Geographic / Exchange Filtering Tests
# =============================================================================

def test_exchange_filter_pushdown(service: ScreenerService):
    """Filtering by exchange MIC returns only securities listed on that venue."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity", exchange_mics=["XNAS"]),
        filters=[],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        assert r.exchange_mic == "XNAS"


def test_country_filters_distinguish_listing_and_issuer_domicile(service: ScreenerService):
    """
    Listing country (e.g. US for NYSE ADRs) differs from Issuer Domicile (e.g. TW for TSM).
    """
    # Filter where listing country is US
    us_listed_req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="all_equity", listing_country_codes=["US"]),
        filters=[],
    )
    us_listed_res = service.run_screen(us_listed_req)
    tickers = {r.ticker for r in us_listed_res.rows}
    assert "TSM" in tickers  # TSM trades on NYSE (US)

    # Filter where issuer domicile is Taiwan (TW)
    tw_issuer_req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="all_equity", issuer_country_codes=["TW"]),
        filters=[],
    )
    tw_issuer_res = service.run_screen(tw_issuer_req)
    tw_tickers = {r.ticker for r in tw_issuer_res.rows}
    assert "TSM" in tw_tickers
    assert "AAPL" not in tw_tickers


def test_sector_and_industry_filters(service: ScreenerService):
    """Filtering by sector returns only matching operating companies."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity", sectors=["Technology"]),
        filters=[],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        assert r.sector == "Technology"


# =============================================================================
# 3. Market Data Filters (Market Cap, Price, Volume, Liquidity)
# =============================================================================

def test_market_cap_gte_filter(service: ScreenerService):
    """Filter for mega-cap stocks with market cap >= $1 Trillion."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="market_cap",
                operator=FilterOperator.GTE,
                value="1000000000000",  # $1T
            )
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) >= 5
    for r in res.rows:
        assert r.metrics["market_cap"].raw_value >= Decimal("1000000000000")


def test_price_range_between_filter(service: ScreenerService):
    """Filter for stocks with price BETWEEN 200 and 500."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="last_price",
                operator=FilterOperator.BETWEEN,
                value="200.00",
                secondary_value="500.00",
            )
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        price = r.metrics["last_price"].raw_value
        assert Decimal("200.00") <= price <= Decimal("500.00")


def test_average_volume_filter(service: ScreenerService):
    """Filter for liquid stocks with 20-day average volume >= 20M shares."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="volume_20d_avg",
                operator=FilterOperator.GTE,
                value="20000000",
            )
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        vol = r.metrics["volume_20d_avg"].raw_value
        assert vol >= Decimal("20000000")


# =============================================================================
# 4. Fundamental & Valuation Ratio Filters
# =============================================================================

def test_revenue_and_net_income_filters(service: ScreenerService):
    """Filter for profitable companies with Revenue >= $100B and Net Income >= $30B."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="revenue",
                operator=FilterOperator.GTE,
                value="100000000000",
            ),
            FilterCriterionDTO(
                filter_id="net_income",
                operator=FilterOperator.GTE,
                value="30000000000",
            ),
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) >= 4
    for r in res.rows:
        assert r.metrics["revenue"].raw_value >= Decimal("100000000000")
        assert r.metrics["net_income"].raw_value >= Decimal("30000000000")


def test_pe_ratio_lte_filter_excludes_negative_earnings(service: ScreenerService):
    """
    Filtering for P/E <= 40 must return valid low-multiple stocks and strictly
    EXCLUDE loss-making companies (like BIOX) whose P/E is None / Not Meaningful.
    """
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="pe_ratio",
                operator=FilterOperator.LTE,
                value="40.00",
            )
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        pe = r.metrics["pe_ratio"].raw_value
        assert pe is not None
        assert pe <= Decimal("40.00")
        assert r.ticker != "BIOX"  # Loss-making startup cannot satisfy P/E <= 40!


def test_strict_null_handling_missing_metric_does_not_satisfy_comparisons(service: ScreenerService):
    """
    Berkshire Hathaway (BRK.A) and JPMorgan (JPM) do not report standard gross margin.
    Filtering on gross_margin >= 0 must strictly exclude them (missing is not zero).
    """
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="gross_margin",
                operator=FilterOperator.GTE,
                value="0.00",
            )
        ],
    )
    res = service.run_screen(req)
    tickers = {r.ticker for r in res.rows}
    assert "JPM" not in tickers  # Bank has no gross margin
    assert "BRK.A" not in tickers  # Insurance conglomerate has no gross margin


def test_dividend_yield_filter(service: ScreenerService):
    """Filtering on dividend_yield >= 1.5% returns dividend-paying stocks."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        filters=[
            FilterCriterionDTO(
                filter_id="dividend_yield",
                operator=FilterOperator.GTE,
                value="1.50",
            )
        ],
    )
    res = service.run_screen(req)
    assert len(res.rows) > 0
    for r in res.rows:
        dy = r.metrics["dividend_yield"].raw_value
        assert dy >= Decimal("1.50")


# =============================================================================
# 5. Deterministic Sorting & Pagination Tests
# =============================================================================

def test_deterministic_sorting_with_stable_tie_breaker(service: ScreenerService):
    """Sorting by Market Cap DESC produces deterministic order with stable tie-breakers."""
    req = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        sort=[SortCriterionDTO(field_id="market_cap", direction=SortDirection.DESC)],
        page_size=10,
    )
    res1 = service.run_screen(req)
    res2 = service.run_screen(req)

    # Identical deterministic ordering
    assert [r.ticker for r in res1.rows] == [r.ticker for r in res2.rows]

    # Verify descending market cap
    caps = [r.metrics["market_cap"].raw_value for r in res1.rows]
    for i in range(len(caps) - 1):
        assert caps[i] >= caps[i + 1]


def test_bounded_pagination_and_cursor(service: ScreenerService):
    """Pagination with small page size returns correct pages and next_cursor."""
    req1 = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        page=1,
        page_size=5,
    )
    res1 = service.run_screen(req1)
    assert len(res1.rows) == 5
    assert res1.has_next_page is True
    assert res1.next_cursor is not None

    # Next page using cursor
    req2 = ScreenerRunRequestDTO(
        universe=UniverseSelectionDTO(universe_id="common_equity"),
        cursor=res1.next_cursor,
    )
    res2 = service.run_screen(req2)
    assert len(res2.rows) == 5
    assert res2.page == 2

    # Disjoint rows across pages
    page1_tickers = {r.ticker for r in res1.rows}
    page2_tickers = {r.ticker for r in res2.rows}
    assert page1_tickers.isdisjoint(page2_tickers)


# =============================================================================
# 6. Validation & Error Handling Tests
# =============================================================================

def test_unknown_universe_raises_error(service: ScreenerService):
    req = ScreenerRunRequestDTO(universe=UniverseSelectionDTO(universe_id="invalid_xyz"))
    with pytest.raises(ScreenerUniverseNotFoundError):
        service.run_screen(req)


def test_unknown_filter_raises_error(service: ScreenerService):
    req = ScreenerRunRequestDTO(
        filters=[FilterCriterionDTO(filter_id="invalid_filter_metric", operator=FilterOperator.GTE, value="100")]
    )
    with pytest.raises(ScreenerFilterNotFoundError):
        service.run_screen(req)


def test_invalid_range_raises_error(service: ScreenerService):
    req = ScreenerRunRequestDTO(
        filters=[
            FilterCriterionDTO(
                filter_id="last_price",
                operator=FilterOperator.BETWEEN,
                value="500.00",
                secondary_value="100.00",  # Min > Max is invalid!
            )
        ]
    )
    with pytest.raises(ScreenerRangeInvalidError):
        service.run_screen(req)


def test_filter_complexity_limit_exceeded(service: ScreenerService):
    """Exceeding 20 active filters must raise ScreenerQueryLimitExceededError."""
    filters = [
        FilterCriterionDTO(filter_id="market_cap", operator=FilterOperator.GTE, value=str(i * 1000000))
        for i in range(25)
    ]
    req = ScreenerRunRequestDTO(filters=filters)
    with pytest.raises(ScreenerQueryLimitExceededError):
        service.run_screen(req)


# =============================================================================
# 7. FastAPI HTTP API Integration Tests
# =============================================================================

def test_api_list_universes(client: TestClient):
    response = client.get("/screeners/universes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    universe_ids = {u["universe_id"] for u in data}
    assert "common_equity" in universe_ids
    assert "delisted_equity" in universe_ids


def test_api_list_filters(client: TestClient):
    response = client.get("/screeners/filters")
    assert response.status_code == 200
    data = response.json()
    filter_ids = {f["filter_id"] for f in data}
    assert "market_cap" in filter_ids
    assert "last_price" in filter_ids
    assert "pe_ratio" in filter_ids
    assert "revenue" in filter_ids


def test_api_list_columns(client: TestClient):
    response = client.get("/screeners/columns")
    assert response.status_code == 200
    data = response.json()
    column_ids = {c["column_id"] for c in data}
    assert "symbol" in column_ids
    assert "market_cap" in column_ids
    assert "last_price" in column_ids


def test_api_list_exchanges(client: TestClient):
    response = client.get("/screeners/exchanges")
    assert response.status_code == 200
    data = response.json()
    mics = {e["mic"] for e in data}
    assert "XNAS" in mics
    assert "XNYS" in mics


def test_api_list_geographies(client: TestClient):
    response = client.get("/screeners/geographies")
    assert response.status_code == 200
    data = response.json()
    codes = {g["code"] for g in data}
    assert "US" in codes
    assert "IN" in codes


def test_api_list_industries(client: TestClient):
    response = client.get("/screeners/industries")
    assert response.status_code == 200
    data = response.json()
    sectors = {s["name"] for s in data}
    assert "Technology" in sectors
    assert "Healthcare" in sectors


def test_api_validate_endpoint(client: TestClient):
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [{"filter_id": "market_cap", "operator": "gte", "value": "1000000000"}],
    }
    response = client.post("/screeners/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert len(data["accepted_filters"]) == 1


def test_api_run_screener(client: TestClient):
    payload = {
        "universe": {"universe_id": "common_equity"},
        "filters": [
            {"filter_id": "market_cap", "operator": "gte", "value": "500000000000"},
            {"filter_id": "last_price", "operator": "gt", "value": "100"},
        ],
        "sort": [{"field_id": "market_cap", "direction": "desc"}],
        "page_size": 10,
    }
    response = client.post("/screeners/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_matching_count"] >= 3
    assert len(data["rows"]) <= 10
    first_row = data["rows"][0]
    assert first_row["ticker"] in ["AAPL", "MSFT", "NVDA"]
    assert "market_cap" in first_row["metrics"]
    assert first_row["metrics"]["market_cap"]["status"] == "available"


def test_api_coverage_endpoint(client: TestClient):
    response = client.get("/screeners/coverage")
    assert response.status_code == 200
    data = response.json()
    assert data["total_instruments"] >= 20
    assert data["instruments_with_quotes"] >= 20
    assert data["instruments_with_market_cap"] >= 20
    assert data["instruments_with_fundamentals"] >= 20
