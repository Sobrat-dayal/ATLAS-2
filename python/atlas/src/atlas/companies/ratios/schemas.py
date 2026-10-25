"""Pydantic Schemas & Data Transfer Objects for Financial Ratios (Stage 83)."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from atlas.companies.ratios.enums import (
    DenominatorPolicy,
    NegativePolicy,
    RatioCategory,
    RatioPeriodType,
    RatioStatus,
    UnitKind,
)


class RatioDefinitionDTO(BaseModel):
    id: str
    name: str
    description: str
    category: RatioCategory
    methodology_version: int
    methodology_id: str
    formula_display: str
    numerator_definition: str
    denominator_definition: str
    required_inputs: List[str]
    supported_periods: List[RatioPeriodType]
    unit_kind: UnitKind
    output_format: str
    denominator_policy: DenominatorPolicy
    negative_policy: NegativePolicy
    requires_market_data: bool
    requires_balance_sheet_average: bool
    supported_industries: List[str]

    model_config = ConfigDict(from_attributes=True)


class RatioCatalogResponse(BaseModel):
    ratios: List[RatioDefinitionDTO]
    total_count: int
    categories: List[str]


class RatioInputFactDTO(BaseModel):
    fact_key: str
    concept_name: str
    value: Optional[Decimal]
    formatted_value: Optional[str]
    statement_type: str
    period_id: str
    is_average: bool = False
    source_revision: str = "v1"


class RatioValueDTO(BaseModel):
    ratio_id: str
    name: str
    category: RatioCategory
    status: RatioStatus
    exact_value: Optional[Decimal] = None
    formatted_value: str
    unit_kind: UnitKind
    formula_display: str
    period_id: str
    period_type: RatioPeriodType
    numerator_value: Optional[Decimal] = None
    denominator_value: Optional[Decimal] = None
    explanation: Optional[str] = None
    methodology_version: int = 1
    input_lineage: List[RatioInputFactDTO] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)


class CompanyRatiosResponse(BaseModel):
    company_id: UUID
    company_name: str
    period_id: str
    period_type: RatioPeriodType
    fiscal_year: int
    reporting_currency: str = "USD"
    ratios: List[RatioValueDTO]
    category_counts: Dict[str, int] = Field(default_factory=dict)
    available_count: int
    total_count: int


class RatioHistoryPointDTO(BaseModel):
    period_id: str
    fiscal_year: int
    period_type: RatioPeriodType
    period_end: Optional[date] = None
    status: RatioStatus
    exact_value: Optional[Decimal] = None
    formatted_value: str
    is_restated: bool = False


class RatioHistoryResponse(BaseModel):
    company_id: UUID
    company_name: str
    ratio_id: str
    ratio_name: str
    category: RatioCategory
    unit_kind: UnitKind
    series: List[RatioHistoryPointDTO]


class RatioMethodologyResponse(BaseModel):
    definition: RatioDefinitionDTO
    calculation_notes: str
    supported_periods: List[RatioPeriodType]


class RatioLineageResponse(BaseModel):
    company_id: UUID
    ratio_id: str
    period_id: str
    ratio_value: Optional[RatioValueDTO] = None
    source_documents: List[Dict[str, Any]] = Field(default_factory=list)
