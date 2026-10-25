"""Pydantic Schemas for Financial Statements API (Stage 82)."""

import datetime
import uuid
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

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


class StatementPeriodDTO(BaseModel):
    """Represents a fiscal column in the financial statement."""

    period_id: str = Field(..., description="Unique period key (e.g. FY2024, Q3-2024, TTM-2024-09)")
    label: str = Field(..., description="Display label (e.g. FY2024, Q3 2024)")
    period_type: StatementPeriodType = Field(...)
    fiscal_year: Optional[int] = Field(default=None)
    fiscal_quarter: Optional[str] = Field(default=None, description="Q1, Q2, Q3, Q4, or FY")
    period_start: Optional[datetime.date] = Field(default=None)
    period_end: datetime.date = Field(...)
    filing_date: Optional[datetime.date] = Field(default=None)
    reported_at: Optional[datetime.datetime] = Field(default=None)
    is_restated: bool = Field(default=False)
    revision_id: Optional[str] = Field(default=None)
    source_document_id: Optional[uuid.UUID] = Field(default=None)
    source_filing_name: Optional[str] = Field(default=None)
    is_derived: bool = Field(default=False)
    derivation_lineage: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FinancialStatementCellDTO(BaseModel):
    """Exact decimal and formatted value for a specific row and period."""

    concept_id: str
    original_concept: Optional[str] = None
    original_label: Optional[str] = None
    exact_value: Optional[Decimal] = Field(default=None, description="Lossless decimal value")
    formatted_value: str = Field(default="—", description="Display formatted text, e.g. (123.45) or $383.29B")
    raw_number: Optional[float] = None
    unit: str = Field(default="USD")
    unit_category: str = Field(default="currency")  # currency, shares, currency_per_share, percent
    scale: str = Field(default="millions")
    derivation_kind: DerivationKind = Field(default=DerivationKind.REPORTED)
    is_restated: bool = Field(default=False)
    source_revision: Optional[str] = None
    source_document_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None

    # Comparison fields (populated when comparison mode is active)
    comparison_value: Optional[Decimal] = None
    comparison_formatted: Optional[str] = None
    is_not_meaningful: bool = Field(default=False, description="True for negative/zero base percentage changes (N/M)")

    model_config = ConfigDict(from_attributes=True)


class FinancialStatementRowDTO(BaseModel):
    """Hierarchical row in the financial statement."""

    concept_id: str
    label: str
    hierarchy_level: int = 0
    parent_id: Optional[str] = None
    display_order: int = 0
    is_group: bool = False
    is_total: bool = False
    normal_sign: str = "signed"
    unit_category: str = "currency"
    description: Optional[str] = None
    cells: Dict[str, FinancialStatementCellDTO] = Field(
        default_factory=dict,
        description="Keyed by period_id",
    )

    model_config = ConfigDict(from_attributes=True)


class StatementDiagnosticsDTO(BaseModel):
    """Accounting consistency diagnostics."""

    status: DiagnosticStatus = Field(default=DiagnosticStatus.CONSISTENT)
    balance_difference: Optional[Decimal] = Field(default=None, description="Assets - (Liabilities + Equity)")
    is_balanced: bool = Field(default=True)
    tolerance_applied: Optional[Decimal] = None
    notes: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FinancialStatementResponse(BaseModel):
    """Complete institutional-grade statement workspace payload."""

    company_entity_id: uuid.UUID
    reporting_entity_id: uuid.UUID
    company_name: str
    statement_type: StatementType
    accounting_framework: AccountingFramework
    consolidation_scope: ConsolidationScope
    reporting_currency: str
    scale: ScaleType
    comparison_mode: ComparisonMode
    revision_policy: RevisionPolicy
    periods: List[StatementPeriodDTO]
    rows: List[FinancialStatementRowDTO]
    diagnostics: StatementDiagnosticsDTO
    source_provenance: str = Field(default="canonical")
    as_of: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class PeriodSummaryItem(BaseModel):
    period_id: str
    label: str
    period_type: StatementPeriodType
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[str] = None
    period_end: datetime.date
    filing_date: Optional[datetime.date] = None
    is_restated: bool = False


class StatementCatalogResponse(BaseModel):
    """Catalog of available statements, years, and scopes for a company."""

    company_entity_id: uuid.UUID
    reporting_entity_id: uuid.UUID
    available_statements: List[StatementType]
    available_fiscal_years: List[int]
    available_periods: List[PeriodSummaryItem]
    supported_scopes: List[ConsolidationScope]
    reporting_currencies: List[str]
    accounting_frameworks: List[AccountingFramework]
    is_ttm_supported: bool = True
    latest_filing_date: Optional[datetime.date] = None

    model_config = ConfigDict(from_attributes=True)
