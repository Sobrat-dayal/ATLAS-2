"""Company Financial Ratios Service (Stage 83).

Coordinates:
- Ratio definition retrieval and category filtering
- Financial input qualification and balance sheet averaging
- Pure deterministic exact Decimal ratio calculation
- Multi-period historical ratio series generation
- Audit provenance and source fact lineage tracking
"""

from decimal import Decimal
from typing import Dict, List, Optional
from uuid import UUID

from atlas.companies.ratios.enums import (
    RatioCategory,
    RatioPeriodType,
    RatioStatus,
    UnitKind,
)
from atlas.companies.ratios.formulas import (
    calculate_asset_turnover,
    calculate_capex_to_revenue,
    calculate_cash_conversion,
    calculate_cash_conversion_cycle,
    calculate_cash_ratio,
    calculate_current_ratio,
    calculate_debt_to_assets,
    calculate_debt_to_capital,
    calculate_debt_to_ebitda,
    calculate_debt_to_equity,
    calculate_dio,
    calculate_dividend_yield,
    calculate_dpo,
    calculate_dso,
    calculate_earnings_yield,
    calculate_ebitda_margin,
    calculate_enterprise_value,
    calculate_ev_to_ebitda,
    calculate_ev_to_revenue,
    calculate_forward_pe,
    calculate_free_cash_flow,
    calculate_free_cash_flow_margin,
    calculate_free_cash_flow_yield,
    calculate_gross_margin,
    calculate_interest_coverage,
    calculate_inventory_turnover,
    calculate_net_debt,
    calculate_net_debt_to_ebitda,
    calculate_net_margin,
    calculate_operating_cash_flow_margin,
    calculate_operating_cash_flow_ratio,
    calculate_operating_margin,
    calculate_payables_turnover,
    calculate_pb,
    calculate_pe,
    calculate_price_to_cash_flow,
    calculate_price_to_free_cash_flow,
    calculate_ps,
    calculate_quick_ratio,
    calculate_receivables_turnover,
    calculate_roa,
    calculate_roce,
    calculate_roe,
    calculate_roic,
)
from atlas.companies.ratios.input_resolver import RatioInputResolver
from atlas.companies.ratios.registry import (
    FinancialRatioDefinition,
    FinancialRatioRegistry,
    default_ratio_registry,
)
from atlas.companies.ratios.schemas import (
    CompanyRatiosResponse,
    RatioCatalogResponse,
    RatioDefinitionDTO,
    RatioHistoryPointDTO,
    RatioHistoryResponse,
    RatioInputFactDTO,
    RatioLineageResponse,
    RatioMethodologyResponse,
    RatioValueDTO,
)
from atlas.companies.statements.enums import (
    ConsolidationScope,
    StatementPeriodType,
)
from atlas.companies.statements.repository import CompanyStatementsRepository


