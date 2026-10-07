from typing import Optional

from atlas.fundamentals.concepts import FundamentalConceptDefinition
from atlas.fundamentals.enums import (
    FinancialPeriodNature,
    FinancialStatementType,
    FinancialUnitKind,
)


class FundamentalConceptRegistry:
    """
    Registry of canonical Fundamental Concept Definitions.
    """

    def __init__(self) -> None:
        self._concepts: dict[str, FundamentalConceptDefinition] = {}
        self._frozen = False

    def register(self, concept: FundamentalConceptDefinition) -> None:
        if self._frozen:
            raise RuntimeError("Concept registry is frozen and cannot be modified.")
        if concept.key in self._concepts:
            raise ValueError(f"Concept key '{concept.key}' is already registered.")
        self._concepts[concept.key] = concept

    def get(self, key: str) -> Optional[FundamentalConceptDefinition]:
        return self._concepts.get(key)

    def freeze(self) -> None:
        self._frozen = True

    def list_concepts(self) -> list[FundamentalConceptDefinition]:
        return [self._concepts[key] for key in sorted(self._concepts.keys())]

    @property
    def is_frozen(self) -> bool:
        return self._frozen

# Global instance for the application
registry = FundamentalConceptRegistry()

# Bootstrapping core concepts
registry.register(
    FundamentalConceptDefinition(
        key="revenue",
        display_name="Revenue",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        description="Total revenue.",
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="cost_of_revenue",
        display_name="Cost of Revenue",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        description="Cost of revenue.",
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="gross_profit",
        display_name="Gross Profit",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        description="Gross profit.",
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="research_and_development",
        display_name="Research and Development",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="selling_general_and_administrative",
        display_name="Selling, General and Administrative",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="operating_expenses",
        display_name="Operating Expenses",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="operating_income",
        display_name="Operating Income",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="interest_income",
        display_name="Interest Income",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="interest_expense",
        display_name="Interest Expense",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="other_non_operating_income_expense",
        display_name="Other Non-Operating Income / Expense",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="income_before_tax",
        display_name="Income Before Tax",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="income_tax_expense",
        display_name="Income Tax Expense",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="net_income",
        display_name="Net Income",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT, FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="net_income_attributable_to_common",
        display_name="Net Income Attributable to Common",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="basic_eps",
        display_name="Basic EPS",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY_PER_SHARE]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="diluted_eps",
        display_name="Diluted EPS",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY_PER_SHARE]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="weighted_average_shares_basic",
        display_name="Weighted Average Shares (Basic)",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.SHARES]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="weighted_average_shares_diluted",
        display_name="Weighted Average Shares (Diluted)",
        statement_types=frozenset([FinancialStatementType.INCOME_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.SHARES]),
        normal_sign="positive",
    )
)

# Balance Sheet
registry.register(
    FundamentalConceptDefinition(
        key="cash_and_cash_equivalents",
        display_name="Cash and Cash Equivalents",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="short_term_investments",
        display_name="Short Term Investments",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="accounts_receivable",
        display_name="Accounts Receivable",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="inventory",
        display_name="Inventory",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="current_assets",
        display_name="Current Assets",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="property_plant_equipment_net",
        display_name="Property, Plant, Equipment (Net)",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="goodwill",
        display_name="Goodwill",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="intangible_assets_net",
        display_name="Intangible Assets (Net)",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="total_assets",
        display_name="Total Assets",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="accounts_payable",
        display_name="Accounts Payable",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="current_liabilities",
        display_name="Current Liabilities",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="short_term_debt",
        display_name="Short Term Debt",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="long_term_debt",
        display_name="Long Term Debt",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="total_debt",
        display_name="Total Debt",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="total_liabilities",
        display_name="Total Liabilities",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="common_stock",
        display_name="Common Stock",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="additional_paid_in_capital",
        display_name="Additional Paid-in Capital",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="retained_earnings",
        display_name="Retained Earnings",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="treasury_stock",
        display_name="Treasury Stock",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="total_equity",
        display_name="Total Equity",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="total_liabilities_and_equity",
        display_name="Total Liabilities and Equity",
        statement_types=frozenset([FinancialStatementType.BALANCE_SHEET]),
        period_nature=FinancialPeriodNature.INSTANT,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)

# Cash Flow
registry.register(
    FundamentalConceptDefinition(
        key="net_income_cash_flow",
        display_name="Net Income",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="depreciation_and_amortization",
        display_name="Depreciation & Amortization",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="stock_based_compensation",
        display_name="Stock Based Compensation",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="changes_in_working_capital",
        display_name="Changes in Working Capital",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="operating_cash_flow",
        display_name="Operating Cash Flow",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="capital_expenditures",
        display_name="Capital Expenditures",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="acquisitions",
        display_name="Acquisitions",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="investment_purchases",
        display_name="Investment Purchases",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="investment_sales_maturities",
        display_name="Investment Sales/Maturities",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="investing_cash_flow",
        display_name="Investing Cash Flow",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="debt_issuance",
        display_name="Debt Issuance",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="debt_repayment",
        display_name="Debt Repayment",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="dividends_paid",
        display_name="Dividends Paid",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="share_repurchases",
        display_name="Share Repurchases",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="negative",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="financing_cash_flow",
        display_name="Financing Cash Flow",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="effect_of_fx_on_cash",
        display_name="Effect of FX on Cash",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="net_change_in_cash",
        display_name="Net Change in Cash",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="signed",
    )
)
registry.register(
    FundamentalConceptDefinition(
        key="ending_cash_balance",
        display_name="Ending Cash Balance",
        statement_types=frozenset([FinancialStatementType.CASH_FLOW_STATEMENT]),
        period_nature=FinancialPeriodNature.DURATION,
        unit_kinds=frozenset([FinancialUnitKind.CURRENCY]),
        normal_sign="positive",
    )
)

registry.freeze()
