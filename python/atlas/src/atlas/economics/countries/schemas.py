"""Pydantic V2 Schemas and DTOs for Country Economics Intelligence (Stage 90)."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from atlas.economics.v1.enums import (
    GeographicScopeKind,
    IndicatorCategory,
    PriceBasisKind,
    SeasonalAdjustmentKind,
    StatisticalUnit,
)

from .enums import (
    FiscalAccountingBasis,
    GDPApproachKind,
    GovernmentAccountingScope,
)


class CountryEconomicProfileDTO(BaseModel):
    """Institutional metadata and statistical governance."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    name: str
    iso_code: str
    scope_kind: GeographicScopeKind
    currency_code: str
    central_bank_name: str
    statistical_agency: str
    fiscal_year_structure: str
    national_accounts_standard: str
    available_categories: List[IndicatorCategory]
    supported_series_count: int
    earliest_observation_period: str
    latest_observation_period: str
    notes: Optional[str] = None


class GDPComponentItemDTO(BaseModel):
    """An individual expenditure or production component of GDP."""
    model_config = ConfigDict(from_attributes=True)

    component_id: str
    name: str
    code: str
    value: float
    unit: StatisticalUnit
    share_of_gdp_pct: Optional[float] = None
    growth_yoy: Optional[float] = None
    is_additive: bool = True
    source_series_id: Optional[str] = None
    notes: Optional[str] = None


class CountryGDPDecompositionDTO(BaseModel):
    """GDP analysis including nominal/real levels, per-capita, and components."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    price_basis: PriceBasisKind
    currency: str
    nominal_gdp_billions: Optional[float] = None
    real_gdp_billions: Optional[float] = None
    gdp_deflator_index: Optional[float] = None
    real_growth_qoq_ann: Optional[float] = None
    real_growth_yoy: Optional[float] = None
    gdp_per_capita_usd: Optional[float] = None
    per_capita_population_period: Optional[str] = None
    approach: GDPApproachKind
    components: List[GDPComponentItemDTO] = []
    total_calculated: Optional[float] = None
    is_strictly_additive: bool = True
    non_additive_reason: Optional[str] = None
    statistical_discrepancy: Optional[float] = None


class CountrySectorValueAddedItemDTO(BaseModel):
    """Production approach Gross Value Added by sector."""
    model_config = ConfigDict(from_attributes=True)

    sector_name: str
    sector_code: str
    value_added_billions: float
    unit: StatisticalUnit
    share_of_gva_pct: float
    growth_yoy: Optional[float] = None


class CountryProductionDecompositionDTO(BaseModel):
    """Production-side sector breakdown of GVA."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    total_gva_billions: float
    currency: str
    sectors: List[CountrySectorValueAddedItemDTO] = []
    taxes_less_subsidies_on_products: Optional[float] = None
    gdp_at_market_prices: Optional[float] = None


class CountryInflationSummaryDTO(BaseModel):
    """National price and inflation conditions."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    cpi_index_level: Optional[float] = None
    cpi_index_base: Optional[str] = None
    headline_yoy: Optional[float] = None
    headline_mom: Optional[float] = None
    core_yoy: Optional[float] = None
    core_mom: Optional[float] = None
    food_inflation_yoy: Optional[float] = None
    energy_inflation_yoy: Optional[float] = None
    ppi_yoy: Optional[float] = None
    gdp_deflator_yoy: Optional[float] = None
    seasonal_adjustment: SeasonalAdjustmentKind = SeasonalAdjustmentKind.NOT_ADJUSTED
    notes: Optional[str] = None


class CountryLaborSummaryDTO(BaseModel):
    """Labor market conditions, employment, and wages."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    unemployment_rate: Optional[float] = None
    employment_level_thousands: Optional[float] = None
    labor_force_participation_rate: Optional[float] = None
    employment_to_population_ratio: Optional[float] = None
    youth_unemployment_rate: Optional[float] = None
    nominal_wage_growth_yoy: Optional[float] = None
    real_wage_growth_yoy: Optional[float] = None
    survey_methodology: str
    age_scope: str
    seasonal_adjustment: SeasonalAdjustmentKind = SeasonalAdjustmentKind.SEASONALLY_ADJUSTED