class CompanyRatiosService:
    """Core domain service for company financial ratio calculations."""

    def __init__(
        self,
        registry: Optional[FinancialRatioRegistry] = None,
        statements_repo: Optional[CompanyStatementsRepository] = None,
        input_resolver: Optional[RatioInputResolver] = None,
    ):
        self.registry = registry or default_ratio_registry
        self.statements_repo = statements_repo or CompanyStatementsRepository()
        self.input_resolver = input_resolver or RatioInputResolver(self.statements_repo)

    def get_ratio_catalog(self, category: Optional[RatioCategory] = None) -> RatioCatalogResponse:
        """Returns registered canonical financial ratios."""
        items = self.registry.list_ratios(category)
        dtos = [RatioDefinitionDTO.model_validate(item) for item in items]
        cats = [c.value for c in RatioCategory]
        return RatioCatalogResponse(
            ratios=dtos,
            total_count=len(dtos),
            categories=cats,
        )

    def get_ratio_methodology(self, ratio_id: str) -> RatioMethodologyResponse:
        """Returns detailed methodology and formula explanation for a single ratio."""
        defn = self.registry.get_ratio(ratio_id)
        notes = (
            f"Calculated using exact Decimal representation. "
            f"Denominator policy: {defn.denominator_policy.value}. "
            f"Negative policy: {defn.negative_policy.value}. "
            f"Requires balance sheet averaging: {defn.requires_balance_sheet_average}."
        )
        return RatioMethodologyResponse(
            definition=RatioDefinitionDTO.model_validate(defn),
            calculation_notes=notes,
            supported_periods=defn.supported_periods,
        )

    def calculate_single_ratio(
        self,
        defn: FinancialRatioDefinition,
        inputs: Dict[str, Optional[Decimal]],
        lineage: List[RatioInputFactDTO],
        period_id: str,
        period_type: RatioPeriodType,
    ) -> RatioValueDTO:
        """Calculates a single ratio given pre-resolved inputs."""
        rid = defn.id
        val: Optional[Decimal] = None
        explanation: Optional[str] = None
        status = RatioStatus.AVAILABLE
        num_val: Optional[Decimal] = None
        den_val: Optional[Decimal] = None

        # Period days policy: 365 for annual, 91 for quarterly
        period_days = 91 if period_type == RatioPeriodType.QUARTERLY else 365

        # ---------------------------------------------------------------------
        # 1. Profitability Ratios
        # ---------------------------------------------------------------------
        if rid == "profitability.gross_margin":
            num_val = inputs.get("gross_profit")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_gross_margin(num_val, den_val)

        elif rid == "profitability.operating_margin":
            num_val = inputs.get("operating_income")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_operating_margin(num_val, den_val)

        elif rid == "profitability.ebitda_margin":
            num_val = inputs.get("ebitda")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_ebitda_margin(
                inputs.get("operating_income"),
                inputs.get("depreciation_and_amortization"),
                den_val,
            )

        elif rid == "profitability.net_margin":
            num_val = inputs.get("net_income")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_net_margin(num_val, den_val)

        elif rid == "profitability.roe":
            num_val = inputs.get("net_income")
            den_val = inputs.get("average_equity")
            val, explanation, status = calculate_roe(num_val, den_val)

        elif rid == "profitability.roa":
            num_val = inputs.get("net_income")
            den_val = inputs.get("average_assets")
            val, explanation, status = calculate_roa(num_val, den_val)

        elif rid == "profitability.roic":
            num_val = inputs.get("operating_income")
            den_val = inputs.get("average_invested_capital")
            val, explanation, status = calculate_roic(
                inputs.get("operating_income"),
                inputs.get("income_tax_expense"),
                inputs.get("income_before_tax"),
                den_val,
            )

        elif rid == "profitability.roce":
            num_val = inputs.get("operating_income")
            den_val = inputs.get("average_capital_employed")
            val, explanation, status = calculate_roce(num_val, den_val)

        # ---------------------------------------------------------------------
        # 2. Liquidity Ratios
        # ---------------------------------------------------------------------
        elif rid == "liquidity.current_ratio":
            num_val = inputs.get("current_assets")
            den_val = inputs.get("current_liabilities")
            val, explanation, status = calculate_current_ratio(num_val, den_val)

        elif rid == "liquidity.quick_ratio":
            den_val = inputs.get("current_liabilities")
            val, explanation, status = calculate_quick_ratio(
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
                inputs.get("accounts_receivable"),
                den_val,
            )

        elif rid == "liquidity.cash_ratio":
            den_val = inputs.get("current_liabilities")
            val, explanation, status = calculate_cash_ratio(
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
                den_val,
            )

        elif rid == "liquidity.operating_cash_flow_ratio":
            num_val = inputs.get("operating_cash_flow")
            den_val = inputs.get("current_liabilities")
            val, explanation, status = calculate_operating_cash_flow_ratio(num_val, den_val)

        # ---------------------------------------------------------------------
        # 3. Solvency & Leverage Ratios
        # ---------------------------------------------------------------------
        elif rid == "solvency.debt_to_equity":
            num_val = inputs.get("total_debt")
            den_val = inputs.get("total_equity")
            val, explanation, status = calculate_debt_to_equity(num_val, den_val)

        elif rid == "solvency.debt_to_assets":
            num_val = inputs.get("total_debt")
            den_val = inputs.get("total_assets")
            val, explanation, status = calculate_debt_to_assets(num_val, den_val)

        elif rid == "solvency.debt_to_capital":
            num_val = inputs.get("total_debt")
            den_val = inputs.get("total_equity")
            val, explanation, status = calculate_debt_to_capital(num_val, den_val)

        elif rid == "solvency.net_debt":
            num_val = inputs.get("total_debt")
            val, explanation, status = calculate_net_debt(
                num_val,
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
            )

        elif rid == "solvency.interest_coverage":
            num_val = inputs.get("operating_income")
            den_val = inputs.get("interest_expense")
            val, explanation, status = calculate_interest_coverage(num_val, den_val)

        elif rid == "solvency.debt_to_ebitda":
            num_val = inputs.get("total_debt")
            den_val = inputs.get("ebitda")
            val, explanation, status = calculate_debt_to_ebitda(num_val, den_val)

        elif rid == "solvency.net_debt_to_ebitda":
            net_debt_res, _, _ = calculate_net_debt(
                inputs.get("total_debt"),
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
            )
            num_val = net_debt_res
            den_val = inputs.get("ebitda")
            val, explanation, status = calculate_net_debt_to_ebitda(num_val, den_val)

        # ---------------------------------------------------------------------
        # 4. Efficiency Ratios
        # ---------------------------------------------------------------------
        elif rid == "efficiency.asset_turnover":
            num_val = inputs.get("revenue")
            den_val = inputs.get("average_assets")
            val, explanation, status = calculate_asset_turnover(num_val, den_val)

        elif rid == "efficiency.inventory_turnover":
            num_val = inputs.get("cost_of_revenue")
            den_val = inputs.get("average_inventory")
            val, explanation, status = calculate_inventory_turnover(num_val, den_val)

        elif rid == "efficiency.receivables_turnover":
            num_val = inputs.get("revenue")
            den_val = inputs.get("average_receivables")
            val, explanation, status = calculate_receivables_turnover(num_val, den_val)

        elif rid == "efficiency.payables_turnover":
            num_val = inputs.get("cost_of_revenue")
            den_val = inputs.get("average_payables")
            val, explanation, status = calculate_payables_turnover(num_val, den_val)

        elif rid == "efficiency.dso":
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_dso(
                inputs.get("average_receivables"), den_val, period_days=period_days
            )

        elif rid == "efficiency.dio":
            den_val = inputs.get("cost_of_revenue")
            val, explanation, status = calculate_dio(
                inputs.get("average_inventory"), den_val, period_days=period_days
            )

        elif rid == "efficiency.dpo":
            den_val = inputs.get("cost_of_revenue")
            val, explanation, status = calculate_dpo(
                inputs.get("average_payables"), den_val, period_days=period_days
            )

        elif rid == "efficiency.cash_conversion_cycle":
            dso_val, _, _ = calculate_dso(inputs.get("average_receivables"), inputs.get("revenue"), period_days=period_days)
            dio_val, _, _ = calculate_dio(inputs.get("average_inventory"), inputs.get("cost_of_revenue"), period_days=period_days)
            dpo_val, _, _ = calculate_dpo(inputs.get("average_payables"), inputs.get("cost_of_revenue"), period_days=period_days)
            val, explanation, status = calculate_cash_conversion_cycle(dso_val, dio_val, dpo_val)

        # ---------------------------------------------------------------------
        # 5. Cash Flow Metrics
        # ---------------------------------------------------------------------
        elif rid == "cashflow.free_cash_flow":
            num_val = inputs.get("operating_cash_flow")
            val, explanation, status = calculate_free_cash_flow(
                num_val, inputs.get("capital_expenditures")
            )

        elif rid == "cashflow.free_cash_flow_margin":
            fcf_val, _, _ = calculate_free_cash_flow(
                inputs.get("operating_cash_flow"), inputs.get("capital_expenditures")
            )
            num_val = fcf_val
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_free_cash_flow_margin(num_val, den_val)

        elif rid == "cashflow.operating_cash_flow_margin":
            num_val = inputs.get("operating_cash_flow")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_operating_cash_flow_margin(num_val, den_val)

        elif rid == "cashflow.cash_conversion":
            num_val = inputs.get("operating_cash_flow")
            den_val = inputs.get("net_income")
            val, explanation, status = calculate_cash_conversion(num_val, den_val)

        elif rid == "cashflow.capex_to_revenue":
            num_val = inputs.get("capital_expenditures")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_capex_to_revenue(num_val, den_val)

        elif rid == "cashflow.free_cash_flow_yield":
            fcf_val, _, _ = calculate_free_cash_flow(
                inputs.get("operating_cash_flow"), inputs.get("capital_expenditures")
            )
            num_val = fcf_val
            den_val = inputs.get("market_cap")
            val, explanation, status = calculate_free_cash_flow_yield(num_val, den_val)

        # ---------------------------------------------------------------------
        # 6. Valuation Ratios
        # ---------------------------------------------------------------------
        elif rid == "valuation.pe":
            num_val = inputs.get("market_cap")
            den_val = inputs.get("net_income")
            val, explanation, status = calculate_pe(num_val, den_val)

        elif rid == "valuation.forward_pe":
            num_val = inputs.get("market_price")
            # Forward EPS: only when explicitly authorized/registered
            den_val = inputs.get("forward_eps")
            if den_val is None:
                val, explanation, status = None, "Authorized consensus forward EPS estimate unavailable", RatioStatus.UNAVAILABLE
            else:
                val, explanation, status = calculate_forward_pe(num_val, den_val)

        elif rid == "valuation.pb":
            num_val = inputs.get("market_cap")
            den_val = inputs.get("total_equity")
            val, explanation, status = calculate_pb(num_val, den_val)

        elif rid == "valuation.ps":
            num_val = inputs.get("market_cap")
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_ps(num_val, den_val)

        elif rid == "valuation.price_to_cash_flow":
            num_val = inputs.get("market_cap")
            den_val = inputs.get("operating_cash_flow")
            val, explanation, status = calculate_price_to_cash_flow(num_val, den_val)

        elif rid == "valuation.price_to_free_cash_flow":
            fcf_val, _, _ = calculate_free_cash_flow(
                inputs.get("operating_cash_flow"), inputs.get("capital_expenditures")
            )
            num_val = inputs.get("market_cap")
            den_val = fcf_val
            val, explanation, status = calculate_price_to_free_cash_flow(num_val, den_val)

        elif rid == "valuation.enterprise_value":
            val, explanation, status = calculate_enterprise_value(
                inputs.get("market_cap"),
                inputs.get("total_debt"),
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
            )

        elif rid == "valuation.ev_to_ebitda":
            ev_val, _, _ = calculate_enterprise_value(
                inputs.get("market_cap"),
                inputs.get("total_debt"),
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
            )
            num_val = ev_val
            den_val = inputs.get("ebitda")
            val, explanation, status = calculate_ev_to_ebitda(num_val, den_val)

        elif rid == "valuation.ev_to_revenue":
            ev_val, _, _ = calculate_enterprise_value(
                inputs.get("market_cap"),
                inputs.get("total_debt"),
                inputs.get("cash_and_cash_equivalents"),
                inputs.get("short_term_investments"),
            )
            num_val = ev_val
            den_val = inputs.get("revenue")
            val, explanation, status = calculate_ev_to_revenue(num_val, den_val)

        elif rid == "valuation.dividend_yield":
            num_val = inputs.get("dividends_paid")
            den_val = inputs.get("market_cap")
            val, explanation, status = calculate_dividend_yield(num_val, den_val)

        elif rid == "valuation.earnings_yield":
            num_val = inputs.get("net_income")
            den_val = inputs.get("market_cap")
            val, explanation, status = calculate_earnings_yield(num_val, den_val)

        # ---------------------------------------------------------------------
        # Output Formatting
        # ---------------------------------------------------------------------
        formatted_val = "—"
        if status == RatioStatus.AVAILABLE and val is not None:
            if defn.unit_kind == UnitKind.PERCENT:
                formatted_val = f"{val:.2f}%"
            elif defn.unit_kind == UnitKind.MULTIPLE:
                formatted_val = f"{val:.2f}x"
            elif defn.unit_kind == UnitKind.DAYS:
                formatted_val = f"{val:.1f} days"
            elif defn.unit_kind == UnitKind.MONETARY:
                # Monetary scale formatting (Millions/Billions)
                abs_v = abs(val)
                if abs_v >= Decimal("1000000000"):
                    formatted_val = f"${val / Decimal('1000000000'):,.2f}B"
                elif abs_v >= Decimal("1000000"):
                    formatted_val = f"${val / Decimal('1000000'):,.2f}M"
                else:
                    formatted_val = f"${val:,.2f}"
            else:
                formatted_val = f"{val:.2f}"
        elif status == RatioStatus.NOT_MEANINGFUL:
            formatted_val = "N/M"

        # Relevant lineage items for this ratio's required inputs
        ratio_lineage = [item for item in lineage if item.fact_key in defn.required_inputs or item.fact_key.startswith("average_")]

        return RatioValueDTO(
            ratio_id=defn.id,
            name=defn.name,
            category=defn.category,
            status=status,
            exact_value=val,
            formatted_value=formatted_val,
            unit_kind=defn.unit_kind,
            formula_display=defn.formula_display,
            period_id=period_id,
            period_type=period_type,
            numerator_value=num_val,
            denominator_value=den_val,
            explanation=explanation,
            methodology_version=defn.methodology_version,
            input_lineage=ratio_lineage,
        )

    def get_company_ratios(
        self,
        company_id: UUID,
        company_name: str = "Apple Inc.",
        period_id: str = "FY2024",
        period_type: RatioPeriodType = RatioPeriodType.ANNUAL,
        category: Optional[RatioCategory] = None,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
    ) -> CompanyRatiosResponse:
        """Calculates qualified financial ratios for a company and reporting period."""
        # 1. Resolve statement facts and market inputs
        inputs, lineage = self.input_resolver.resolve_period_inputs(
            company_id=company_id,
            period_id=period_id,
            period_type=period_type,
            consolidation_scope=consolidation_scope,
        )

        # 2. Get registered ratio definitions
        definitions = self.registry.list_ratios(category)

        # 3. Calculate each ratio
        results: List[RatioValueDTO] = []
        category_counts: Dict[str, int] = {}
        avail_count = 0

        for defn in definitions:
            dto = self.calculate_single_ratio(defn, inputs, lineage, period_id, period_type)
            results.append(dto)
            cat_name = defn.category.value
            category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
            if dto.status == RatioStatus.AVAILABLE:
                avail_count += 1

        # Extract fiscal year from period_id
        fy = 2024
        if period_id.startswith("FY") and len(period_id) == 6:
            try:
                fy = int(period_id[2:])
            except ValueError:
                pass
        elif "-" in period_id:
            try:
                fy = int(period_id.split("-")[1])
            except ValueError:
                pass

        return CompanyRatiosResponse(
            company_id=company_id,
            company_name=company_name,
            period_id=period_id,
            period_type=period_type,
            fiscal_year=fy,
            reporting_currency="USD",
            ratios=results,
            category_counts=category_counts,
            available_count=avail_count,
            total_count=len(results),
        )

    def get_company_ratio_history(
        self,
        company_id: UUID,
        ratio_id: str,
        company_name: str = "Apple Inc.",
        period_type: RatioPeriodType = RatioPeriodType.ANNUAL,
        limit: int = 10,
    ) -> RatioHistoryResponse:
        """Generates historical time series for a single financial ratio."""
        defn = self.registry.get_ratio(ratio_id)

        # Discover available periods for company
        catalog = self.statements_repo.get_statement_catalog(company_id)
        candidate_periods = [p for p in catalog.available_periods if (
            p.period_type == StatementPeriodType.ANNUAL if period_type == RatioPeriodType.ANNUAL else p.period_type == StatementPeriodType.QUARTERLY
        )]

        # Sort chronologically by fiscal_year and fiscal_quarter
        candidate_periods = sorted(
            candidate_periods,
            key=lambda p: (p.fiscal_year, p.fiscal_quarter or ""),
        )[-limit:]

        points: List[RatioHistoryPointDTO] = []
        for p in candidate_periods:
            inputs, lineage = self.input_resolver.resolve_period_inputs(
                company_id=company_id,
                period_id=p.period_id,
                period_type=period_type,
            )
            dto = self.calculate_single_ratio(defn, inputs, lineage, p.period_id, period_type)
            points.append(
                RatioHistoryPointDTO(
                    period_id=p.period_id,
                    fiscal_year=p.fiscal_year,
                    period_type=period_type,
                    period_end=p.period_end,
                    status=dto.status,
                    exact_value=dto.exact_value,
                    formatted_value=dto.formatted_value,
                )
            )

        return RatioHistoryResponse(
            company_id=company_id,
            company_name=company_name,
            ratio_id=defn.id,
            ratio_name=defn.name,
            category=defn.category,
            unit_kind=defn.unit_kind,
            series=points,
        )

    def get_ratio_lineage(
        self,
        company_id: UUID,
        ratio_id: str,
        period_id: str = "FY2024",
    ) -> RatioLineageResponse:
        """Returns the calculation lineage and underlying financial statement fact references."""
        defn = self.registry.get_ratio(ratio_id)
        inputs, lineage = self.input_resolver.resolve_period_inputs(
            company_id=company_id,
            period_id=period_id,
            period_type=RatioPeriodType.ANNUAL,
        )
        dto = self.calculate_single_ratio(defn, inputs, lineage, period_id, RatioPeriodType.ANNUAL)

        doc_refs = [
            {
                "statement_type": "10-K / Annual Report",
                "period_id": period_id,
                "provenance_provider": "SEC EDGAR / Canonical Fundamentals",
                "filing_status": "FILED",
            }
        ]

        return RatioLineageResponse(
            company_id=company_id,
            ratio_id=ratio_id,
            period_id=period_id,
            ratio_value=dto,
            source_documents=doc_refs,
        )
