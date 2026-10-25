"""Comprehensive Automated Test Suite for ATLAS Stage 82:
Company Financial Statements: Income Statements, Balance Sheets, Cash Flow Statements,
Standardized Accounting Taxonomies, Period Derivations, Trailing-Twelve-Month,
Restatements, Comparisons, Common-Size Analysis, and Diagnostic Reconciliations.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from atlas.auth import AuthPrincipal
from atlas.companies import Company, CompanyService
from atlas.companies.statements import (
    BALANCE_SHEET_HIERARCHY,
    CASH_FLOW_HIERARCHY,
    INCOME_STATEMENT_HIERARCHY,
    CompanyStatementsRepository,
    CompanyStatementsService,
    ComparisonMode,
    DerivationKind,
    DiagnosticStatus,
    ScaleType,
    StatementPeriodType,
    StatementType,
    calculate_common_size,
    calculate_percentage_change,
    calculate_ttm_annual_bridge,
    calculate_ttm_sum,
    calculate_yoy_absolute_change,
    derive_q4_from_annual_and_9m,
    derive_standalone_quarter_value,
    evaluate_balance_sheet_diagnostics,
    evaluate_cash_flow_diagnostics,
    format_financial_value,
)
from atlas.entities.models import Entity
from httpx import ASGITransport, AsyncClient

from atlas_api.app import create_app
from atlas_api.auth.dependencies import get_current_user
from atlas_api.authorization.dependencies import get_authorization_context
from atlas_api.dependencies import get_db_session
from atlas_api.routers.companies import get_company_service
from atlas_api.routers.company_statements import get_statements_service

APPLE_ID = uuid.UUID("c0000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_principal():
    return AuthPrincipal(
        sub=str(uuid.uuid4()),
        email="analyst@atlas.financial",
    )


@pytest.fixture
def mock_company_service():
    service = MagicMock(spec=CompanyService)
    apple = Company(
        entity_id=APPLE_ID,
        legal_name="Apple Inc.",
        short_name="Apple",
        organization_type="public_company",
        status="active",
    )
    entity = Entity(
        entity_id=APPLE_ID,
        entity_type="company",
        canonical_name="apple_inc",
        display_name="Apple Inc.",
    )
    service.get_company = AsyncMock(side_effect=lambda cid: (entity, apple) if cid == APPLE_ID else None)
    return service


@pytest.fixture
def app_instance(mock_principal, mock_company_service):
    app = create_app()
    app.dependency_overrides[get_current_user] = lambda: mock_principal
    mock_authz = MagicMock()
    mock_authz.has_permission.return_value = True
    app.dependency_overrides[get_authorization_context] = lambda: mock_authz
    app.dependency_overrides[get_company_service] = lambda: mock_company_service
    app.dependency_overrides[get_statements_service] = lambda: CompanyStatementsService(CompanyStatementsRepository())
    async def mock_db_session():
        yield AsyncMock()
    app.dependency_overrides[get_db_session] = mock_db_session
    return app


# =============================================================================
# 1. Accounting Taxonomy & Hierarchy Tests
# =============================================================================


class TestAccountingTaxonomy:
    """Verifies canonical accounting taxonomy, concept hierarchy, and stable IDs."""

    def test_income_statement_hierarchy_structure(self):
        concept_ids = [node.concept_id for node in INCOME_STATEMENT_HIERARCHY]
        assert "revenue" in concept_ids
        assert "cost_of_revenue" in concept_ids
        assert "gross_profit" in concept_ids
        assert "operating_income" in concept_ids
        assert "net_income" in concept_ids
        assert "basic_eps" in concept_ids
        assert "diluted_eps" in concept_ids

        # Check hierarchy relations
        prod_rev = next(n for n in INCOME_STATEMENT_HIERARCHY if n.concept_id == "product_revenue")
        assert prod_rev.parent_id == "revenue"
        assert prod_rev.hierarchy_level == 1

        gp = next(n for n in INCOME_STATEMENT_HIERARCHY if n.concept_id == "gross_profit")
        assert gp.is_total is True

    def test_balance_sheet_hierarchy_structure(self):
        concept_ids = [node.concept_id for node in BALANCE_SHEET_HIERARCHY]
        assert "cash_and_cash_equivalents" in concept_ids
        assert "current_assets" in concept_ids
        assert "total_assets" in concept_ids
        assert "current_liabilities" in concept_ids
        assert "total_liabilities" in concept_ids
        assert "total_equity" in concept_ids
        assert "total_liabilities_and_equity" in concept_ids

        tot_assets = next(n for n in BALANCE_SHEET_HIERARCHY if n.concept_id == "total_assets")
        assert tot_assets.is_total is True

    def test_cash_flow_hierarchy_structure(self):
        concept_ids = [node.concept_id for node in CASH_FLOW_HIERARCHY]
        assert "operating_cash_flow" in concept_ids
        assert "capital_expenditures" in concept_ids
        assert "investing_cash_flow" in concept_ids
        assert "financing_cash_flow" in concept_ids
        assert "net_change_in_cash" in concept_ids
        assert "ending_cash_balance" in concept_ids


# =============================================================================
# 2. Exact Decimal Precision & Financial Scaling Tests
# =============================================================================


class TestPrecisionAndScaling:
    """Verifies exact Decimal arithmetic, negative parentheses, and display scale formatting."""

    def test_lossless_decimal_formatting_in_billions(self):
        val = Decimal("391035000000")  # Apple FY2024 Revenue
        formatted, scale_used = format_financial_value(val, scale=ScaleType.BILLIONS)
        assert formatted == "391.04B"
        assert scale_used == "billions"

    def test_lossless_decimal_formatting_in_millions(self):
        val = Decimal("93736000000")  # Apple FY2024 Net Income
        formatted, scale_used = format_financial_value(val, scale=ScaleType.MILLIONS)
        assert formatted == "93,736.00M"
        assert scale_used == "millions"

    def test_negative_accounting_parentheses(self):
        val = Decimal("-9458000000")  # Negative CapEx
        formatted, _ = format_financial_value(val, scale=ScaleType.BILLIONS)
        assert formatted == "(9.46B)"

    def test_eps_not_scaled_to_millions(self):
        eps_val = Decimal("6.08")
        formatted, scale_used = format_financial_value(eps_val, unit_category="currency_per_share", scale=ScaleType.MILLIONS)
        assert formatted == "$6.08"
        assert scale_used == "exact"

        neg_eps = Decimal("-1.25")
        neg_formatted, _ = format_financial_value(neg_eps, unit_category="currency_per_share")
        assert neg_formatted == "($1.25)"

    def test_shares_formatted_in_millions(self):
        shares = Decimal("15408000000")  # 15.4 billion shares
        formatted, scale_used = format_financial_value(shares, unit_category="shares")
        assert formatted == "15,408.00M"
        assert scale_used == "millions"

    def test_zero_distinguished_from_missing(self):
        zero_formatted, _ = format_financial_value(Decimal("0"))
        assert zero_formatted == "0.00M"

        none_formatted, _ = format_financial_value(None)
        assert none_formatted == "—"


# =============================================================================
# 3. Quarterly & TTM Derivation Tests
# =============================================================================


class TestDerivationsAndTTM:
    """Verifies mathematical correctness of YTD quarter derivation and TTM rules."""

    def test_standalone_quarter_from_ytd(self):
        # Q2 standalone = 6M YTD - 3M YTD
        ytd_6m = Decimal("210300000000")
        ytd_3m = Decimal("119575000000")
        q2_standalone = derive_standalone_quarter_value(ytd_6m, ytd_3m)
        assert q2_standalone == Decimal("90725000000")

    def test_q4_from_annual_and_9m(self):
        # Q4 = FY - 9M YTD
        fy = Decimal("391035000000")
        ytd_9m = Decimal("296105000000")
        q4_derived = derive_q4_from_annual_and_9m(fy, ytd_9m)
        assert q4_derived == Decimal("94930000000")

    def test_quarter_derivation_missing_returns_none(self):
        assert derive_standalone_quarter_value(Decimal("100"), None) is None
        assert derive_standalone_quarter_value(None, Decimal("50")) is None

    def test_valid_ttm_four_quarters_sum(self):
        # Apple FY2024 four quarters: Q1 $119.58B, Q2 $90.75B, Q3 $85.78B, Q4 $94.93B
        q1 = Decimal("119575000000")
        q2 = Decimal("90753000000")
        q3 = Decimal("85777000000")
        q4 = Decimal("94930000000")
        quarters = [q1, q2, q3, q4]

        ttm_val, is_valid, msg = calculate_ttm_sum(quarters)
        assert is_valid is True
        assert ttm_val == Decimal("391035000000")
        assert "4 consecutive standalone quarters" in msg

    def test_ttm_rejects_missing_quarters(self):
        # Only 3 quarters available
        quarters = [Decimal("100"), Decimal("90"), Decimal("85")]
        val, is_valid, msg = calculate_ttm_sum(quarters)
        assert is_valid is False
        assert val is None
        assert "Expected 4 quarters" in msg

        # 4 quarters with one None
        quarters_with_gap = [Decimal("100"), None, Decimal("85"), Decimal("95")]
        val, is_valid, msg = calculate_ttm_sum(quarters_with_gap)
        assert is_valid is False
        assert val is None
        assert "Missing 1 quarter" in msg

    def test_valid_ttm_annual_bridge(self):
        # TTM = FY_{prior} + YTD_{curr} - YTD_{prior}
        fy_prev = Decimal("383285000000")
        ytd_curr = Decimal("296105000000")
        ytd_prior = Decimal("293787000000")
        ttm_bridge, is_valid, _ = calculate_ttm_annual_bridge(fy_prev, ytd_curr, ytd_prior)
        assert is_valid is True
        assert ttm_bridge == Decimal("385603000000")


# =============================================================================
# 4. Period Comparisons & Common Size Tests
# =============================================================================


class TestComparisonsAndCommonSize:
    """Verifies YoY/QoQ absolute and percentage changes and common-size analysis."""

    def test_yoy_absolute_change(self):
        fy24 = Decimal("391035000000")
        fy23 = Decimal("383285000000")
        diff = calculate_yoy_absolute_change(fy24, fy23)
        assert diff == Decimal("7750000000")

    def test_positive_yoy_percentage_change(self):
        fy24 = Decimal("391035000000")
        fy23 = Decimal("383285000000")
        pct, is_nm, formatted = calculate_percentage_change(fy24, fy23)
        assert is_nm is False
        assert formatted == "+2.0%"

    def test_negative_percentage_change(self):
        fy23 = Decimal("383285000000")
        fy22 = Decimal("394328000000")
        pct, is_nm, formatted = calculate_percentage_change(fy23, fy22)
        assert is_nm is False
        assert formatted == "(2.8%)"

    def test_zero_baseline_returns_not_meaningful(self):
        pct, is_nm, formatted = calculate_percentage_change(Decimal("100"), Decimal("0"))
        assert is_nm is True
        assert formatted == "N/M"

    def test_negative_baseline_returns_not_meaningful(self):
        # Negative base percentage change is mathematically misleading in accounting
        pct, is_nm, formatted = calculate_percentage_change(Decimal("50"), Decimal("-100"))
        assert is_nm is True
        assert formatted == "N/M"

    def test_common_size_income_statement(self):
        revenue = Decimal("391035000000")
        cogs = Decimal("210352000000")
        net_inc = Decimal("93736000000")

        pct_cogs, fmt_cogs = calculate_common_size(cogs, revenue)
        assert fmt_cogs == "53.8%"

        pct_ni, fmt_ni = calculate_common_size(net_inc, revenue)
        assert fmt_ni == "24.0%"

    def test_common_size_zero_denominator_returns_not_meaningful(self):
        pct, fmt = calculate_common_size(Decimal("50"), Decimal("0"))
        assert fmt == "N/M"


# =============================================================================
# 5. Accounting Consistency Diagnostics Tests
# =============================================================================


class TestAccountingDiagnostics:
    """Verifies Balance Sheet and Cash Flow consistency diagnostic checks."""

    def test_balanced_balance_sheet(self):
        facts = {
            "total_assets": Decimal("364980000000"),
            "total_liabilities": Decimal("308030000000"),
            "total_equity": Decimal("56950000000"),
        }
        res = evaluate_balance_sheet_diagnostics(facts)
        assert res.is_balanced is True
        assert res.status == DiagnosticStatus.CONSISTENT
        assert res.balance_difference == Decimal("0")

    def test_unbalanced_balance_sheet_flagged(self):
        facts = {
            "total_assets": Decimal("364980000000"),
            "total_liabilities": Decimal("300000000000"),
            "total_equity": Decimal("56950000000"),  # Sum = 356.95B (difference = 8.03B)
        }
        res = evaluate_balance_sheet_diagnostics(facts)
        assert res.is_balanced is False
        assert res.status == DiagnosticStatus.REQUIRES_REVIEW
        assert res.balance_difference == Decimal("8030000000")

    def test_reconciled_cash_flow(self):
        facts = {
            "operating_cash_flow": Decimal("118254000000"),
            "investing_cash_flow": Decimal("2484000000"),
            "financing_cash_flow": Decimal("-115682000000"),
            "net_change_in_cash": Decimal("5056000000"),
            "cash_at_beginning_of_period": Decimal("29965000000"),
            "ending_cash_balance": Decimal("35021000000"),
        }
        res = evaluate_cash_flow_diagnostics(facts)
        assert res.is_balanced is True
        assert res.status == DiagnosticStatus.CONSISTENT


# =============================================================================
# 6. Service & Repository Multi-Period Integration Tests
# =============================================================================


class TestStatementServiceIntegration:
    """Verifies end-to-end service orchestration across multi-period annual and quarterly statements."""

    @pytest.fixture(autouse=True)
    def setup_repo(self):
        self.repo = CompanyStatementsRepository()
        self.service = CompanyStatementsService(self.repo)

    @pytest.mark.asyncio
    async def test_get_statement_catalog(self):
        catalog = await self.service.get_statement_catalog(APPLE_ID)
        assert catalog.company_entity_id == APPLE_ID
        assert StatementType.INCOME_STATEMENT in catalog.available_statements
        assert StatementType.BALANCE_SHEET in catalog.available_statements
        assert StatementType.CASH_FLOW_STATEMENT in catalog.available_statements
        assert 2024 in catalog.available_fiscal_years
        assert 2021 in catalog.available_fiscal_years
        assert len(catalog.available_periods) >= 8

    @pytest.mark.asyncio
    async def test_annual_income_statement_multi_period(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.INCOME_STATEMENT,
            period_type=StatementPeriodType.ANNUAL,
            scale=ScaleType.BILLIONS,
            max_periods=4,
        )
        assert resp.company_entity_id == APPLE_ID
        assert len(resp.periods) == 4
        # Chronological order
        labels = [p.label for p in resp.periods]
        assert labels == ["FY2021", "FY2022", "FY2023", "FY2024"]

        # Check Revenue row
        rev_row = next(r for r in resp.rows if r.concept_id == "revenue")
        assert rev_row.cells["FY2024"].formatted_value == "391.04B"
        assert rev_row.cells["FY2023"].formatted_value == "383.29B"
        assert rev_row.cells["FY2022"].formatted_value == "394.33B"
        assert rev_row.cells["FY2021"].formatted_value == "365.82B"

    @pytest.mark.asyncio
    async def test_quarterly_income_statement(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.INCOME_STATEMENT,
            period_type=StatementPeriodType.QUARTERLY,
            scale=ScaleType.BILLIONS,
            max_periods=4,
        )
        assert len(resp.periods) == 4
        assert [p.label for p in resp.periods] == ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]

        rev_row = next(r for r in resp.rows if r.concept_id == "revenue")
        assert rev_row.cells["Q1-2024"].formatted_value == "119.58B"
        assert rev_row.cells["Q4-2024"].formatted_value == "94.93B"

    @pytest.mark.asyncio
    async def test_ttm_derivation_income_statement(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.INCOME_STATEMENT,
            period_type=StatementPeriodType.TTM,
            scale=ScaleType.BILLIONS,
        )
        assert len(resp.periods) == 1
        assert resp.periods[0].period_type == StatementPeriodType.TTM
        assert resp.periods[0].is_derived is True
        assert len(resp.periods[0].derivation_lineage) == 4

        # TTM Revenue = sum of 4 quarters = 391.04B
        rev_row = next(r for r in resp.rows if r.concept_id == "revenue")
        ttm_cell = next(iter(rev_row.cells.values()))
        assert ttm_cell.formatted_value == "391.04B"
        assert ttm_cell.derivation_kind == DerivationKind.DERIVED_TTM

    @pytest.mark.asyncio
    async def test_ttm_on_balance_sheet_strictly_rejected(self):
        with pytest.raises(ValueError, match="mathematically invalid"):
            await self.service.get_financial_statement(
                company_id=APPLE_ID,
                statement_type=StatementType.BALANCE_SHEET,
                period_type=StatementPeriodType.TTM,
            )

    @pytest.mark.asyncio
    async def test_balance_sheet_annual_point_in_time(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.BALANCE_SHEET,
            period_type=StatementPeriodType.ANNUAL,
            scale=ScaleType.BILLIONS,
            max_periods=4,
        )
        assert len(resp.periods) == 4
        assert resp.diagnostics.is_balanced is True
        assert resp.diagnostics.status == DiagnosticStatus.CONSISTENT

        assets_row = next(r for r in resp.rows if r.concept_id == "total_assets")
        assert assets_row.cells["FY2024"].formatted_value == "364.80B"

    @pytest.mark.asyncio
    async def test_cash_flow_statement_reconciliation(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.CASH_FLOW_STATEMENT,
            period_type=StatementPeriodType.ANNUAL,
            scale=ScaleType.BILLIONS,
            max_periods=4,
        )
        assert len(resp.periods) == 4
        assert resp.diagnostics.is_balanced is True

        ocf_row = next(r for r in resp.rows if r.concept_id == "operating_cash_flow")
        assert ocf_row.cells["FY2024"].formatted_value == "118.24B"

    @pytest.mark.asyncio
    async def test_income_statement_common_size(self):
        resp = await self.service.get_financial_statement(
            company_id=APPLE_ID,
            statement_type=StatementType.INCOME_STATEMENT,
            period_type=StatementPeriodType.ANNUAL,
            comparison_mode=ComparisonMode.COMMON_SIZE,
            scale=ScaleType.BILLIONS,
            max_periods=4,
        )
        # Check that comparison_formatted contains common-size percentages
        cogs_row = next(r for r in resp.rows if r.concept_id == "cost_of_revenue")
        assert cogs_row.cells["FY2024"].comparison_formatted == "53.8%"

        ni_row = next(r for r in resp.rows if r.concept_id == "net_income")
        assert ni_row.cells["FY2024"].comparison_formatted == "24.0%"


# =============================================================================
# 7. FastAPI HTTP API Endpoint Tests
# =============================================================================


class TestCompanyStatementsAPI:
    """Verifies HTTP API routes under /api/v1/companies/{company_id}/statements."""

    @pytest.mark.asyncio
    async def test_get_catalog_endpoint(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(f"/api/v1/companies/{APPLE_ID}/statements/catalog")
            assert response.status_code == 200
            data = response.json()
            assert data["company_entity_id"] == str(APPLE_ID)
            assert "income_statement" in data["available_statements"]
            assert "balance_sheet" in data["available_statements"]
            assert "cash_flow_statement" in data["available_statements"]
            assert 2024 in data["available_fiscal_years"]

    @pytest.mark.asyncio
    async def test_get_income_statement_endpoint(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                f"/api/v1/companies/{APPLE_ID}/statements/income",
                params={"period_type": "annual", "scale": "billions", "max_periods": 4},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["statement_type"] == "income_statement"
            assert len(data["periods"]) == 4
            assert len(data["rows"]) > 0

    @pytest.mark.asyncio
    async def test_get_balance_sheet_endpoint(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                f"/api/v1/companies/{APPLE_ID}/statements/balance-sheet",
                params={"period_type": "annual", "scale": "billions"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["statement_type"] == "balance_sheet"
            assert data["diagnostics"]["is_balanced"] is True

    @pytest.mark.asyncio
    async def test_get_balance_sheet_ttm_rejected_by_api(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                f"/api/v1/companies/{APPLE_ID}/statements/balance-sheet",
                params={"period_type": "ttm"},
            )
            assert response.status_code == 400
            assert "mathematically invalid" in response.text

    @pytest.mark.asyncio
    async def test_get_cash_flow_endpoint(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                f"/api/v1/companies/{APPLE_ID}/statements/cash-flow",
                params={"period_type": "annual", "scale": "billions"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["statement_type"] == "cash_flow_statement"

    @pytest.mark.asyncio
    async def test_get_sources_metadata_endpoint(self, app_instance):
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                f"/api/v1/companies/{APPLE_ID}/statements/income_statement/sources"
            )
            assert response.status_code == 200
            data = response.json()
            assert data["statement_type"] == "income_statement"
            assert len(data["sources"]) > 0
            assert "filing_name" in data["sources"][0]

    @pytest.mark.asyncio
    async def test_missing_company_returns_404(self, app_instance):
        unknown_id = uuid.uuid4()
        transport = ASGITransport(app=app_instance)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(f"/api/v1/companies/{unknown_id}/statements/catalog")
            assert response.status_code == 404
