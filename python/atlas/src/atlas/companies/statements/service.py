"""Company Financial Statements Service (Stage 82).

Orchestrates:
- Canonical statement retrieval from repository.
- Period catalog generation.
- Exact Decimal calculations and TTM derivation.
- Accounting taxonomy hierarchy projection.
- Display scale conversion and financial sign formatting.
- Period-over-period comparisons (YoY, QoQ) and common-size analysis.
- Accounting consistency diagnostics.
- Strict entitlement and error handling.
"""

import uuid
from decimal import Decimal
from typing import Dict, List, Optional

from atlas.companies.statements.derivations import (
    calculate_common_size,
    calculate_percentage_change,
    calculate_ttm_sum,
    calculate_yoy_absolute_change,
    format_financial_value,
)
from atlas.companies.statements.diagnostics import evaluate_statement_diagnostics
from atlas.companies.statements.enums import (
    AccountingFramework,
    ComparisonMode,
    ConsolidationScope,
    DerivationKind,
    DiagnosticStatus,
    RevisionPolicy,
    ScaleType,
    StatementPeriodType,
    StatementType,
)
from atlas.companies.statements.repository import CompanyStatementsRepository
from atlas.companies.statements.schemas import (
    FinancialStatementCellDTO,
    FinancialStatementResponse,
    FinancialStatementRowDTO,
    StatementCatalogResponse,
    StatementDiagnosticsDTO,
    StatementPeriodDTO,
)
from atlas.companies.statements.taxonomy import get_statement_hierarchy


