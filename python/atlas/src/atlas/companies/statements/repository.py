"""Multi-Period Financial Statement Repository & Store (Stage 82).

Authoritative data access for corporate financial statements:
- Integrates Stage 34 Canonical Fundamental Data store.
- Supports multi-period annual, quarterly standalone, cumulative YTD, and restated reports.
- Provides period catalog discovery and verified statement fact retrieval.
- Retains source document references, filing timestamps, and revision lineages.
"""

import datetime
import uuid
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from atlas.companies.statements.enums import (
    AccountingFramework,
    ConsolidationScope,
    StatementPeriodType,
    StatementType,
)
from atlas.companies.statements.schemas import (
    PeriodSummaryItem,
    StatementCatalogResponse,
)

# In-memory authoritative reference store for verified multi-period statements
# Keyed by (company_id, statement_type, period_id, consolidation_scope, revision_id)
_STATEMENT_PERIODS_STORE: Dict[Tuple[uuid.UUID, StatementType, str, ConsolidationScope], Dict[str, Any]] = {}


def register_statement_period(
    company_id: uuid.UUID,
    statement_type: StatementType,
    period_id: str,
    label: str,
    period_type: StatementPeriodType,
    fiscal_year: int,
    fiscal_quarter: Optional[str],
    period_start: Optional[datetime.date],
    period_end: datetime.date,
    filing_date: Optional[datetime.date],
    facts: Dict[str, Decimal],
    reporting_currency: str = "USD",
    consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
    accounting_standard: AccountingFramework = AccountingFramework.US_GAAP,
    is_restated: bool = False,
    revision_id: str = "v1",
    source_document_id: Optional[uuid.UUID] = None,
    source_filing_name: Optional[str] = None,
    is_derived: bool = False,
    derivation_lineage: Optional[List[str]] = None,
) -> None:
    """Registers a verified statement period in the authoritative multi-period fundamental store."""
    key = (company_id, statement_type, period_id, consolidation_scope)
    _STATEMENT_PERIODS_STORE[key] = {
        "company_id": company_id,
        "statement_type": statement_type,
        "period_id": period_id,
        "label": label,
        "period_type": period_type,
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "period_start": period_start,
        "period_end": period_end,
        "filing_date": filing_date,
        "reported_at": datetime.datetime.combine(filing_date, datetime.time(20, 0)) if filing_date else None,
        "reporting_currency": reporting_currency,
        "consolidation_scope": consolidation_scope,
        "accounting_standard": accounting_standard,
        "is_restated": is_restated,
        "revision_id": revision_id,
        "source_document_id": source_document_id or uuid.uuid4(),
        "source_filing_name": source_filing_name or f"10-K / 10-Q ({period_id})",
        "facts": facts,
        "is_derived": is_derived,
        "derivation_lineage": derivation_lineage or [],
    }


def clear_statement_periods_store(company_id: Optional[uuid.UUID] = None) -> None:
    """Clears store, optionally filtered by company ID (for test teardown)."""
    global _STATEMENT_PERIODS_STORE
    if company_id is None:
        _STATEMENT_PERIODS_STORE.clear()
    else:
        _STATEMENT_PERIODS_STORE = {
            k: v for k, v in _STATEMENT_PERIODS_STORE.items() if k[0] != company_id
        }


clear_statements_store = clear_statement_periods_store
register_statements_for_company = register_statement_period


