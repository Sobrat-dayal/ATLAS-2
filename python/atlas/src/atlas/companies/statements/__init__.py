"""Atlas Company Financial Statements Package (Stage 82)."""

from atlas.companies.statements.derivations import (
    calculate_common_size,
    calculate_percentage_change,
    calculate_ttm_annual_bridge,
    calculate_ttm_sum,
    calculate_yoy_absolute_change,
    derive_q4_from_annual_and_9m,
    derive_standalone_quarter_value,
    format_financial_value,
)
from atlas.companies.statements.diagnostics import (
    evaluate_balance_sheet_diagnostics,
    evaluate_cash_flow_diagnostics,
    evaluate_statement_diagnostics,
)
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
from atlas.companies.statements.errors import (
    InvalidStatementQueryError,
    PeriodNotAvailableError,
    ReportingScopeNotAvailableError,
    StatementError,
    StatementNotFoundError,
    TTMInsufficientPeriodsError,
)
from atlas.companies.statements.repository import (
    CompanyStatementsRepository,
    clear_statements_store,
    register_statements_for_company,
)
from atlas.companies.statements.schemas import (
    FinancialStatementCellDTO,
    FinancialStatementResponse,
    FinancialStatementRowDTO,
    PeriodSummaryItem,
    StatementCatalogResponse,
    StatementDiagnosticsDTO,
    StatementPeriodDTO,
)
from atlas.companies.statements.service import CompanyStatementsService
from atlas.companies.statements.taxonomy import (
    BALANCE_SHEET_HIERARCHY,
    CASH_FLOW_HIERARCHY,
    INCOME_STATEMENT_HIERARCHY,
    ConceptHierarchyNode,
    get_statement_hierarchy,
)

__all__ = [
    # Enums
    "StatementType",
    "StatementPeriodType",
    "ConsolidationScope",
    "AccountingFramework",
    "ScaleType",
    "ComparisonMode",
    "RevisionPolicy",
    "DerivationKind",
    "DiagnosticStatus",
    # Errors
    "StatementError",
    "StatementNotFoundError",
    "PeriodNotAvailableError",
    "ReportingScopeNotAvailableError",
    "TTMInsufficientPeriodsError",
    "InvalidStatementQueryError",
    # Taxonomy
    "ConceptHierarchyNode",
    "INCOME_STATEMENT_HIERARCHY",
    "BALANCE_SHEET_HIERARCHY",
    "CASH_FLOW_HIERARCHY",
    "get_statement_hierarchy",
    # Schemas
    "StatementPeriodDTO",
    "FinancialStatementCellDTO",
    "FinancialStatementRowDTO",
    "StatementDiagnosticsDTO",
    "FinancialStatementResponse",
    "PeriodSummaryItem",
    "StatementCatalogResponse",
    # Derivations & Calculations
    "format_financial_value",
    "derive_standalone_quarter_value",
    "derive_q4_from_annual_and_9m",
    "calculate_ttm_sum",
    "calculate_ttm_annual_bridge",
    "calculate_yoy_absolute_change",
    "calculate_percentage_change",
    "calculate_common_size",
    # Diagnostics
    "evaluate_balance_sheet_diagnostics",
    "evaluate_cash_flow_diagnostics",
    "evaluate_statement_diagnostics",
    # Repository & Service
    "CompanyStatementsRepository",
    "register_statements_for_company",
    "clear_statements_store",
    "CompanyStatementsService",
]
