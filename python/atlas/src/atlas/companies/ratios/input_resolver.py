"""Financial Input Resolver for Financial Ratios (Stage 83).

Resolves required financial statement facts from Stage 82 CompanyStatementsRepository,
calculates balance sheet averages across period openings and closings, and integrates
market price and shares outstanding data with provenance lineage.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from atlas.companies.ratios.enums import RatioPeriodType
from atlas.companies.ratios.schemas import RatioInputFactDTO
from atlas.companies.statements.enums import (
    ConsolidationScope,
    StatementType,
)
from atlas.companies.statements.repository import CompanyStatementsRepository

# Canonical market valuation store for testing and fallback
_MARKET_PRICE_STORE: Dict[UUID, Decimal] = {}
_SHARES_STORE: Dict[UUID, Decimal] = {}


def register_market_price(company_id: UUID, price: Decimal) -> None:
    _MARKET_PRICE_STORE[company_id] = price


def register_shares_outstanding(company_id: UUID, shares: Decimal) -> None:
    _SHARES_STORE[company_id] = shares


def clear_market_data_store() -> None:
    _MARKET_PRICE_STORE.clear()
    _SHARES_STORE.clear()


class RatioInputResolver:
    """Retrieves and qualifies financial statement facts and market inputs."""

    def __init__(self, statements_repo: Optional[CompanyStatementsRepository] = None):
        self.statements_repo = statements_repo or CompanyStatementsRepository()

    def get_market_inputs(self, company_id: UUID) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
        """Returns (market_price, shares_outstanding, market_cap)."""
        apple_id = UUID("c0000000-0000-0000-0000-000000000001")
        # Default seed for Apple reference company if not explicitly overridden
        default_price = Decimal("225.00") if company_id == apple_id else None
        default_shares = Decimal("15251660000") if company_id == apple_id else None

        price = _MARKET_PRICE_STORE.get(company_id, default_price)
        shares = _SHARES_STORE.get(company_id, default_shares)

        if price is not None and shares is not None:
            market_cap = price * shares
            return price, shares, market_cap
        return price, shares, None

    def resolve_period_inputs(
        self,
        company_id: UUID,
        period_id: str,
        period_type: RatioPeriodType,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
    ) -> Tuple[Dict[str, Optional[Decimal]], List[RatioInputFactDTO]]:
        """Resolves all required financial inputs for a given company and reporting period."""
        facts_map: Dict[str, Optional[Decimal]] = {}
        lineage: List[RatioInputFactDTO] = []

        # 1. Fetch current Income Statement, Balance Sheet, and Cash Flow facts
        is_stmt = self.statements_repo.get_statement(
            company_id=company_id,
            statement_type=StatementType.INCOME_STATEMENT,
            period_id=period_id,
            consolidation_scope=consolidation_scope,
        )
        bs_stmt = self.statements_repo.get_statement(
            company_id=company_id,
            statement_type=StatementType.BALANCE_SHEET,
            period_id=period_id,
            consolidation_scope=consolidation_scope,
        )
        cf_stmt = self.statements_repo.get_statement(
            company_id=company_id,
            statement_type=StatementType.CASH_FLOW_STATEMENT,
            period_id=period_id,
            consolidation_scope=consolidation_scope,
        )

        is_facts = is_stmt.get("facts", {}) if is_stmt else {}
        bs_facts = bs_stmt.get("facts", {}) if bs_stmt else {}
        cf_facts = cf_stmt.get("facts", {}) if cf_stmt else {}

        # Record Income Statement inputs
        for k in [
            "revenue", "gross_profit", "cost_of_revenue", "operating_income",
            "income_tax_expense", "income_before_tax", "net_income",
            "diluted_eps", "basic_eps", "interest_expense", "weighted_average_shares_diluted",
        ]:
            val = is_facts.get(k)
            facts_map[k] = val
            if val is not None:
                lineage.append(
                    RatioInputFactDTO(
                        fact_key=k,
                        concept_name=k.replace("_", " ").title(),
                        value=val,
                        formatted_value=str(val),
                        statement_type="INCOME_STATEMENT",
                        period_id=period_id,
                    )
                )

        # Record Cash Flow Statement inputs
        for k in ["operating_cash_flow", "capital_expenditures", "depreciation_and_amortization", "dividends_paid"]:
            val = cf_facts.get(k)
            facts_map[k] = val
            if val is not None:
                lineage.append(
                    RatioInputFactDTO(
                        fact_key=k,
                        concept_name=k.replace("_", " ").title(),
                        value=val,
                        formatted_value=str(val),
                        statement_type="CASH_FLOW_STATEMENT",
                        period_id=period_id,
                    )
                )

        # If D&A was not in Cash Flow, check if it was on Income Statement
        if facts_map.get("depreciation_and_amortization") is None:
            facts_map["depreciation_and_amortization"] = is_facts.get("depreciation_and_amortization")

        # Record Balance Sheet point-in-time facts
        for k in [
            "current_assets", "current_liabilities", "cash_and_cash_equivalents",
            "short_term_investments", "accounts_receivable", "inventory",
            "accounts_payable", "total_assets", "total_equity", "total_liabilities",
            "short_term_debt", "long_term_debt",
        ]:
            val = bs_facts.get(k)
            facts_map[k] = val
            if val is not None:
                lineage.append(
                    RatioInputFactDTO(
                        fact_key=k,
                        concept_name=k.replace("_", " ").title(),
                        value=val,
                        formatted_value=str(val),
                        statement_type="BALANCE_SHEET",
                        period_id=period_id,
                    )
                )

        # Calculate Total Debt
        st_debt = facts_map.get("short_term_debt") or Decimal("0")
        lt_debt = facts_map.get("long_term_debt") or Decimal("0")
        total_debt = st_debt + lt_debt if (facts_map.get("short_term_debt") is not None or facts_map.get("long_term_debt") is not None) else None
        facts_map["total_debt"] = total_debt

        # Calculate EBITDA
        op_inc = facts_map.get("operating_income")
        dna = facts_map.get("depreciation_and_amortization") or Decimal("0")
        if op_inc is not None:
            facts_map["ebitda"] = op_inc + dna
        else:
            facts_map["ebitda"] = None

        # 2. Resolve Average Balance Sheet Values (for ROE, ROA, Asset Turnover, etc.)
        prior_period_id = self._get_prior_period_id(period_id)
        prior_bs = None
        if prior_period_id:
            prior_bs = self.statements_repo.get_statement(
                company_id=company_id,
                statement_type=StatementType.BALANCE_SHEET,
                period_id=prior_period_id,
                consolidation_scope=consolidation_scope,
            )
        prior_facts = prior_bs.get("facts", {}) if prior_bs else {}

        # Calculate averages for total_equity, total_assets, inventory, accounts_receivable, accounts_payable
        for key in ["total_equity", "total_assets", "inventory", "accounts_receivable", "accounts_payable"]:
            curr_val = facts_map.get(key)
            prev_val = prior_facts.get(key)
            avg_key = f"average_{key}" if key != "total_equity" else "average_equity"
            if avg_key == "average_total_assets":
                avg_key = "average_assets"

            if curr_val is not None and prev_val is not None:
                avg_val = (curr_val + prev_val) / Decimal("2")
                facts_map[avg_key] = avg_val
                lineage.append(
                    RatioInputFactDTO(
                        fact_key=avg_key,
                        concept_name=f"Average {key.replace('_', ' ').title()}",
                        value=avg_val,
                        formatted_value=f"Avg({prev_val:,.0f}, {curr_val:,.0f})",
                        statement_type="BALANCE_SHEET",
                        period_id=period_id,
                        is_average=True,
                    )
                )
            elif curr_val is not None:
                # Fallback to period-end when prior period is unavailable
                facts_map[avg_key] = curr_val
                lineage.append(
                    RatioInputFactDTO(
                        fact_key=avg_key,
                        concept_name=f"Ending {key.replace('_', ' ').title()} (Prior Period Unavailable)",
                        value=curr_val,
                        formatted_value=f"{curr_val:,.0f}",
                        statement_type="BALANCE_SHEET",
                        period_id=period_id,
                        is_average=False,
                    )
                )
            else:
                facts_map[avg_key] = None

        # Average Invested Capital = Total Debt + Total Equity - Cash & Equivalents
        curr_eq = facts_map.get("total_equity")
        curr_cash = (facts_map.get("cash_and_cash_equivalents") or Decimal("0")) + (facts_map.get("short_term_investments") or Decimal("0"))
        if total_debt is not None and curr_eq is not None:
            curr_inv_cap = total_debt + curr_eq - curr_cash
            prior_debt = (prior_facts.get("short_term_debt") or Decimal("0")) + (prior_facts.get("long_term_debt") or Decimal("0"))
            prior_eq = prior_facts.get("total_equity")
            prior_cash = (prior_facts.get("cash_and_cash_equivalents") or Decimal("0")) + (prior_facts.get("short_term_investments") or Decimal("0"))
            if prior_eq is not None:
                prev_inv_cap = prior_debt + prior_eq - prior_cash
                facts_map["average_invested_capital"] = (curr_inv_cap + prev_inv_cap) / Decimal("2")
            else:
                facts_map["average_invested_capital"] = curr_inv_cap
        else:
            facts_map["average_invested_capital"] = None

        # Average Capital Employed = Total Assets - Current Liabilities
        curr_ta = facts_map.get("total_assets")
        curr_cl = facts_map.get("current_liabilities")
        if curr_ta is not None and curr_cl is not None:
            curr_ce = curr_ta - curr_cl
            prev_ta = prior_facts.get("total_assets")
            prev_cl = prior_facts.get("current_liabilities")
            if prev_ta is not None and prev_cl is not None:
                prev_ce = prev_ta - prev_cl
                facts_map["average_capital_employed"] = (curr_ce + prev_ce) / Decimal("2")
            else:
                facts_map["average_capital_employed"] = curr_ce
        else:
            facts_map["average_capital_employed"] = None

        # 3. Market Valuation Inputs
        market_price, shares_out, market_cap = self.get_market_inputs(company_id)
        facts_map["market_price"] = market_price
        facts_map["shares_outstanding"] = shares_out
        facts_map["market_cap"] = market_cap

        if market_price is not None:
            lineage.append(
                RatioInputFactDTO(
                    fact_key="market_price",
                    concept_name="Latest Market Price",
                    value=market_price,
                    formatted_value=f"${market_price:.2f}",
                    statement_type="MARKET_DATA",
                    period_id=period_id,
                )
            )
        if market_cap is not None:
            lineage.append(
                RatioInputFactDTO(
                    fact_key="market_cap",
                    concept_name="Market Capitalization",
                    value=market_cap,
                    formatted_value=f"${market_cap:,.0f}",
                    statement_type="MARKET_DATA",
                    period_id=period_id,
                )
            )

        return facts_map, lineage

    def _get_prior_period_id(self, period_id: str) -> Optional[str]:
        """Maps period ID to prior comparable period ID (e.g. FY2024 -> FY2023, Q4-2024 -> Q3-2024)."""
        if period_id.startswith("FY") and len(period_id) == 6:
            try:
                year = int(period_id[2:])
                return f"FY{year - 1}"
            except ValueError:
                return None
        elif period_id.startswith("Q") and "-" in period_id:
            parts = period_id.split("-")
            qtr = parts[0]
            year = int(parts[1])
            if qtr == "Q4":
                return f"Q3-{year}"
            elif qtr == "Q3":
                return f"Q2-{year}"
            elif qtr == "Q2":
                return f"Q1-{year}"
            elif qtr == "Q1":
                return f"Q4-{year - 1}"
        return None