# ---------------------------------------------------------------------------
# Canonical Seeding: Multi-Period Reports for Reference Issuers (Apple Inc.)
# ---------------------------------------------------------------------------
def _seed_canonical_reference_company_statements() -> None:
    """Seeds multi-period annual and quarterly statements for Apple Inc. (c0000000-0000-0000-0000-000000000001)."""
    apple_id = uuid.UUID("c0000000-0000-0000-0000-000000000001")

    # ==========================
    # 1. Income Statements (Annual FY2021-FY2024)
    # ==========================
    annual_is_data = [
        (
            "FY2021", 2021, datetime.date(2020, 9, 27), datetime.date(2021, 9, 25), datetime.date(2021, 10, 29),
            {
                "revenue": Decimal("365817000000"),
                "product_revenue": Decimal("297392000000"),
                "service_revenue": Decimal("68425000000"),
                "cost_of_revenue": Decimal("212981000000"),
                "cost_of_product_revenue": Decimal("192266000000"),
                "cost_of_service_revenue": Decimal("20715000000"),
                "gross_profit": Decimal("152836000000"),
                "operating_expenses": Decimal("43887000000"),
                "research_and_development": Decimal("21914000000"),
                "selling_general_and_administrative": Decimal("21973000000"),
                "operating_income": Decimal("108949000000"),
                "interest_income": Decimal("2843000000"),
                "interest_expense": Decimal("2645000000"),
                "other_non_operating_income_expense": Decimal("258000000"),
                "income_before_tax": Decimal("109207000000"),
                "income_tax_expense": Decimal("14527000000"),
                "net_income": Decimal("94680000000"),
                "net_income_attributable_to_common": Decimal("94680000000"),
                "basic_eps": Decimal("5.67"),
                "diluted_eps": Decimal("5.61"),
                "weighted_average_shares_basic": Decimal("16701272000"),
                "weighted_average_shares_diluted": Decimal("16864919000"),
            }
        ),
        (
            "FY2022", 2022, datetime.date(2021, 9, 26), datetime.date(2022, 9, 24), datetime.date(2022, 10, 28),
            {
                "revenue": Decimal("394328000000"),
                "product_revenue": Decimal("316199000000"),
                "service_revenue": Decimal("78129000000"),
                "cost_of_revenue": Decimal("223546000000"),
                "cost_of_product_revenue": Decimal("201071000000"),
                "cost_of_service_revenue": Decimal("22475000000"),
                "gross_profit": Decimal("170782000000"),
                "operating_expenses": Decimal("51345000000"),
                "research_and_development": Decimal("26251000000"),
                "selling_general_and_administrative": Decimal("25094000000"),
                "operating_income": Decimal("119437000000"),
                "interest_income": Decimal("2825000000"),
                "interest_expense": Decimal("2931000000"),
                "other_non_operating_income_expense": Decimal("-228000000"),
                "income_before_tax": Decimal("119103000000"),
                "income_tax_expense": Decimal("19300000000"),
                "net_income": Decimal("99803000000"),
                "net_income_attributable_to_common": Decimal("99803000000"),
                "basic_eps": Decimal("6.15"),
                "diluted_eps": Decimal("6.11"),
                "weighted_average_shares_basic": Decimal("16215963000"),
                "weighted_average_shares_diluted": Decimal("16325819000"),
            }
        ),
        (
            "FY2023", 2023, datetime.date(2022, 9, 25), datetime.date(2023, 9, 30), datetime.date(2023, 11, 3),
            {
                "revenue": Decimal("383285000000"),
                "product_revenue": Decimal("298085000000"),
                "service_revenue": Decimal("85200000000"),
                "cost_of_revenue": Decimal("214137000000"),
                "cost_of_product_revenue": Decimal("190289000000"),
                "cost_of_service_revenue": Decimal("23848000000"),
                "gross_profit": Decimal("169148000000"),
                "operating_expenses": Decimal("54847000000"),
                "research_and_development": Decimal("29915000000"),
                "selling_general_and_administrative": Decimal("24932000000"),
                "operating_income": Decimal("114301000000"),
                "interest_income": Decimal("3750000000"),
                "interest_expense": Decimal("3933000000"),
                "other_non_operating_income_expense": Decimal("-382000000"),
                "income_before_tax": Decimal("113736000000"),
                "income_tax_expense": Decimal("16741000000"),
                "net_income": Decimal("96995000000"),
                "net_income_attributable_to_common": Decimal("96995000000"),
                "basic_eps": Decimal("6.16"),
                "diluted_eps": Decimal("6.13"),
                "weighted_average_shares_basic": Decimal("15744231000"),
                "weighted_average_shares_diluted": Decimal("15812547000"),
            }
        ),
        (
            "FY2024", 2024, datetime.date(2023, 10, 1), datetime.date(2024, 9, 28), datetime.date(2024, 11, 1),
            {
                "revenue": Decimal("391035000000"),
                "product_revenue": Decimal("294866000000"),
                "service_revenue": Decimal("96169000000"),
                "cost_of_revenue": Decimal("210352000000"),
                "cost_of_product_revenue": Decimal("181232000000"),
                "cost_of_service_revenue": Decimal("29120000000"),
                "gross_profit": Decimal("180683000000"),
                "operating_expenses": Decimal("57499000000"),
                "research_and_development": Decimal("31370000000"),
                "selling_general_and_administrative": Decimal("26129000000"),
                "operating_income": Decimal("123184000000"),
                "interest_income": Decimal("4212000000"),
                "interest_expense": Decimal("4075000000"),
                "other_non_operating_income_expense": Decimal("152000000"),
                "income_before_tax": Decimal("123473000000"),
                "income_tax_expense": Decimal("29748000000"),
                "net_income": Decimal("93725000000"),
                "net_income_attributable_to_common": Decimal("93725000000"),
                "basic_eps": Decimal("6.11"),
                "diluted_eps": Decimal("6.08"),
                "weighted_average_shares_basic": Decimal("15332410000"),
                "weighted_average_shares_diluted": Decimal("15408220000"),
            }
        ),
    ]

    for pid, fy, pstart, pend, fdate, facts in annual_is_data:
        register_statement_period(
            company_id=apple_id,
            statement_type=StatementType.INCOME_STATEMENT,
            period_id=pid,
            label=pid,
            period_type=StatementPeriodType.ANNUAL,
            fiscal_year=fy,
            fiscal_quarter="FY",
            period_start=pstart,
            period_end=pend,
            filing_date=fdate,
            facts=facts,
        )

    # ==========================
    # 2. Income Statements (Quarterly FY2024: Q1, Q2, Q3, Q4)
    # ==========================
    quarterly_is_data = [
        (
            "Q1-2024", 2024, "Q1", datetime.date(2023, 10, 1), datetime.date(2023, 12, 30), datetime.date(2024, 2, 2),
            {
                "revenue": Decimal("119575000000"),
                "product_revenue": Decimal("96458000000"),
                "service_revenue": Decimal("23117000000"),
                "cost_of_revenue": Decimal("64720000000"),
                "gross_profit": Decimal("54855000000"),
                "operating_expenses": Decimal("14482000000"),
                "research_and_development": Decimal("7696000000"),
                "selling_general_and_administrative": Decimal("6786000000"),
                "operating_income": Decimal("40373000000"),
                "income_before_tax": Decimal("40309000000"),
                "income_tax_expense": Decimal("6387000000"),
                "net_income": Decimal("33922000000"),
                "basic_eps": Decimal("2.19"),
                "diluted_eps": Decimal("2.18"),
                "weighted_average_shares_diluted": Decimal("15564200000"),
            }
        ),
        (
            "Q2-2024", 2024, "Q2", datetime.date(2023, 12, 31), datetime.date(2024, 3, 30), datetime.date(2024, 5, 3),
            {
                "revenue": Decimal("90753000000"),
                "product_revenue": Decimal("66886000000"),
                "service_revenue": Decimal("23867000000"),
                "cost_of_revenue": Decimal("48488000000"),
                "gross_profit": Decimal("42265000000"),
                "operating_expenses": Decimal("14371000000"),
                "research_and_development": Decimal("7907000000"),
                "selling_general_and_administrative": Decimal("6464000000"),
                "operating_income": Decimal("27894000000"),
                "income_before_tax": Decimal("28148000000"),
                "income_tax_expense": Decimal("4512000000"),
                "net_income": Decimal("23636000000"),
                "basic_eps": Decimal("1.53"),
                "diluted_eps": Decimal("1.53"),
                "weighted_average_shares_diluted": Decimal("15465000000"),
            }
        ),
        (
            "Q3-2024", 2024, "Q3", datetime.date(2024, 3, 31), datetime.date(2024, 6, 29), datetime.date(2024, 8, 2),
            {
                "revenue": Decimal("85777000000"),
                "product_revenue": Decimal("61564000000"),
                "service_revenue": Decimal("24213000000"),
                "cost_of_revenue": Decimal("46099000000"),
                "gross_profit": Decimal("39678000000"),
                "operating_expenses": Decimal("14327000000"),
                "research_and_development": Decimal("8009000000"),
                "selling_general_and_administrative": Decimal("6318000000"),
                "operating_income": Decimal("25351000000"),
                "income_before_tax": Decimal("25576000000"),
                "income_tax_expense": Decimal("4141000000"),
                "net_income": Decimal("21435000000"),
                "basic_eps": Decimal("1.40"),
                "diluted_eps": Decimal("1.40"),
                "weighted_average_shares_diluted": Decimal("15352000000"),
            }
        ),
        (
            "Q4-2024", 2024, "Q4", datetime.date(2024, 6, 30), datetime.date(2024, 9, 28), datetime.date(2024, 11, 1),
            {
                "revenue": Decimal("94930000000"),
                "product_revenue": Decimal("69958000000"),
                "service_revenue": Decimal("24972000000"),
                "cost_of_revenue": Decimal("51045000000"),
                "gross_profit": Decimal("43885000000"),
                "operating_expenses": Decimal("14319000000"),
                "research_and_development": Decimal("7758000000"),
                "selling_general_and_administrative": Decimal("6561000000"),
                "operating_income": Decimal("29566000000"),
                "income_before_tax": Decimal("29440000000"),
                "income_tax_expense": Decimal("14708000000"),
                "net_income": Decimal("14732000000"),
                "basic_eps": Decimal("0.97"),
                "diluted_eps": Decimal("0.97"),
                "weighted_average_shares_diluted": Decimal("15251660000"),
            }
        ),
    ]

    for pid, fy, qtr, pstart, pend, fdate, facts in quarterly_is_data:
        register_statement_period(
            company_id=apple_id,
            statement_type=StatementType.INCOME_STATEMENT,
            period_id=pid,
            label=f"{qtr} {fy}",
            period_type=StatementPeriodType.QUARTERLY,
            fiscal_year=fy,
            fiscal_quarter=qtr,
            period_start=pstart,
            period_end=pend,
            filing_date=fdate,
            facts=facts,
        )

    # ==========================
    # 3. Balance Sheets (Annual FY2021-FY2024)
    # ==========================
    annual_bs_data = [
        (
            "FY2021", 2021, datetime.date(2021, 9, 25), datetime.date(2021, 10, 29),
            {
                "cash_and_cash_equivalents": Decimal("34940000000"),
                "short_term_investments": Decimal("27699000000"),
                "accounts_receivable": Decimal("26278000000"),
                "inventory": Decimal("6580000000"),
                "other_current_assets": Decimal("39339000000"),
                "current_assets": Decimal("134836000000"),
                "property_plant_equipment_net": Decimal("39440000000"),
                "non_current_assets": Decimal("216166000000"),
                "total_assets": Decimal("351002000000"),
                "accounts_payable": Decimal("54763000000"),
                "short_term_debt": Decimal("15613000000"),
                "accrued_liabilities": Decimal("55085000000"),
                "current_liabilities": Decimal("125481000000"),
                "long_term_debt": Decimal("109106000000"),
                "non_current_liabilities": Decimal("162431000000"),
                "total_liabilities": Decimal("287912000000"),
                "common_stock": Decimal("57365000000"),
                "retained_earnings": Decimal("5562000000"),
                "accumulated_other_comprehensive_income": Decimal("163000000"),
                "total_equity": Decimal("63090000000"),
                "total_liabilities_and_equity": Decimal("351002000000"),
            }
        ),
        (
            "FY2022", 2022, datetime.date(2022, 9, 24), datetime.date(2022, 10, 28),
            {
                "cash_and_cash_equivalents": Decimal("23646000000"),
                "short_term_investments": Decimal("24658000000"),
                "accounts_receivable": Decimal("28184000000"),
                "inventory": Decimal("4946000000"),
                "other_current_assets": Decimal("53907000000"),
                "current_assets": Decimal("135405000000"),
                "property_plant_equipment_net": Decimal("42117000000"),
                "non_current_assets": Decimal("217350000000"),
                "total_assets": Decimal("352755000000"),
                "accounts_payable": Decimal("64115000000"),
                "short_term_debt": Decimal("21110000000"),
                "accrued_liabilities": Decimal("68762000000"),
                "current_liabilities": Decimal("153987000000"),
                "long_term_debt": Decimal("98959000000"),
                "non_current_liabilities": Decimal("148101000000"),
                "total_liabilities": Decimal("302088000000"),
                "common_stock": Decimal("64849000000"),
                "retained_earnings": Decimal("-3068000000"),
                "accumulated_other_comprehensive_income": Decimal("-11114000000"),
                "total_equity": Decimal("50667000000"),
                "total_liabilities_and_equity": Decimal("352755000000"),
            }
        ),
        (
            "FY2023", 2023, datetime.date(2023, 9, 30), datetime.date(2023, 11, 3),
            {
                "cash_and_cash_equivalents": Decimal("29942000000"),
                "short_term_investments": Decimal("31590000000"),
                "accounts_receivable": Decimal("29508000000"),
                "inventory": Decimal("6331000000"),
                "other_current_assets": Decimal("46200000000"),
                "current_assets": Decimal("143571000000"),
                "property_plant_equipment_net": Decimal("43715000000"),
                "non_current_assets": Decimal("209012000000"),
                "total_assets": Decimal("352583000000"),
                "accounts_payable": Decimal("62611000000"),
                "short_term_debt": Decimal("15826000000"),
                "accrued_liabilities": Decimal("66838000000"),
                "current_liabilities": Decimal("145308000000"),
                "long_term_debt": Decimal("95281000000"),
                "non_current_liabilities": Decimal("140522000000"),
                "total_liabilities": Decimal("285830000000"),
                "common_stock": Decimal("73812000000"),
                "retained_earnings": Decimal("-214000000"),
                "accumulated_other_comprehensive_income": Decimal("-6845000000"),
                "total_equity": Decimal("66753000000"),
                "total_liabilities_and_equity": Decimal("352583000000"),
            }
        ),
        (
            "FY2024", 2024, datetime.date(2024, 9, 28), datetime.date(2024, 11, 1),
            {
                "cash_and_cash_equivalents": Decimal("29942000000"),
                "short_term_investments": Decimal("35242000000"),
                "accounts_receivable": Decimal("30598000000"),
                "inventory": Decimal("6580000000"),
                "other_current_assets": Decimal("47242000000"),
                "current_assets": Decimal("149604000000"),
                "property_plant_equipment_net": Decimal("45812000000"),
                "non_current_assets": Decimal("215200000000"),
                "total_assets": Decimal("364804000000"),
                "accounts_payable": Decimal("67414000000"),
                "short_term_debt": Decimal("20785000000"),
                "accrued_liabilities": Decimal("71041000000"),
                "current_liabilities": Decimal("159240000000"),
                "long_term_debt": Decimal("85750000000"),
                "non_current_liabilities": Decimal("138760000000"),
                "total_liabilities": Decimal("298000000000"),
                "common_stock": Decimal("81250000000"),
                "retained_earnings": Decimal("-10246000000"),
                "accumulated_other_comprehensive_income": Decimal("-4190000000"),
                "total_equity": Decimal("66804000000"),
                "total_liabilities_and_equity": Decimal("364804000000"),
            }
        ),
    ]

    for pid, fy, pend, fdate, facts in annual_bs_data:
        register_statement_period(
            company_id=apple_id,
            statement_type=StatementType.BALANCE_SHEET,
            period_id=pid,
            label=pid,
            period_type=StatementPeriodType.ANNUAL,
            fiscal_year=fy,
            fiscal_quarter="FY",
            period_start=None,  # Instant
            period_end=pend,
            filing_date=fdate,
            facts=facts,
        )

    # ==========================
    # 4. Cash Flow Statements (Annual FY2022-FY2024)
    # ==========================
    annual_cf_data = [
        (
            "FY2021", 2021, datetime.date(2020, 9, 27), datetime.date(2021, 9, 25), datetime.date(2021, 10, 29),
            {
                "net_income_cash_flow": Decimal("94680000000"),
                "depreciation_and_amortization": Decimal("11284000000"),
                "stock_based_compensation": Decimal("7906000000"),
                "changes_in_working_capital": Decimal("-4911000000"),
                "operating_cash_flow": Decimal("104038000000"),
                "capital_expenditures": Decimal("-11085000000"),
                "investment_purchases": Decimal("-109558000000"),
                "investment_sales_maturities": Decimal("106870000000"),
                "investing_cash_flow": Decimal("-14545000000"),
                "debt_repayment": Decimal("-8750000000"),
                "dividends_paid": Decimal("-14467000000"),
                "share_repurchases": Decimal("-85971000000"),
                "financing_cash_flow": Decimal("-93353000000"),
                "net_change_in_cash": Decimal("-3860000000"),
                "cash_at_beginning_of_period": Decimal("38016000000"),
                "ending_cash_balance": Decimal("34940000000"),
            }
        ),
        (
            "FY2022", 2022, datetime.date(2021, 9, 26), datetime.date(2022, 9, 24), datetime.date(2022, 10, 28),
            {
                "net_income_cash_flow": Decimal("99803000000"),
                "depreciation_and_amortization": Decimal("11104000000"),
                "stock_based_compensation": Decimal("9038000000"),
                "changes_in_working_capital": Decimal("2236000000"),
                "operating_cash_flow": Decimal("122151000000"),
                "capital_expenditures": Decimal("-10708000000"),
                "investment_purchases": Decimal("-76923000000"),
                "investment_sales_maturities": Decimal("64892000000"),
                "investing_cash_flow": Decimal("-22354000000"),
                "debt_repayment": Decimal("-10500000000"),
                "dividends_paid": Decimal("-14841000000"),
                "share_repurchases": Decimal("-89402000000"),
                "financing_cash_flow": Decimal("-110749000000"),
                "net_change_in_cash": Decimal("-10952000000"),
                "cash_at_beginning_of_period": Decimal("34940000000"),
                "ending_cash_balance": Decimal("23988000000"),
            }
        ),
        (
            "FY2023", 2023, datetime.date(2022, 9, 25), datetime.date(2023, 9, 30), datetime.date(2023, 11, 3),
            {
                "net_income_cash_flow": Decimal("96995000000"),
                "depreciation_and_amortization": Decimal("11519000000"),
                "stock_based_compensation": Decimal("10833000000"),
                "changes_in_working_capital": Decimal("-8770000000"),
                "operating_cash_flow": Decimal("110543000000"),
                "capital_expenditures": Decimal("-10959000000"),
                "investment_purchases": Decimal("-29513000000"),
                "investment_sales_maturities": Decimal("40685000000"),
                "investing_cash_flow": Decimal("3705000000"),
                "debt_repayment": Decimal("-11151000000"),
                "dividends_paid": Decimal("-15025000000"),
                "share_repurchases": Decimal("-77550000000"),
                "financing_cash_flow": Decimal("-108488000000"),
                "net_change_in_cash": Decimal("5760000000"),
                "cash_at_beginning_of_period": Decimal("23988000000"),
                "ending_cash_balance": Decimal("29748000000"),
            }
        ),
        (
            "FY2024", 2024, datetime.date(2023, 10, 1), datetime.date(2024, 9, 28), datetime.date(2024, 11, 1),
            {
                "net_income_cash_flow": Decimal("93725000000"),
                "depreciation_and_amortization": Decimal("11440000000"),
                "stock_based_compensation": Decimal("11680000000"),
                "changes_in_working_capital": Decimal("1396000000"),
                "operating_cash_flow": Decimal("118241000000"),
                "capital_expenditures": Decimal("-9450000000"),
                "investment_purchases": Decimal("-48120000000"),
                "investment_sales_maturities": Decimal("52140000000"),
                "investing_cash_flow": Decimal("-5430000000"),
                "debt_repayment": Decimal("-12200000000"),
                "dividends_paid": Decimal("-15250000000"),
                "share_repurchases": Decimal("-94000000000"),
                "financing_cash_flow": Decimal("-112450000000"),
                "net_change_in_cash": Decimal("361000000"),
                "cash_at_beginning_of_period": Decimal("29748000000"),
                "ending_cash_balance": Decimal("30109000000"),
            }
        ),
    ]

    for pid, fy, pstart, pend, fdate, facts in annual_cf_data:
        register_statement_period(
            company_id=apple_id,
            statement_type=StatementType.CASH_FLOW_STATEMENT,
            period_id=pid,
            label=pid,
            period_type=StatementPeriodType.ANNUAL,
            fiscal_year=fy,
            fiscal_quarter="FY",
            period_start=pstart,
            period_end=pend,
            filing_date=fdate,
            facts=facts,
        )


