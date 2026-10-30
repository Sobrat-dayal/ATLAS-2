"""
Pydantic V2 Schemas for Portfolio Allocation and Exposure Analytics.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.portfolios.exposure.enums import (
    AssetClass,
    ExposureBasis,
    ExposureDataCompleteness,
    ExposureDimension,
    GeographyPolicy,
    LookThroughStatus,
    SectorTaxonomy,
)


class ExposureCategoryResponse(BaseModel):
    category_id: str
    category_label: str
    base_value: Decimal
    weight: Decimal
    percentage: Decimal
    position_count: int
    direct_value: Decimal
    look_through_value: Decimal
    is_residual: bool = False
    is_unclassified: bool = False
    parent_category_id: Optional[str] = None
    subcategories: List[ExposureCategoryResponse] = Field(default_factory=list)


class ExposureDimensionResponse(BaseModel):
    dimension: ExposureDimension
    total_base_value: Decimal
    total_weight: Decimal
    reconciled: bool
    reconciliation_discrepancy: Decimal
    categories: List[ExposureCategoryResponse] = Field(default_factory=list)


class SecurityWeightResponse(BaseModel):
    instrument_id: str
    symbol: str
    name: str
    asset_class: str
    base_value: Decimal
    weight: Decimal
    percentage: Decimal
    direct_weight: Decimal
    look_through_weight: Decimal
    effective_shares: Decimal
    rank: int


class IssuerWeightResponse(BaseModel):
    issuer_id: str
    issuer_name: str
    country_code: str
    base_value: Decimal
    weight: Decimal
    percentage: Decimal
    constituent_instruments: List[str]
    rank: int


class ConcentrationSummaryResponse(BaseModel):
    top1_weight: Decimal
    top3_weight: Decimal
    top5_weight: Decimal
    top10_weight: Decimal
    top20_weight: Decimal
    herfindahl_index: Decimal
    herfindahl_index_normalized: Decimal
    effective_number_of_holdings: Decimal
    total_positions: int
    direct_holdings_count: int
    look_through_holdings_count: int


class FundConstituentResponse(BaseModel):
    parent_fund_id: str
    constituent_instrument_id: str
    constituent_symbol: str
    constituent_name: str
    constituent_asset_class: str
    constituent_sector: str
    constituent_country: str
    constituent_currency: str
    constituent_weight_in_fund: Decimal
    effective_base_value: Decimal
    effective_portfolio_weight: Decimal
    is_residual: bool = False


class FundLookThroughResponse(BaseModel):
    fund_instrument_id: str
    fund_symbol: str
    fund_name: str
    fund_base_value: Decimal
    fund_weight_in_portfolio: Decimal
    as_of_date: date
    status: LookThroughStatus
    coverage_ratio: Decimal
    residual_weight: Decimal
    residual_base_value: Decimal
    constituents: List[FundConstituentResponse] = Field(default_factory=list)


class CrossFundOverlapResponse(BaseModel):
    constituent_symbol: str
    constituent_name: str
    total_effective_weight: Decimal
    total_effective_value: Decimal
    funds_involved: List[str]
    weights_by_fund: Dict[str, Decimal]


class HistoricalAllocationPointResponse(BaseModel):
    as_of_date: date
    dimension: ExposureDimension
    category_id: str
    category_label: str
    weight: Decimal
    base_value: Decimal
    base_currency: str


class AllocationChangeResponse(BaseModel):
    dimension: ExposureDimension
    category_id: str
    category_label: str
    start_date: date
    end_date: date
    start_weight: Decimal
    end_weight: Decimal
    weight_change_pct: Decimal
    weight_change_bps: int
    start_value: Decimal
    end_value: Decimal
    value_change: Decimal


class ExposureDataQualityResponse(BaseModel):
    completeness: ExposureDataCompleteness
    total_positions: int
    classified_positions: int
    unclassified_positions: int
    classification_coverage_ratio: Decimal
    valuation_coverage_ratio: Decimal
    fx_coverage_ratio: Decimal
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    reconciled: bool = True
    reconciliation_discrepancy: Decimal = Decimal("0.000000")


class PortfolioExposureRunResponse(BaseModel):
    run_id: str
    portfolio_id: str
    account_ids: List[str]
    as_of_date: date
    calculated_at: datetime
    base_currency: str
    exposure_basis: ExposureBasis
    geography_policy: GeographyPolicy
    look_through_applied: bool
    total_nav: Decimal
    gross_exposure: Decimal
    cash_value: Decimal
    cash_weight: Decimal
    input_hash: str
    calculation_version: str
    reconciled: bool
    data_quality: ExposureDataQualityResponse
    asset_classes: ExposureDimensionResponse
    sectors: ExposureDimensionResponse
    industries: ExposureDimensionResponse
    countries: ExposureDimensionResponse
    currencies: ExposureDimensionResponse
    concentration: ConcentrationSummaryResponse
    security_weights: List[SecurityWeightResponse] = Field(default_factory=list)
    issuer_weights: List[IssuerWeightResponse] = Field(default_factory=list)
    funds: List[FundLookThroughResponse] = Field(default_factory=list)
    cross_fund_overlap: List[CrossFundOverlapResponse] = Field(default_factory=list)


class CalculateExposureRequest(BaseModel):
    as_of_date: Optional[date] = None
    account_ids: Optional[List[str]] = None
    exposure_basis: ExposureBasis = ExposureBasis.NET_ASSET_VALUE
    geography_policy: GeographyPolicy = GeographyPolicy.ISSUER_DOMICILE
    enable_look_through: bool = True
    max_look_through_depth: int = 3
    force_recalculate: bool = False

