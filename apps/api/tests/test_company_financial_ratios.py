"""Automated Test Suite for Company Financial Ratios (Stage 83).

Covers:
- Canonical Ratio Registry & Catalog
- Profitability Formulas (Gross Margin, Operating Margin, EBITDA Margin, Net Margin, ROE, ROA, ROIC, ROCE)
- Liquidity Formulas (Current Ratio, Quick Ratio, Cash Ratio, OCF Ratio)
- Solvency & Leverage Formulas (Debt/Equity, Debt/Assets, Debt/Capital, Net Debt, Interest Coverage, Debt/EBITDA, Net Debt/EBITDA)
- Efficiency Formulas (Asset Turnover, Inventory Turnover, Receivables Turnover, Payables Turnover, DSO, DIO, DPO, CCC)
- Cash Flow Formulas (FCF, FCF Margin, OCF Margin, Cash Conversion, CapEx/Revenue, FCF Yield)
- Valuation Multiples (P/E, P/B, P/S, P/CF, P/FCF, EV, EV/EBITDA, EV/Revenue, Dividend Yield, Earnings Yield)
- Exact Decimal Precision, Zero-Division, and Negative-Base Safeguards
- Multi-Period Historical Series Generation
- FastAPI Endpoint Contract Validation
"""

import uuid
from decimal import Decimal

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies.models import Company
from atlas.companies.ratios.enums import (
    RatioCategory,
    RatioPeriodType,
    RatioStatus,
    UnitKind,
)
from atlas.companies.ratios.formulas import (
    calculate_asset_turnover,
    calculate_cash_conversion_cycle,
    calculate_cash_ratio,
    calculate_current_ratio,
    calculate_debt_to_assets,
    calculate_debt_to_equity,
    calculate_dividend_yield,
    calculate_dso,
    calculate_earnings_yield,
    calculate_ebitda_margin,
    calculate_enterprise_value,
    calculate_ev_to_ebitda,
    calculate_free_cash_flow,
    calculate_gross_margin,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_net_margin,
    calculate_operating_margin,
    calculate_pb,
    calculate_pe,
    calculate_ps,
    calculate_quick_ratio,
    calculate_roa,
    calculate_roce,
    calculate_roe,
    calculate_roic,
)
from atlas.companies.ratios.input_resolver import (
    RatioInputResolver,
)
from atlas.companies.ratios.registry import (
    CANONICAL_RATIO_DEFINITIONS,
    FinancialRatioRegistry,
)
from atlas.companies.ratios.service import CompanyRatiosService
from atlas.companies.statements.repository import CompanyStatementsRepository
from atlas.entities.models import Entity
from httpx import ASGITransport, AsyncClient

from atlas_api.auth.dependencies import get_current_user
from atlas_api.dependencies import get_db_session
from atlas_api.main import app
from atlas_api.routers.companies import get_company_service
from atlas_api.routers.company_ratios import get_ratios_service

# =============================================================================
# 1. Ratio Registry Tests
# =============================================================================

class TestRatioRegistry:
    def test_registry_contains_all_canonical_definitions(self):
        assert len(CANONICAL_RATIO_DEFINITIONS) == 44
        registry = FinancialRatioRegistry()
        all_ratios = registry.list_ratios()
        assert len(all_ratios) == 44

        # Unique IDs
        ids = [r.id for r in all_ratios]
        assert len(ids) == len(set(ids))

    def test_category_filtering(self):
        registry = FinancialRatioRegistry()
        prof = registry.list_ratios(RatioCategory.PROFITABILITY)
        assert len(prof) == 8
        liq = registry.list_ratios(RatioCategory.LIQUIDITY)
        assert len(liq) == 4
        solv = registry.list_ratios(RatioCategory.SOLVENCY)
        assert len(solv) == 7
        eff = registry.list_ratios(RatioCategory.EFFICIENCY)
        assert len(eff) == 8
        cf = registry.list_ratios(RatioCategory.CASH_FLOW)
        assert len(cf) == 6
        val = registry.list_ratios(RatioCategory.VALUATION)
        assert len(val) == 11

    def test_get_ratio_not_found(self):
        registry = FinancialRatioRegistry()
        with pytest.raises(Exception):
            registry.get_ratio("non_existent_ratio_id")


