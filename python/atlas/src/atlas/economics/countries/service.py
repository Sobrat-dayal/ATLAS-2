"""Domain Service for Country Economics Intelligence (Stage 90).

Coordinates macroeconomic category queries, per-capita demographic reconciliations,
expenditure additivity validation, and conversion to Pydantic V2 DTOs.
"""

from typing import List, Optional

from .enums import GDPApproachKind
from .models import (
    CountryDemographicsSummary,
    CountryEconomicProfile,
    CountryEconomicsOverview,
    CountryExternalSummary,
    CountryFiscalSummary,
    CountryGDPDecomposition,
    CountryIndustrySummary,
    CountryInflationSummary,
    CountryLaborSummary,
    CountryMonetarySummary,
    CountryProductionDecomposition,
)
from .repository import CountryEconomicsRepository
from .schemas import (
    CountryCoverageResponseDTO,
    CountryDemographicsSummaryDTO,
    CountryEconomicProfileDTO,
    CountryEconomicsOverviewDTO,
    CountryExternalSummaryDTO,
    CountryFiscalSummaryDTO,
    CountryGDPDecompositionDTO,
    CountryIndustrySummaryDTO,
    CountryInflationSummaryDTO,
    CountryLaborSummaryDTO,
    CountryMonetarySummaryDTO,
    CountryProductionDecompositionDTO,
    CountrySectorValueAddedItemDTO,
    GDPComponentItemDTO,
)