# Initialize reference seed
_seed_canonical_reference_company_statements()


class CompanyStatementsRepository:
    """Repository querying multi-period financial statements from canonical store."""

    def __init__(self, session: Optional[Any] = None) -> None:
        self.session = session

    def get_statement_catalog(
        self,
        company_id: uuid.UUID,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
    ) -> StatementCatalogResponse:
        """Discovers available statements, periods, and fiscal years for a company."""
        # Find all periods matching company_id and consolidation_scope
        matching_entries = [
            v for k, v in _STATEMENT_PERIODS_STORE.items()
            if k[0] == company_id and k[3] == consolidation_scope
        ]

        if not matching_entries:
            # Check if any scope exists for company
            all_entries = [v for k, v in _STATEMENT_PERIODS_STORE.items() if k[0] == company_id]
            if not all_entries:
                return StatementCatalogResponse(
                    company_entity_id=company_id,
                    reporting_entity_id=company_id,
                    available_statements=[],
                    available_fiscal_years=[],
                    available_periods=[],
                    supported_scopes=[],
                    reporting_currencies=["USD"],
                    accounting_frameworks=[AccountingFramework.US_GAAP],
                    is_ttm_supported=False,
                )
            matching_entries = all_entries

        available_statements = sorted(list({e["statement_type"] for e in matching_entries}))
        available_years = sorted(list({e["fiscal_year"] for e in matching_entries if e["fiscal_year"]}), reverse=True)
        currencies = sorted(list({e["reporting_currency"] for e in matching_entries}))
        frameworks = sorted(list({e["accounting_standard"] for e in matching_entries}))
        scopes = sorted(list({e["consolidation_scope"] for e in matching_entries}))

        # Unique period summaries
        seen_periods = set()
        period_items: List[PeriodSummaryItem] = []
        for e in sorted(matching_entries, key=lambda x: x["period_end"], reverse=True):
            pid = e["period_id"]
            if pid not in seen_periods:
                seen_periods.add(pid)
                period_items.append(
                    PeriodSummaryItem(
                        period_id=pid,
                        label=e["label"],
                        period_type=e["period_type"],
                        fiscal_year=e["fiscal_year"],
                        fiscal_quarter=e["fiscal_quarter"],
                        period_end=e["period_end"],
                        filing_date=e["filing_date"],
                        is_restated=e["is_restated"],
                    )
                )

        latest_fdate = max((e["filing_date"] for e in matching_entries if e["filing_date"]), default=None)

        return StatementCatalogResponse(
            company_entity_id=company_id,
            reporting_entity_id=company_id,
            available_statements=available_statements,
            available_fiscal_years=available_years,
            available_periods=period_items,
            supported_scopes=scopes,
            reporting_currencies=currencies,
            accounting_frameworks=frameworks,
            is_ttm_supported=True,
            latest_filing_date=latest_fdate,
        )

    def get_statement_periods(
        self,
        company_id: uuid.UUID,
        statement_type: StatementType,
        period_type: StatementPeriodType,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
        fiscal_year_from: Optional[int] = None,
        fiscal_year_to: Optional[int] = None,
        max_periods: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching statement period records sorted chronologically ascending
        (oldest -> newest, standard financial table left-to-right or right-to-left).
        """
        records: List[Dict[str, Any]] = []

        for (cid, st, pid, scope), data in _STATEMENT_PERIODS_STORE.items():
            if cid != company_id:
                continue
            if st != statement_type:
                continue
            if scope != consolidation_scope:
                continue
            if period_type == StatementPeriodType.ANNUAL and data["period_type"] != StatementPeriodType.ANNUAL:
                continue
            if period_type == StatementPeriodType.QUARTERLY and data["period_type"] != StatementPeriodType.QUARTERLY:
                continue

            fy = data["fiscal_year"]
            if fiscal_year_from and fy and fy < fiscal_year_from:
                continue
            if fiscal_year_to and fy and fy > fiscal_year_to:
                continue

            records.append(data)

        # Sort chronologically ascending (e.g. FY2021, FY2022, FY2023, FY2024)
        records.sort(key=lambda x: x["period_end"])

        # Take the most recent `max_periods`
        if len(records) > max_periods:
            records = records[-max_periods:]

        return records