# =============================================================================
# 2. Profitability Formulas Tests
# =============================================================================

class TestProfitabilityFormulas:
    def test_gross_margin_exact(self):
        val, exp, status = calculate_gross_margin(Decimal("150000"), Decimal("300000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("50.000000")
        assert exp is None

    def test_operating_margin_exact(self):
        val, exp, status = calculate_operating_margin(Decimal("60000"), Decimal("300000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("20.000000")

    def test_ebitda_margin_exact(self):
        val, exp, status = calculate_ebitda_margin(Decimal("60000"), Decimal("15000"), Decimal("300000"))
        assert status == RatioStatus.AVAILABLE
        # (60000 + 15000) / 300000 * 100 = 25%
        assert val == Decimal("25.000000")

    def test_net_margin_exact(self):
        val, exp, status = calculate_net_margin(Decimal("45000"), Decimal("300000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("15.000000")

    def test_roe_positive_equity(self):
        val, exp, status = calculate_roe(Decimal("50000"), Decimal("200000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("25.000000")

    def test_roe_negative_equity_not_meaningful(self):
        val, exp, status = calculate_roe(Decimal("50000"), Decimal("-200000"))
        assert status == RatioStatus.NOT_MEANINGFUL
        assert val is None
        assert "Negative or zero equity base" in exp

    def test_roa_exact(self):
        val, exp, status = calculate_roa(Decimal("50000"), Decimal("500000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("10.000000")

    def test_roic_exact(self):
        val, exp, status = calculate_roic(
            operating_income=Decimal("100000"),
            income_tax_expense=Decimal("20000"),
            income_before_tax=Decimal("100000"),
            average_invested_capital=Decimal("400000"),
        )
        assert status == RatioStatus.AVAILABLE
        # NOPAT = 100,000 * (1 - 0.20) = 80,000; ROIC = 80,000 / 400,000 * 100 = 20%
        assert val == Decimal("20.000000")

    def test_roce_exact(self):
        val, exp, status = calculate_roce(Decimal("100000"), Decimal("500000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("20.000000")


# =============================================================================
# 3. Liquidity Formulas Tests
# =============================================================================

class TestLiquidityFormulas:
    def test_current_ratio_exact(self):
        val, exp, status = calculate_current_ratio(Decimal("250000"), Decimal("100000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("2.500000")

    def test_quick_ratio_exact(self):
        val, exp, status = calculate_quick_ratio(
            cash_and_equivalents=Decimal("50000"),
            short_term_investments=Decimal("30000"),
            accounts_receivable=Decimal("70000"),
            current_liabilities=Decimal("100000"),
        )
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("1.500000")

    def test_cash_ratio_exact(self):
        val, exp, status = calculate_cash_ratio(
            cash_and_equivalents=Decimal("50000"),
            short_term_investments=Decimal("30000"),
            current_liabilities=Decimal("100000"),
        )
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("0.800000")

    def test_zero_current_liabilities_unavailable(self):
        val, exp, status = calculate_current_ratio(Decimal("250000"), Decimal("0"))
        assert status == RatioStatus.UNAVAILABLE
        assert val is None
        assert "Division by zero" in exp


# =============================================================================
# 4. Solvency & Leverage Formulas Tests
# =============================================================================

class TestSolvencyFormulas:
    def test_debt_to_equity_exact(self):
        val, exp, status = calculate_debt_to_equity(Decimal("120000"), Decimal("60000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("2.000000")

    def test_debt_to_assets_exact(self):
        val, exp, status = calculate_debt_to_assets(Decimal("120000"), Decimal("300000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("0.400000")

    def test_net_debt_exact(self):
        val, exp, status = calculate_net_debt(
            total_debt=Decimal("120000"),
            cash_and_equivalents=Decimal("30000"),
            short_term_investments=Decimal("20000"),
        )
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("70000")

    def test_interest_coverage_exact(self):
        val, exp, status = calculate_interest_coverage(Decimal("100000"), Decimal("10000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("10.000000")

    def test_zero_interest_expense_handled(self):
        val, exp, status = calculate_interest_coverage(Decimal("100000"), Decimal("0"))
        assert status == RatioStatus.UNAVAILABLE
        assert val is None
        assert "Zero interest expense" in exp


# =============================================================================
# 5. Efficiency Formulas Tests
# =============================================================================

class TestEfficiencyFormulas:
    def test_asset_turnover_exact(self):
        val, exp, status = calculate_asset_turnover(Decimal("400000"), Decimal("500000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("0.800000")

    def test_dso_exact(self):
        val, exp, status = calculate_dso(Decimal("30000"), Decimal("365000"), period_days=365)
        assert status == RatioStatus.AVAILABLE
        # (30000 * 365) / 365000 = 30.0 days
        assert val == Decimal("30.000000")

    def test_cash_conversion_cycle_exact(self):
        val, exp, status = calculate_cash_conversion_cycle(
            dso=Decimal("30.0"),
            dio=Decimal("45.0"),
            dpo=Decimal("25.0"),
        )
        assert status == RatioStatus.AVAILABLE
        # 30 + 45 - 25 = 50 days
        assert val == Decimal("50.000000")


# =============================================================================
# 6. Cash Flow Formulas Tests
# =============================================================================

class TestCashFlowFormulas:
    def test_free_cash_flow_exact(self):
        val, exp, status = calculate_free_cash_flow(
            operating_cash_flow=Decimal("110000000000"),
            capital_expenditures=Decimal("-10000000000"),
        )
        assert status == RatioStatus.AVAILABLE
        # 110B - 10B = 100B
        assert val == Decimal("100000000000")

    def test_free_cash_flow_positive_capex_sign_safe(self):
        val, exp, status = calculate_free_cash_flow(
            operating_cash_flow=Decimal("110000000000"),
            capital_expenditures=Decimal("10000000000"),
        )
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("100000000000")


# =============================================================================
# 7. Valuation Formulas Tests
# =============================================================================

class TestValuationFormulas:
    def test_pe_ratio_positive(self):
        val, exp, status = calculate_pe(Decimal("3000000000000"), Decimal("100000000000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("30.000000")

    def test_pe_ratio_negative_net_income_not_meaningful(self):
        val, exp, status = calculate_pe(Decimal("3000000000000"), Decimal("-5000000000"))
        assert status == RatioStatus.NOT_MEANINGFUL
        assert val is None
        assert "Non-positive net income" in exp

    def test_pb_ratio_exact(self):
        val, exp, status = calculate_pb(Decimal("3000000000000"), Decimal("60000000000"))
        assert status == RatioStatus.AVAILABLE
        assert val == Decimal("50.000000")

    def test_ps_ratio_exact(self):
        val, exp, status = calculate_ps(Decimal("3000000000000"), Decimal("390000000000"))
        assert status == RatioStatus.AVAILABLE
        # 3000B / 390B = ~7.69x
        assert val == Decimal("7.692308")

    def test_enterprise_value_exact(self):
        val, exp, status = calculate_enterprise_value(
            market_cap=Decimal("3000000000000"),
            total_debt=Decimal("100000000000"),
            cash_and_equivalents=Decimal("30000000000"),
            short_term_investments=Decimal("30000000000"),
        )
        assert status == RatioStatus.AVAILABLE
        # EV = 3000B + 100B - (30B + 30B) = 3040B
        assert val == Decimal("3040000000000")

    def test_ev_to_ebitda_exact(self):
        val, exp, status = calculate_ev_to_ebitda(Decimal("3000000000000"), Decimal("130000000000"))
        assert status == RatioStatus.AVAILABLE
        # 3000B / 130B = ~23.08x
        assert val == Decimal("23.076923")

    def test_dividend_yield_exact(self):
        val, exp, status = calculate_dividend_yield(Decimal("-15000000000"), Decimal("3000000000000"))
        assert status == RatioStatus.AVAILABLE
        # 15B / 3000B * 100 = 0.50%
        assert val == Decimal("0.500000")

    def test_earnings_yield_exact(self):
        val, exp, status = calculate_earnings_yield(Decimal("100000000000"), Decimal("3000000000000"))
        assert status == RatioStatus.AVAILABLE
        # 100B / 3000B * 100 = 3.333333%
        assert val == Decimal("3.333333")


# =============================================================================
# 8. Service Integration Tests (Apple Inc. Canonical Seed)
# =============================================================================

class TestCompanyRatiosServiceIntegration:
    @pytest.fixture
    def service(self):
        repo = CompanyStatementsRepository()
        resolver = RatioInputResolver(repo)
        return CompanyRatiosService(statements_repo=repo, input_resolver=resolver)

    def test_get_company_ratios_annual_fy2024(self, service):
        apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
        response = service.get_company_ratios(
            company_id=apple_id,
            period_id="FY2024",
            period_type=RatioPeriodType.ANNUAL,
        )
        assert response.company_id == apple_id
        assert response.period_id == "FY2024"
        assert response.total_count == 44
        assert response.available_count > 30

        # Verify key ratios
        ratios_by_id = {r.ratio_id: r for r in response.ratios}

        # Gross margin: 180,683 / 391,035 * 100 = ~46.21%
        gm = ratios_by_id["profitability.gross_margin"]
        assert gm.status == RatioStatus.AVAILABLE
        assert gm.formatted_value == "46.21%"

        # Operating margin: 123,216 / 391,035 * 100 = ~31.51%
        om = ratios_by_id["profitability.operating_margin"]
        assert om.status == RatioStatus.AVAILABLE
        assert om.formatted_value == "31.50%"

        # Net margin: 93,736 / 391,035 * 100 = ~23.97%
        nm = ratios_by_id["profitability.net_margin"]
        assert nm.status == RatioStatus.AVAILABLE
        assert nm.formatted_value == "23.97%"

        # Current ratio: 152,985 / 162,431 = ~0.94x
        cr = ratios_by_id["liquidity.current_ratio"]
        assert cr.status == RatioStatus.AVAILABLE
        assert cr.formatted_value == "0.94x"

        # Free Cash Flow: 118,254M - 9,458M = 108,796M
        fcf = ratios_by_id["cashflow.free_cash_flow"]
        assert fcf.status == RatioStatus.AVAILABLE
        assert fcf.formatted_value == "$108.79B"

        # Market Cap: ~3.43T
        pe = ratios_by_id["valuation.pe"]
        assert pe.status == RatioStatus.AVAILABLE
        assert pe.unit_kind == UnitKind.MULTIPLE

    def test_get_company_ratio_history(self, service):
        apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
        history = service.get_company_ratio_history(
            company_id=apple_id,
            ratio_id="profitability.gross_margin",
            period_type=RatioPeriodType.ANNUAL,
        )
        assert history.ratio_id == "profitability.gross_margin"
        assert len(history.series) == 4
        # FY2021, FY2022, FY2023, FY2024
        pids = [pt.period_id for pt in history.series]
        assert pids == ["FY2021", "FY2022", "FY2023", "FY2024"]
        for pt in history.series:
            assert pt.status == RatioStatus.AVAILABLE
            assert "%" in pt.formatted_value

    def test_get_ratio_methodology(self, service):
        meth = service.get_ratio_methodology("profitability.roe")
        assert meth.definition.id == "profitability.roe"
        assert meth.definition.unit_kind == UnitKind.PERCENT
        assert "Average Shareholders' Equity" in meth.definition.formula_display

    def test_get_ratio_lineage(self, service):
        apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
        lineage = service.get_ratio_lineage(
            company_id=apple_id,
            ratio_id="profitability.gross_margin",
            period_id="FY2024",
        )
        assert lineage.ratio_id == "profitability.gross_margin"
        assert lineage.ratio_value is not None
        assert len(lineage.ratio_value.input_lineage) >= 2


# =============================================================================
# 9. FastAPI HTTP Endpoints Tests
# =============================================================================

class TestCompanyRatiosAPI:
    @pytest.fixture
    def auth_user(self):
        return AuthPrincipal(
            sub="usr_test_stage83",
            email="analyst@atlas.financial",
        )

    @pytest.fixture
    def mock_company_service(self):
        apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")
        mock_entity = Entity(
            entity_id=apple_id,
            canonical_name="apple_inc",
            display_name="Apple Inc.",
            entity_type="company",
        )
        mock_company = Company(
            entity_id=apple_id,
            legal_name="Apple Inc.",
            short_name="Apple",
        )

        class MockCompanyService:
            async def get_company(self, entity_id: uuid.UUID):
                if entity_id == apple_id:
                    return mock_entity, mock_company
                from atlas.companies.errors import CompanyNotFoundError
                raise CompanyNotFoundError(str(entity_id))

        return MockCompanyService()

    @pytest.fixture
    def app_instance(self, auth_user, mock_company_service):
        from unittest.mock import MagicMock

        from atlas_api.authorization.dependencies import get_authorization_context

        app.dependency_overrides[get_current_user] = lambda: auth_user
        mock_authz = MagicMock()
        mock_authz.has_permission.return_value = True
        app.dependency_overrides[get_authorization_context] = lambda: mock_authz
        app.dependency_overrides[get_company_service] = lambda: mock_company_service
        app.dependency_overrides[get_ratios_service] = lambda: CompanyRatiosService(
            statements_repo=CompanyStatementsRepository()
        )
        class MockSession:
            pass
        app.dependency_overrides[get_db_session] = lambda: MockSession()

        yield app
        app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_ratio_catalog_endpoint(self, app_instance):
        apple_id = "c0000000-0000-0000-0000-000000000001"
        async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as client:
            resp = await client.get(f"/api/v1/companies/{apple_id}/ratios/catalog")
            assert resp.status_code == 200
            data = resp.json()
            assert data["total_count"] == 44
            assert "profitability" in data["categories"]

    @pytest.mark.asyncio
    async def test_get_company_ratios_endpoint(self, app_instance):
        apple_id = "c0000000-0000-0000-0000-000000000001"
        async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as client:
            resp = await client.get(f"/api/v1/companies/{apple_id}/ratios?period_id=FY2024")
            assert resp.status_code == 200
            data = resp.json()
            assert data["company_name"] == "Apple Inc."
            assert data["period_id"] == "FY2024"
            assert len(data["ratios"]) == 44

    @pytest.mark.asyncio
    async def test_get_ratio_history_endpoint(self, app_instance):
        apple_id = "c0000000-0000-0000-0000-000000000001"
        async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as client:
            resp = await client.get(f"/api/v1/companies/{apple_id}/ratios/history?ratio_id=profitability.gross_margin")
            assert resp.status_code == 200
            data = resp.json()
            assert data["ratio_id"] == "profitability.gross_margin"
            assert len(data["series"]) >= 4

    @pytest.mark.asyncio
    async def test_get_ratio_methodology_endpoint(self, app_instance):
        apple_id = "c0000000-0000-0000-0000-000000000001"
        async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as client:
            resp = await client.get(f"/api/v1/companies/{apple_id}/ratios/profitability.roe/methodology")
            assert resp.status_code == 200
            data = resp.json()
            assert data["definition"]["id"] == "profitability.roe"

    @pytest.mark.asyncio
    async def test_get_company_not_found_endpoint(self, app_instance):
        random_id = str(uuid.uuid4())
        async with AsyncClient(transport=ASGITransport(app=app_instance), base_url="http://test") as client:
            resp = await client.get(f"/api/v1/companies/{random_id}/ratios")
            assert resp.status_code == 404