class CountryEconomicsService:
    """Service orchestrating Country Economics business logic and validations."""

    def __init__(self, repo: Optional[CountryEconomicsRepository] = None):
        self.repo = repo or CountryEconomicsRepository()

    def _to_float(self, val) -> Optional[float]:
        return float(val) if val is not None else None

    # -------------------------------------------------------------------------
    # Profile & Country Discovery
    # -------------------------------------------------------------------------

    def get_profile(self, geography_id: str) -> CountryEconomicProfileDTO:
        profile: CountryEconomicProfile = self.repo.get_profile(geography_id)
        return CountryEconomicProfileDTO.model_validate(profile)

    def list_countries(self) -> List[CountryEconomicProfileDTO]:
        profiles = self.repo.list_countries()
        return [CountryEconomicProfileDTO.model_validate(p) for p in profiles]

    # -------------------------------------------------------------------------
    # Master Overview
    # -------------------------------------------------------------------------

    def get_overview(self, geography_id: str) -> CountryEconomicsOverviewDTO:
        overview: CountryEconomicsOverview = self.repo.get_overview(geography_id)
        return CountryEconomicsOverviewDTO(
            profile=CountryEconomicProfileDTO.model_validate(overview.profile),
            headline_real_gdp_growth_qoq=self._to_float(overview.headline_real_gdp_growth_qoq),
            headline_real_gdp_growth_yoy=self._to_float(overview.headline_real_gdp_growth_yoy),
            headline_gdp_period=overview.headline_gdp_period,
            nominal_gdp_usd_billions=self._to_float(overview.nominal_gdp_usd_billions),
            gdp_per_capita_usd=self._to_float(overview.gdp_per_capita_usd),
            headline_cpi_inflation_yoy=self._to_float(overview.headline_cpi_inflation_yoy),
            headline_cpi_period=overview.headline_cpi_period,
            core_cpi_inflation_yoy=self._to_float(overview.core_cpi_inflation_yoy),
            unemployment_rate=self._to_float(overview.unemployment_rate),
            unemployment_period=overview.unemployment_period,
            policy_interest_rate=self._to_float(overview.policy_interest_rate),
            policy_rate_period=overview.policy_rate_period,
            general_gov_debt_pct_gdp=self._to_float(overview.general_gov_debt_pct_gdp),
            fiscal_balance_pct_gdp=self._to_float(overview.fiscal_balance_pct_gdp),
            current_account_pct_gdp=self._to_float(overview.current_account_pct_gdp),
            total_population_millions=self._to_float(overview.total_population_millions),
            fx_reserves_billions=self._to_float(overview.fx_reserves_billions),
            data_freshness_status=overview.data_freshness_status,
        )

    # -------------------------------------------------------------------------
    # National Accounts (GDP Expenditure & Production)
    # -------------------------------------------------------------------------

    def get_gdp(
        self, geography_id: str, approach: GDPApproachKind = GDPApproachKind.EXPENDITURE
    ) -> CountryGDPDecompositionDTO:
        gdp: CountryGDPDecomposition = self.repo.get_gdp_decomposition(geography_id, approach)

        # Map components
        comp_dtos = [
            GDPComponentItemDTO(
                component_id=c.component_id,
                name=c.name,
                code=c.code,
                value=float(c.value),
                unit=c.unit,
                share_of_gdp_pct=self._to_float(c.share_of_gdp_pct),
                growth_yoy=self._to_float(c.growth_yoy),
                is_additive=c.is_additive,
                source_series_id=c.source_series_id,
                notes=c.notes,
            )
            for c in gdp.components
        ]

        return CountryGDPDecompositionDTO(
            geography_id=gdp.geography_id,
            reference_period=gdp.reference_period,
            price_basis=gdp.price_basis,
            currency=gdp.currency,
            nominal_gdp_billions=self._to_float(gdp.nominal_gdp_billions),
            real_gdp_billions=self._to_float(gdp.real_gdp_billions),
            gdp_deflator_index=self._to_float(gdp.gdp_deflator_index),
            real_growth_qoq_ann=self._to_float(gdp.real_growth_qoq_ann),
            real_growth_yoy=self._to_float(gdp.real_growth_yoy),
            gdp_per_capita_usd=self._to_float(gdp.gdp_per_capita_usd),
            per_capita_population_period=gdp.per_capita_population_period,
            approach=gdp.approach,
            components=comp_dtos,
            total_calculated=self._to_float(gdp.total_calculated),
            is_strictly_additive=gdp.is_strictly_additive,
            non_additive_reason=gdp.non_additive_reason,
            statistical_discrepancy=self._to_float(gdp.statistical_discrepancy),
        )

    def get_production(self, geography_id: str) -> CountryProductionDecompositionDTO:
        prod: CountryProductionDecomposition = self.repo.get_production_decomposition(geography_id)
        sector_dtos = [
            CountrySectorValueAddedItemDTO(
                sector_name=s.sector_name,
                sector_code=s.sector_code,
                value_added_billions=float(s.value_added_billions),
                unit=s.unit,
                share_of_gva_pct=float(s.share_of_gva_pct),
                growth_yoy=self._to_float(s.growth_yoy),
            )
            for s in prod.sectors
        ]
        return CountryProductionDecompositionDTO(
            geography_id=prod.geography_id,
            reference_period=prod.reference_period,
            total_gva_billions=float(prod.total_gva_billions),
            currency=prod.currency,
            sectors=sector_dtos,
            taxes_less_subsidies_on_products=self._to_float(prod.taxes_less_subsidies_on_products),
            gdp_at_market_prices=self._to_float(prod.gdp_at_market_prices),
        )

    # -------------------------------------------------------------------------
    # Inflation & Prices
    # -------------------------------------------------------------------------

    def get_inflation(self, geography_id: str) -> CountryInflationSummaryDTO:
        cpi: CountryInflationSummary = self.repo.get_inflation_summary(geography_id)
        return CountryInflationSummaryDTO(
            geography_id=cpi.geography_id,
            reference_period=cpi.reference_period,
            cpi_index_level=self._to_float(cpi.cpi_index_level),
            cpi_index_base=cpi.cpi_index_base,
            headline_yoy=self._to_float(cpi.headline_yoy),
            headline_mom=self._to_float(cpi.headline_mom),
            core_yoy=self._to_float(cpi.core_yoy),
            core_mom=self._to_float(cpi.core_mom),
            food_inflation_yoy=self._to_float(cpi.food_inflation_yoy),
            energy_inflation_yoy=self._to_float(cpi.energy_inflation_yoy),
            ppi_yoy=self._to_float(cpi.ppi_yoy),
            gdp_deflator_yoy=self._to_float(cpi.gdp_deflator_yoy),
            seasonal_adjustment=cpi.seasonal_adjustment,
            notes=cpi.notes,
        )

    # -------------------------------------------------------------------------
    # Labor & Employment
    # -------------------------------------------------------------------------

    def get_labor(self, geography_id: str) -> CountryLaborSummaryDTO:
        labor: CountryLaborSummary = self.repo.get_labor_summary(geography_id)
        return CountryLaborSummaryDTO(
            geography_id=labor.geography_id,
            reference_period=labor.reference_period,
            unemployment_rate=self._to_float(labor.unemployment_rate),
            employment_level_thousands=self._to_float(labor.employment_level_thousands),
            labor_force_participation_rate=self._to_float(labor.labor_force_participation_rate),
            employment_to_population_ratio=self._to_float(labor.employment_to_population_ratio),
            youth_unemployment_rate=self._to_float(labor.youth_unemployment_rate),
            nominal_wage_growth_yoy=self._to_float(labor.nominal_wage_growth_yoy),
            real_wage_growth_yoy=self._to_float(labor.real_wage_growth_yoy),
            survey_methodology=labor.survey_methodology,
            age_scope=labor.age_scope,
            seasonal_adjustment=labor.seasonal_adjustment,
        )

    # -------------------------------------------------------------------------
    # Industry & Retail
    # -------------------------------------------------------------------------

    def get_industry(self, geography_id: str) -> CountryIndustrySummaryDTO:
        ind: CountryIndustrySummary = self.repo.get_industry_summary(geography_id)
        return CountryIndustrySummaryDTO(
            geography_id=ind.geography_id,
            reference_period=ind.reference_period,
            industrial_production_index=self._to_float(ind.industrial_production_index),
            industrial_production_yoy=self._to_float(ind.industrial_production_yoy),
            manufacturing_output_yoy=self._to_float(ind.manufacturing_output_yoy),
            retail_sales_nominal_yoy=self._to_float(ind.retail_sales_nominal_yoy),
            retail_sales_real_yoy=self._to_float(ind.retail_sales_real_yoy),
            capacity_utilization_pct=self._to_float(ind.capacity_utilization_pct),
            housing_starts_annualized_thousands=self._to_float(ind.housing_starts_annualized_thousands),
            building_permits_annualized_thousands=self._to_float(ind.building_permits_annualized_thousands),
            consumer_confidence_index=self._to_float(ind.consumer_confidence_index),
            business_confidence_index=self._to_float(ind.business_confidence_index),
        )

    # -------------------------------------------------------------------------
    # Monetary & Credit
    # -------------------------------------------------------------------------

    def get_monetary(self, geography_id: str) -> CountryMonetarySummaryDTO:
        mon: CountryMonetarySummary = self.repo.get_monetary_summary(geography_id)
        return CountryMonetarySummaryDTO(
            geography_id=mon.geography_id,
            reference_period=mon.reference_period,
            policy_rate=self._to_float(mon.policy_rate),
            policy_rate_target_range=mon.policy_rate_target_range,
            m1_growth_yoy=self._to_float(mon.m1_growth_yoy),
            m2_growth_yoy=self._to_float(mon.m2_growth_yoy),
            domestic_credit_to_private_sector_pct_gdp=self._to_float(mon.domestic_credit_to_private_sector_pct_gdp),
            bank_lending_growth_yoy=self._to_float(mon.bank_lending_growth_yoy),
            monetary_area_name=mon.monetary_area_name,
            central_bank_name=mon.central_bank_name,
        )

    # -------------------------------------------------------------------------
    # Fiscal & Public Debt
    # -------------------------------------------------------------------------

    def get_fiscal(self, geography_id: str) -> CountryFiscalSummaryDTO:
        fiscal: CountryFiscalSummary = self.repo.get_fiscal_summary(geography_id)
        return CountryFiscalSummaryDTO(
            geography_id=fiscal.geography_id,
            reference_period=fiscal.reference_period,
            fiscal_year_label=fiscal.fiscal_year_label,
            accounting_scope=fiscal.accounting_scope,
            accounting_basis=fiscal.accounting_basis,
            total_revenue_billions=self._to_float(fiscal.total_revenue_billions),
            tax_revenue_billions=self._to_float(fiscal.tax_revenue_billions),
            total_expenditure_billions=self._to_float(fiscal.total_expenditure_billions),
            fiscal_balance_billions=self._to_float(fiscal.fiscal_balance_billions),
            fiscal_balance_pct_gdp=self._to_float(fiscal.fiscal_balance_pct_gdp),
            primary_balance_billions=self._to_float(fiscal.primary_balance_billions),
            primary_balance_pct_gdp=self._to_float(fiscal.primary_balance_pct_gdp),
            gross_government_debt_billions=self._to_float(fiscal.gross_government_debt_billions),
            gross_debt_pct_gdp=self._to_float(fiscal.gross_debt_pct_gdp),
            net_debt_pct_gdp=self._to_float(fiscal.net_debt_pct_gdp),
            interest_expenditure_billions=self._to_float(fiscal.interest_expenditure_billions),
            currency=fiscal.currency,
        )

    # -------------------------------------------------------------------------
    # External Sector, Trade & Balance of Payments
    # -------------------------------------------------------------------------

    def get_external(self, geography_id: str) -> CountryExternalSummaryDTO:
        ext: CountryExternalSummary = self.repo.get_external_summary(geography_id)
        return CountryExternalSummaryDTO(
            geography_id=ext.geography_id,
            reference_period=ext.reference_period,
            goods_exports_billions=self._to_float(ext.goods_exports_billions),
            goods_imports_billions=self._to_float(ext.goods_imports_billions),
            merchandise_trade_balance_billions=self._to_float(ext.merchandise_trade_balance_billions),
            services_exports_billions=self._to_float(ext.services_exports_billions),
            services_imports_billions=self._to_float(ext.services_imports_billions),
            services_trade_balance_billions=self._to_float(ext.services_trade_balance_billions),
            total_trade_balance_billions=self._to_float(ext.total_trade_balance_billions),
            current_account_balance_billions=self._to_float(ext.current_account_balance_billions),
            current_account_pct_gdp=self._to_float(ext.current_account_pct_gdp),
            fdi_net_inflow_billions=self._to_float(ext.fdi_net_inflow_billions),
            portfolio_investment_net_billions=self._to_float(ext.portfolio_investment_net_billions),
            gross_external_debt_billions=self._to_float(ext.gross_external_debt_billions),
            foreign_exchange_reserves_billions=self._to_float(ext.foreign_exchange_reserves_billions),
            fx_reserves_currency=ext.fx_reserves_currency,
            gold_reserves_fine_troy_oz_millions=self._to_float(ext.gold_reserves_fine_troy_oz_millions),
        )

    # -------------------------------------------------------------------------
    # Demographics & Structural
    # -------------------------------------------------------------------------

    def get_demographics(self, geography_id: str) -> CountryDemographicsSummaryDTO:
        demo: CountryDemographicsSummary = self.repo.get_demographics_summary(geography_id)
        return CountryDemographicsSummaryDTO(
            geography_id=demo.geography_id,
            reference_period=demo.reference_period,
            total_population_millions=float(demo.total_population_millions),
            population_growth_rate_pct=self._to_float(demo.population_growth_rate_pct),
            working_age_population_pct=self._to_float(demo.working_age_population_pct),
            youth_population_pct=self._to_float(demo.youth_population_pct),
            elderly_population_pct=self._to_float(demo.elderly_population_pct),
            urbanization_rate_pct=self._to_float(demo.urbanization_rate_pct),
            age_dependency_ratio_pct=self._to_float(demo.age_dependency_ratio_pct),
            census_source=demo.census_source,
        )

    # -------------------------------------------------------------------------
    # Coverage & Availability
    # -------------------------------------------------------------------------

    def get_coverage(self, geography_id: str) -> CountryCoverageResponseDTO:
        prof = self.repo.get_profile(geography_id)
        geo_id = prof.geography_id
        return CountryCoverageResponseDTO(
            geography_id=geo_id,
            iso_code=prof.iso_code,
            country_name=prof.name,
            available_categories=prof.available_categories,
            supported_series_count=prof.supported_series_count,
            has_gdp_expenditure=geo_id in self.repo._gdp_expenditure,
            has_gdp_production=geo_id in self.repo._gdp_production,
            has_inflation_components=geo_id in self.repo._inflation,
            has_labor_survey=geo_id in self.repo._labor,
            has_fiscal_accounts=geo_id in self.repo._fiscal,
            has_trade_bop=geo_id in self.repo._external,
            has_demographics=geo_id in self.repo._demographics,
            primary_agencies=[prof.statistical_agency, prof.central_bank_name],
        )