class CountryIndustrySummaryDTO(BaseModel):
    """Real output, retail sales, and sentiment."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    industrial_production_index: Optional[float] = None
    industrial_production_yoy: Optional[float] = None
    manufacturing_output_yoy: Optional[float] = None
    retail_sales_nominal_yoy: Optional[float] = None
    retail_sales_real_yoy: Optional[float] = None
    capacity_utilization_pct: Optional[float] = None
    housing_starts_annualized_thousands: Optional[float] = None
    building_permits_annualized_thousands: Optional[float] = None
    consumer_confidence_index: Optional[float] = None
    business_confidence_index: Optional[float] = None


class CountryMonetarySummaryDTO(BaseModel):
    """Domestic monetary conditions, policy target rate, and credit."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    policy_rate: Optional[float] = None
    policy_rate_target_range: Optional[str] = None
    m1_growth_yoy: Optional[float] = None
    m2_growth_yoy: Optional[float] = None
    domestic_credit_to_private_sector_pct_gdp: Optional[float] = None
    bank_lending_growth_yoy: Optional[float] = None
    monetary_area_name: str
    central_bank_name: str


class CountryFiscalSummaryDTO(BaseModel):
    """Sovereign public finances, expenditures, and debt."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    fiscal_year_label: str
    accounting_scope: GovernmentAccountingScope
    accounting_basis: FiscalAccountingBasis
    total_revenue_billions: Optional[float] = None
    tax_revenue_billions: Optional[float] = None
    total_expenditure_billions: Optional[float] = None
    fiscal_balance_billions: Optional[float] = None
    fiscal_balance_pct_gdp: Optional[float] = None
    primary_balance_billions: Optional[float] = None
    primary_balance_pct_gdp: Optional[float] = None
    gross_government_debt_billions: Optional[float] = None
    gross_debt_pct_gdp: Optional[float] = None
    net_debt_pct_gdp: Optional[float] = None
    interest_expenditure_billions: Optional[float] = None
    currency: str = "USD"


class CountryExternalSummaryDTO(BaseModel):
    """Balance of payments, trade accounts, and FX reserves."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    goods_exports_billions: Optional[float] = None
    goods_imports_billions: Optional[float] = None
    merchandise_trade_balance_billions: Optional[float] = None
    services_exports_billions: Optional[float] = None
    services_imports_billions: Optional[float] = None
    services_trade_balance_billions: Optional[float] = None
    total_trade_balance_billions: Optional[float] = None
    current_account_balance_billions: Optional[float] = None
    current_account_pct_gdp: Optional[float] = None
    fdi_net_inflow_billions: Optional[float] = None
    portfolio_investment_net_billions: Optional[float] = None
    gross_external_debt_billions: Optional[float] = None
    foreign_exchange_reserves_billions: Optional[float] = None
    fx_reserves_currency: str = "USD"
    gold_reserves_fine_troy_oz_millions: Optional[float] = None


class CountryDemographicsSummaryDTO(BaseModel):
    """Demographic structure, population, and urbanization."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    reference_period: str
    total_population_millions: float
    population_growth_rate_pct: Optional[float] = None
    working_age_population_pct: Optional[float] = None
    youth_population_pct: Optional[float] = None
    elderly_population_pct: Optional[float] = None
    urbanization_rate_pct: Optional[float] = None
    age_dependency_ratio_pct: Optional[float] = None
    census_source: str = "National Statistical Office / Census Bureau"


class CountryEconomicsOverviewDTO(BaseModel):
    """Master country macroeconomic overview response."""
    model_config = ConfigDict(from_attributes=True)

    profile: CountryEconomicProfileDTO
    headline_real_gdp_growth_qoq: Optional[float] = None
    headline_real_gdp_growth_yoy: Optional[float] = None
    headline_gdp_period: Optional[str] = None
    nominal_gdp_usd_billions: Optional[float] = None
    gdp_per_capita_usd: Optional[float] = None
    headline_cpi_inflation_yoy: Optional[float] = None
    headline_cpi_period: Optional[str] = None
    core_cpi_inflation_yoy: Optional[float] = None
    unemployment_rate: Optional[float] = None
    unemployment_period: Optional[str] = None
    policy_interest_rate: Optional[float] = None
    policy_rate_period: Optional[str] = None
    general_gov_debt_pct_gdp: Optional[float] = None
    fiscal_balance_pct_gdp: Optional[float] = None
    current_account_pct_gdp: Optional[float] = None
    total_population_millions: Optional[float] = None
    fx_reserves_billions: Optional[float] = None
    data_freshness_status: str = "VERIFIED_CURRENT"


class CountryCoverageResponseDTO(BaseModel):
    """Data coverage and availability summary for a country."""
    model_config = ConfigDict(from_attributes=True)

    geography_id: str
    iso_code: str
    country_name: str
    available_categories: List[IndicatorCategory]
    supported_series_count: int
    has_gdp_expenditure: bool
    has_gdp_production: bool
    has_inflation_components: bool
    has_labor_survey: bool
    has_fiscal_accounts: bool
    has_trade_bop: bool
    has_demographics: bool
    primary_agencies: List[str]