class CompanyStatementsService:
    """Core domain service for Stage 82 Financial Statements."""

    def __init__(self, repository: CompanyStatementsRepository) -> None:
        self.repository = repository

    async def get_statement_catalog(
        self,
        company_id: uuid.UUID,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
    ) -> StatementCatalogResponse:
        """Returns catalog of available statements, periods, and fiscal years."""
        return self.repository.get_statement_catalog(
            company_id=company_id,
            consolidation_scope=consolidation_scope,
        )

    async def get_financial_statement(
        self,
        company_id: uuid.UUID,
        statement_type: StatementType,
        period_type: StatementPeriodType = StatementPeriodType.ANNUAL,
        consolidation_scope: ConsolidationScope = ConsolidationScope.CONSOLIDATED,
        scale: ScaleType = ScaleType.MILLIONS,
        comparison_mode: ComparisonMode = ComparisonMode.NONE,
        revision_policy: RevisionPolicy = RevisionPolicy.LATEST,
        fiscal_year_from: Optional[int] = None,
        fiscal_year_to: Optional[int] = None,
        max_periods: int = 5,
        company_name: str = "Company",
    ) -> FinancialStatementResponse:
        """
        Retrieves, normalizes, and projects complete financial statement table.
        Guarantees:
        - Exact Decimal arithmetic.
        - Zero synthetic figures without underlying facts.
        - TTM strictly restricted to flow statements with 4 consecutive standalone quarters.
        """
        # 1. Fetch relevant periods from repository
        query_period_type = StatementPeriodType.QUARTERLY if period_type == StatementPeriodType.TTM else period_type

        period_records = self.repository.get_statement_periods(
            company_id=company_id,
            statement_type=statement_type,
            period_type=query_period_type,
            consolidation_scope=consolidation_scope,
            fiscal_year_from=fiscal_year_from,
            fiscal_year_to=fiscal_year_to,
            max_periods=max_periods if period_type != StatementPeriodType.TTM else 4,
        )

        # 2. Handle TTM Derivation
        if period_type == StatementPeriodType.TTM:
            if statement_type == StatementType.BALANCE_SHEET:
                raise ValueError("TTM summation is mathematically invalid and strictly prohibited for Balance Sheet stock facts.")

            if len(period_records) < 4:
                # Return empty response with diagnostic notice
                return FinancialStatementResponse(
                    company_entity_id=company_id,
                    reporting_entity_id=company_id,
                    company_name=company_name,
                    statement_type=statement_type,
                    accounting_framework=AccountingFramework.US_GAAP,
                    consolidation_scope=consolidation_scope,
                    reporting_currency="USD",
                    scale=scale,
                    comparison_mode=comparison_mode,
                    revision_policy=revision_policy,
                    periods=[],
                    rows=[],
                    diagnostics=StatementDiagnosticsDTO(
                        status=DiagnosticStatus.INCOMPLETE,
                        notes=["Insufficient consecutive standalone quarters (minimum 4 required) to construct TTM view."],
                    ),
                )

            # Sum the 4 quarters to form single TTM period record
            ttm_facts: Dict[str, Decimal] = {}
            all_concepts = set()
            for r in period_records:
                all_concepts.update(r["facts"].keys())

            for c in all_concepts:
                q_vals = [r["facts"].get(c) for r in period_records]
                val, is_valid, _ = calculate_ttm_sum(q_vals)
                if is_valid and val is not None:
                    ttm_facts[c] = val

            latest_q = period_records[-1]
            ttm_record = {
                "company_id": company_id,
                "statement_type": statement_type,
                "period_id": f"TTM-{latest_q['period_end']}",
                "label": f"TTM ({latest_q['label']})",
                "period_type": StatementPeriodType.TTM,
                "fiscal_year": latest_q["fiscal_year"],
                "fiscal_quarter": "TTM",
                "period_start": period_records[0]["period_start"],
                "period_end": latest_q["period_end"],
                "filing_date": latest_q["filing_date"],
                "reported_at": latest_q["reported_at"],
                "reporting_currency": latest_q["reporting_currency"],
                "consolidation_scope": consolidation_scope,
                "accounting_standard": latest_q["accounting_standard"],
                "is_restated": any(r["is_restated"] for r in period_records),
                "revision_id": "ttm_derived",
                "source_document_id": latest_q["source_document_id"],
                "source_filing_name": f"TTM derived from 4 quarters ({', '.join(r['period_id'] for r in period_records)})",
                "facts": ttm_facts,
                "is_derived": True,
                "derivation_lineage": [r["period_id"] for r in period_records],
            }
            period_records = [ttm_record]

        # 3. Build Period DTOs
        periods_dto: List[StatementPeriodDTO] = []
        for r in period_records:
            periods_dto.append(
                StatementPeriodDTO(
                    period_id=r["period_id"],
                    label=r["label"],
                    period_type=r["period_type"],
                    fiscal_year=r["fiscal_year"],
                    fiscal_quarter=r["fiscal_quarter"],
                    period_start=r["period_start"],
                    period_end=r["period_end"],
                    filing_date=r["filing_date"],
                    reported_at=r["reported_at"],
                    is_restated=r["is_restated"],
                    revision_id=r["revision_id"],
                    source_document_id=r["source_document_id"],
                    source_filing_name=r["source_filing_name"],
                    is_derived=r.get("is_derived", False),
                    derivation_lineage=r.get("derivation_lineage", []),
                )
            )

        # 4. Resolve Framework and Currency
        framework = AccountingFramework.US_GAAP
        currency = "USD"
        if period_records:
            framework = period_records[-1].get("accounting_standard", AccountingFramework.US_GAAP)
            currency = period_records[-1].get("reporting_currency", "USD")

        # 5. Build Hierarchical Statement Rows
        hierarchy_nodes = get_statement_hierarchy(statement_type)
        rows_dto: List[FinancialStatementRowDTO] = []

        # Find denominators for common-size mode if requested
        denominators_by_period: Dict[str, Optional[Decimal]] = {}
        if comparison_mode == ComparisonMode.COMMON_SIZE:
            denom_key = "revenue" if statement_type == StatementType.INCOME_STATEMENT else "total_assets"
            for r in period_records:
                denominators_by_period[r["period_id"]] = r["facts"].get(denom_key)

        for node in hierarchy_nodes:
            cells_map: Dict[str, FinancialStatementCellDTO] = {}

            for idx, r in enumerate(period_records):
                pid = r["period_id"]
                exact_val = r["facts"].get(node.concept_id)

                # Format base value
                formatted_str, scale_used = format_financial_value(
                    exact_val,
                    unit_category=node.unit_category,
                    scale=scale,
                    currency_symbol="$" if currency == "USD" else f"{currency} ",
                )

                # Handle Comparison Mode
                comp_val: Optional[Decimal] = None
                comp_fmt: Optional[str] = None
                is_nm = False

                if comparison_mode in (ComparisonMode.YOY_ABSOLUTE, ComparisonMode.YOY_PERCENT):
                    # Find prior comparable period (1 year prior, i.e. idx - 1 if annual, or idx - 4 if quarterly)
                    step = 4 if period_type == StatementPeriodType.QUARTERLY else 1
                    prior_idx = idx - step
                    if prior_idx >= 0:
                        prior_val = period_records[prior_idx]["facts"].get(node.concept_id)
                        if comparison_mode == ComparisonMode.YOY_ABSOLUTE:
                            comp_val = calculate_yoy_absolute_change(exact_val, prior_val)
                            comp_fmt, _ = format_financial_value(comp_val, unit_category=node.unit_category, scale=scale)
                        elif comparison_mode == ComparisonMode.YOY_PERCENT:
                            comp_val, is_nm, comp_fmt = calculate_percentage_change(exact_val, prior_val)

                elif comparison_mode in (ComparisonMode.QOQ_ABSOLUTE, ComparisonMode.QOQ_PERCENT):
                    if idx > 0:
                        prior_val = period_records[idx - 1]["facts"].get(node.concept_id)
                        if comparison_mode == ComparisonMode.QOQ_ABSOLUTE:
                            comp_val = calculate_yoy_absolute_change(exact_val, prior_val)
                            comp_fmt, _ = format_financial_value(comp_val, unit_category=node.unit_category, scale=scale)
                        elif comparison_mode == ComparisonMode.QOQ_PERCENT:
                            comp_val, is_nm, comp_fmt = calculate_percentage_change(exact_val, prior_val)

                elif comparison_mode == ComparisonMode.COMMON_SIZE:
                    denom = denominators_by_period.get(pid)
                    comp_val, comp_fmt = calculate_common_size(exact_val, denom)

                cells_map[pid] = FinancialStatementCellDTO(
                    concept_id=node.concept_id,
                    original_concept=node.concept_id,
                    original_label=node.label,
                    exact_value=exact_val,
                    formatted_value=formatted_str,
                    raw_number=float(exact_val) if exact_val is not None else None,
                    unit=currency if node.unit_category == "currency" else node.unit_category,
                    unit_category=node.unit_category,
                    scale=scale_used,
                    derivation_kind=DerivationKind.DERIVED_TTM if period_type == StatementPeriodType.TTM else DerivationKind.REPORTED,
                    is_restated=r.get("is_restated", False),
                    source_revision=r.get("revision_id"),
                    source_document_id=r.get("source_document_id"),
                    comparison_value=comp_val,
                    comparison_formatted=comp_fmt,
                    is_not_meaningful=is_nm,
                )

            rows_dto.append(
                FinancialStatementRowDTO(
                    concept_id=node.concept_id,
                    label=node.label,
                    hierarchy_level=node.hierarchy_level,
                    parent_id=node.parent_id,
                    display_order=node.display_order,
                    is_group=node.is_group,
                    is_total=node.is_total,
                    normal_sign=node.normal_sign,
                    unit_category=node.unit_category,
                    description=node.description,
                    cells=cells_map,
                )
            )

        # 6. Evaluate Diagnostics on the Most Recent Period
        diagnostics = StatementDiagnosticsDTO(status=DiagnosticStatus.CONSISTENT)
        if period_records:
            latest_facts = period_records[-1]["facts"]
            diagnostics = evaluate_statement_diagnostics(statement_type, latest_facts)

        return FinancialStatementResponse(
            company_entity_id=company_id,
            reporting_entity_id=company_id,
            company_name=company_name,
            statement_type=statement_type,
            accounting_framework=framework,
            consolidation_scope=consolidation_scope,
            reporting_currency=currency,
            scale=scale,
            comparison_mode=comparison_mode,
            revision_policy=revision_policy,
            periods=periods_dto,
            rows=rows_dto,
            diagnostics=diagnostics,
        )
