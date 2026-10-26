"""Domain Models for Country Economics Intelligence (Stage 90).

Dataclasses representing comprehensive national economic dossiers, GDP decompositions,
sectoral value added, inflation breakdowns, labor survey statistics, fiscal balances,
external sector trade/BOP accounts, and structural demographics.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional

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


@dataclass
class CountryEconomicProfile:
    """Institutional metadata and statistical governance for a sovereign country or economic area."""
    geography_id: str
    name: str
    iso_code: str
    scope_kind: GeographicScopeKind
    currency_code: str
    central_bank_name: str
    statistical_agency: str
    fiscal_year_structure: str             # e.g., "Calendar Year (Jan-Dec)" or "Fiscal Year (Apr-Mar)"
    national_accounts_standard: str        # e.g., "SNA 2008 / NIPA", "ESA 2010"
    available_categories: List[IndicatorCategory]
    supported_series_count: int
    earliest_observation_period: str
    latest_observation_period: str
    notes: Optional[str] = None


@dataclass
class GDPComponentItem:
    """An individual expenditure or production component of Gross Domestic Product."""
    component_id: str
    name: str
    code: str                              # e.g., "PCEC", "GPDI", "GovCons", "EXP", "IMP", "NETEXP"
    value: Decimal
    unit: StatisticalUnit
    share_of_gdp_pct: Optional[Decimal]
    growth_yoy: Optional[Decimal] = None
    is_additive: bool = True
    source_series_id: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class CountryGDPDecomposition:
    """Comprehensive GDP analysis including nominal/real levels, per-capita, and expenditure components."""
    geography_id: str
    reference_period: str                  # e.g., "2024-Q3" or "2023"
    price_basis: PriceBasisKind
    currency: str
    nominal_gdp_billions: Optional[Decimal]
    real_gdp_billions: Optional[Decimal]
    gdp_deflator_index: Optional[Decimal]
    real_growth_qoq_ann: Optional[Decimal]
    real_growth_yoy: Optional[Decimal]
    gdp_per_capita_usd: Optional[Decimal]
    per_capita_population_period: Optional[str]
    approach: GDPApproachKind
    components: List[GDPComponentItem] = field(default_factory=list)
    total_calculated: Optional[Decimal] = None
    is_strictly_additive: bool = True
    non_additive_reason: Optional[str] = None
    statistical_discrepancy: Optional[Decimal] = None


@dataclass
class CountrySectorValueAddedItem:
    """Production approach Gross Value Added (GVA) by economic sector."""
    sector_name: str
    sector_code: str                       # e.g., "AGRICULTURE", "INDUSTRY", "MANUFACTURING", "SERVICES"
    value_added_billions: Decimal
    unit: StatisticalUnit
    share_of_gva_pct: Decimal
    growth_yoy: Optional[Decimal] = None


@dataclass
class CountryProductionDecomposition:
    """Production-side sector breakdown of national accounts Gross Value Added."""
    geography_id: str
    reference_period: str
    total_gva_billions: Decimal
    currency: str
    sectors: List[CountrySectorValueAddedItem] = field(default_factory=list)
    taxes_less_subsidies_on_products: Optional[Decimal] = None
    gdp_at_market_prices: Optional[Decimal] = None


@dataclass
class CountryInflationSummary:
    """Comprehensive national price and inflation environment."""
    geography_id: str
    reference_period: str                  # e.g., "2024-09"
    cpi_index_level: Optional[Decimal]
    cpi_index_base: Optional[str]          # e.g., "2015=100" or "1982-84=100"
    headline_yoy: Optional[Decimal]
    headline_mom: Optional[Decimal]
    core_yoy: Optional[Decimal]
    core_mom: Optional[Decimal]
    food_inflation_yoy: Optional[Decimal]
    energy_inflation_yoy: Optional[Decimal]
    ppi_yoy: Optional[Decimal]
    gdp_deflator_yoy: Optional[Decimal]
    seasonal_adjustment: SeasonalAdjustmentKind = SeasonalAdjustmentKind.NOT_ADJUSTED
    notes: Optional[str] = None


@dataclass
class CountryLaborSummary:
    """Labor market conditions, participation, employment levels, and wages."""
    geography_id: str
    reference_period: str                  # e.g., "2024-09"
    unemployment_rate: Optional[Decimal]
    employment_level_thousands: Optional[Decimal]
    labor_force_participation_rate: Optional[Decimal]
    employment_to_population_ratio: Optional[Decimal]
    youth_unemployment_rate: Optional[Decimal]
    nominal_wage_growth_yoy: Optional[Decimal]
    real_wage_growth_yoy: Optional[Decimal]
    survey_methodology: str                # e.g., "BLS Current Population Survey (Household)"
    age_scope: str                         # e.g., "16 Years and Over"
    seasonal_adjustment: SeasonalAdjustmentKind = SeasonalAdjustmentKind.SEASONALLY_ADJUSTED


@dataclass
class CountryIndustrySummary:
    """Real economy output, industrial production, retail sales, and sentiment."""
    geography_id: str
    reference_period: str                  # e.g., "2024-09"
    industrial_production_index: Optional[Decimal]
    industrial_production_yoy: Optional[Decimal]
    manufacturing_output_yoy: Optional[Decimal]
    retail_sales_nominal_yoy: Optional[Decimal]
    retail_sales_real_yoy: Optional[Decimal]
    capacity_utilization_pct: Optional[Decimal]
    housing_starts_annualized_thousands: Optional[Decimal]
    building_permits_annualized_thousands: Optional[Decimal]
    consumer_confidence_index: Optional[Decimal]
    business_confidence_index: Optional[Decimal]


@dataclass
class CountryMonetarySummary:
    """Domestic monetary conditions, policy target rate, broad money, and bank credit."""
    geography_id: str
    reference_period: str
    policy_rate: Optional[Decimal]
    policy_rate_target_range: Optional[str]
    m1_growth_yoy: Optional[Decimal]
    m2_growth_yoy: Optional[Decimal]
    domestic_credit_to_private_sector_pct_gdp: Optional[Decimal]
    bank_lending_growth_yoy: Optional[Decimal]
    monetary_area_name: str
    central_bank_name: str


@dataclass
class CountryFiscalSummary:
    """Sovereign public finances, government revenues, expenditures, and debt obligations."""
    geography_id: str
    reference_period: str                  # e.g., "FY2024" or "2024-Q2"
    fiscal_year_label: str
    accounting_scope: GovernmentAccountingScope
    accounting_basis: FiscalAccountingBasis
    total_revenue_billions: Optional[Decimal]
    tax_revenue_billions: Optional[Decimal]
    total_expenditure_billions: Optional[Decimal]
    fiscal_balance_billions: Optional[Decimal]
    fiscal_balance_pct_gdp: Optional[Decimal]
    primary_balance_billions: Optional[Decimal]
    primary_balance_pct_gdp: Optional[Decimal]
    gross_government_debt_billions: Optional[Decimal]
    gross_debt_pct_gdp: Optional[Decimal]
    net_debt_pct_gdp: Optional[Decimal]
    interest_expenditure_billions: Optional[Decimal]
    currency: str = "USD"


@dataclass
class CountryExternalSummary:
    """Balance of payments, trade accounts, capital flows, external debt, and FX reserves."""
    geography_id: str
    reference_period: str                  # e.g., "2024-Q2"
    goods_exports_billions: Optional[Decimal]
    goods_imports_billions: Optional[Decimal]
    merchandise_trade_balance_billions: Optional[Decimal]
    services_exports_billions: Optional[Decimal]
    services_imports_billions: Optional[Decimal]
    services_trade_balance_billions: Optional[Decimal]
    total_trade_balance_billions: Optional[Decimal]
    current_account_balance_billions: Optional[Decimal]
    current_account_pct_gdp: Optional[Decimal]
    fdi_net_inflow_billions: Optional[Decimal]
    portfolio_investment_net_billions: Optional[Decimal]
    gross_external_debt_billions: Optional[Decimal]
    foreign_exchange_reserves_billions: Optional[Decimal]
    fx_reserves_currency: str = "USD"
    gold_reserves_fine_troy_oz_millions: Optional[Decimal] = None


@dataclass
class CountryDemographicsSummary:
    """Structural demographic indicators, population totals, and age structures."""
    geography_id: str
    reference_period: str                  # e.g., "2023"
    total_population_millions: Decimal
    population_growth_rate_pct: Optional[Decimal]
    working_age_population_pct: Optional[Decimal]  # 15–64
    youth_population_pct: Optional[Decimal]        # 0–14
    elderly_population_pct: Optional[Decimal]      # 65+
    urbanization_rate_pct: Optional[Decimal]
    age_dependency_ratio_pct: Optional[Decimal]
    census_source: str = "National Statistical Office / Census Bureau"


@dataclass
class CountryEconomicsOverview:
    """Master high-density macroeconomic summary for a selected sovereign country or area."""
    profile: CountryEconomicProfile
    headline_real_gdp_growth_qoq: Optional[Decimal]
    headline_real_gdp_growth_yoy: Optional[Decimal]
    headline_gdp_period: Optional[str]
    nominal_gdp_usd_billions: Optional[Decimal]
    gdp_per_capita_usd: Optional[Decimal]
    headline_cpi_inflation_yoy: Optional[Decimal]
    headline_cpi_period: Optional[str]
    core_cpi_inflation_yoy: Optional[Decimal]
    unemployment_rate: Optional[Decimal]
    unemployment_period: Optional[str]
    policy_interest_rate: Optional[Decimal]
    policy_rate_period: Optional[str]
    general_gov_debt_pct_gdp: Optional[Decimal]
    fiscal_balance_pct_gdp: Optional[Decimal]
    current_account_pct_gdp: Optional[Decimal]
    total_population_millions: Optional[Decimal]
    fx_reserves_billions: Optional[Decimal]
    data_freshness_status: str = "VERIFIED_CURRENT"
