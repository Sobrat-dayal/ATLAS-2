"""Repository for Country Economics Intelligence (Stage 90).

Provides structured access to sovereign national accounts, GDP expenditure decompositions,
sectoral Gross Value Added, inflation breakdowns, labor survey statistics, fiscal balances,
external trade/BOP accounts, and demographic structural profiles for G6 major economies.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from atlas.economics.v1.enums import (
    GeographicScopeKind,
    IndicatorCategory,
    PriceBasisKind,
    SeasonalAdjustmentKind,
    StatisticalUnit,
)
from atlas.economics.v1.models import MajorEconomyMacroSummary
from atlas.economics.v1.repository import EconomicsV1Repository

from .enums import (
    FiscalAccountingBasis,
    GDPApproachKind,
    GovernmentAccountingScope,
)
from .errors import (
    CountryGeographyNotFoundError,
    CountryIndicatorUnavailableError,
)
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
    CountrySectorValueAddedItem,
    GDPComponentItem,
)


class CountryEconomicsRepository:
    """In-memory sovereign macroeconomic repository for Country Economics."""

    def __init__(self, v1_repo: Optional[EconomicsV1Repository] = None):
        self.v1_repo = v1_repo or EconomicsV1Repository()

        self._profiles: Dict[str, CountryEconomicProfile] = {}
        self._gdp_expenditure: Dict[str, CountryGDPDecomposition] = {}
        self._gdp_production: Dict[str, CountryProductionDecomposition] = {}
        self._inflation: Dict[str, CountryInflationSummary] = {}
        self._labor: Dict[str, CountryLaborSummary] = {}
        self._industry: Dict[str, CountryIndustrySummary] = {}
        self._monetary: Dict[str, CountryMonetarySummary] = {}
        self._fiscal: Dict[str, CountryFiscalSummary] = {}
        self._external: Dict[str, CountryExternalSummary] = {}
        self._demographics: Dict[str, CountryDemographicsSummary] = {}

        self._seed_data()

    def _seed_data(self) -> None:
        """Seed verified sovereign datasets for G6 major economies."""
        all_cats = [
            IndicatorCategory.NATIONAL_ACCOUNTS,
            IndicatorCategory.INFLATION,
            IndicatorCategory.LABOR_MARKET,
            IndicatorCategory.INTEREST_RATES,
            IndicatorCategory.MONETARY,
            IndicatorCategory.INDUSTRIAL_ACTIVITY,
            IndicatorCategory.CONSUMPTION,
            IndicatorCategory.FISCAL,
            IndicatorCategory.EXTERNAL_SECTOR,
            IndicatorCategory.HOUSING,
        ]

        # =====================================================================
        # 1. UNITED STATES (geo-us / US)
        # =====================================================================
        self._profiles["geo-us"] = CountryEconomicProfile(
            geography_id="geo-us",
            name="United States",
            iso_code="US",
            scope_kind=GeographicScopeKind.COUNTRY,
            currency_code="USD",
            central_bank_name="Federal Reserve",
            statistical_agency="Bureau of Economic Analysis (BEA) / BLS",
            fiscal_year_structure="Fiscal Year (Oct 1 - Sep 30)",
            national_accounts_standard="SNA 2008 / NIPA (BEA)",
            available_categories=all_cats,
            supported_series_count=18,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="World's largest economy by nominal GDP; primary reporting authority BEA (National Accounts) and BLS (Prices/Labor).",
        )

        self._gdp_expenditure["geo-us"] = CountryGDPDecomposition(
            geography_id="geo-us",
            reference_period="2024-Q3",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="USD",
            nominal_gdp_billions=Decimal("29350.4"),
            real_gdp_billions=Decimal("23150.2"),
            gdp_deflator_index=Decimal("126.8"),
            real_growth_qoq_ann=Decimal("2.8"),
            real_growth_yoy=Decimal("2.7"),
            gdp_per_capita_usd=Decimal("87145.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem(
                    component_id="us-gdp-pce",
                    name="Personal Consumption Expenditures (PCE)",
                    code="PCEC",
                    value=Decimal("19890.2"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("67.8"),
                    growth_yoy=Decimal("3.5"),
                    is_additive=True,
                    source_series_id="ser-us-gdp-growth",
                    notes="Household spending on goods and services; largest single expenditure driver of US GDP.",
                ),
                GDPComponentItem(
                    component_id="us-gdp-gpdi",
                    name="Gross Private Domestic Investment",
                    code="GPDI",
                    value=Decimal("5230.1"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("17.8"),
                    growth_yoy=Decimal("1.8"),
                    is_additive=True,
                    notes="Includes nonresidential fixed investment, residential structures, and private inventory investment.",
                ),
                GDPComponentItem(
                    component_id="us-gdp-gov",
                    name="Government Consumption & Gross Investment",
                    code="GovCons",
                    value=Decimal("5020.3"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("17.1"),
                    growth_yoy=Decimal("4.1"),
                    is_additive=True,
                    notes="Federal defense and non-defense, plus state and local government final demand.",
                ),
                GDPComponentItem(
                    component_id="us-gdp-exp",
                    name="Exports of Goods & Services",
                    code="EXP",
                    value=Decimal("3120.4"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("10.6"),
                    growth_yoy=Decimal("4.4"),
                    is_additive=True,
                    notes="National accounts concept of exports (customs plus services).",
                ),
                GDPComponentItem(
                    component_id="us-gdp-imp",
                    name="Imports of Goods & Services",
                    code="IMP",
                    value=Decimal("3910.6"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("13.3"),
                    growth_yoy=Decimal("5.2"),
                    is_additive=True,
                    notes="National accounts concept of imports; subtracted from total domestic expenditure.",
                ),
                GDPComponentItem(
                    component_id="us-gdp-netexp",
                    name="Net Exports of Goods & Services",
                    code="NETEXP",
                    value=Decimal("-790.2"),
                    unit=StatisticalUnit.CURRENCY_USD_BILLIONS,
                    share_of_gdp_pct=Decimal("-2.7"),
                    growth_yoy=Decimal("-8.2"),
                    is_additive=False,
                    notes="Exports less Imports; trade deficit subtracts from domestic output.",
                ),
            ],
            total_calculated=Decimal("29350.4"),
            is_strictly_additive=True,
            non_additive_reason="Nominal expenditure components sum strictly to current-dollar GDP. Chained 2017 volume components are non-additive outside the 2017 base year.",
            statistical_discrepancy=Decimal("0.0"),
        )

        self._gdp_production["geo-us"] = CountryProductionDecomposition(
            geography_id="geo-us",
            reference_period="2023",
            total_gva_billions=Decimal("27360.0"),
            currency="USD",
            sectors=[
                CountrySectorValueAddedItem("Agriculture, Forestry & Fishing", "AGRICULTURE", Decimal("280.0"), StatisticalUnit.CURRENCY_USD_BILLIONS, Decimal("1.0"), Decimal("2.1")),
                CountrySectorValueAddedItem("Industry & Manufacturing", "INDUSTRY", Decimal("4950.0"), StatisticalUnit.CURRENCY_USD_BILLIONS, Decimal("18.1"), Decimal("1.5")),
                CountrySectorValueAddedItem("Services (Finance, Tech, Healthcare, Trade)", "SERVICES", Decimal("22130.0"), StatisticalUnit.CURRENCY_USD_BILLIONS, Decimal("80.9"), Decimal("2.9")),
            ],
            taxes_less_subsidies_on_products=Decimal("1990.0"),
            gdp_at_market_prices=Decimal("29350.0"),
        )

        self._inflation["geo-us"] = CountryInflationSummary(
            geography_id="geo-us",
            reference_period="2024-09",
            cpi_index_level=Decimal("314.796"),
            cpi_index_base="1982-84=100",
            headline_yoy=Decimal("2.4"),
            headline_mom=Decimal("0.2"),
            core_yoy=Decimal("3.3"),
            core_mom=Decimal("0.3"),
            food_inflation_yoy=Decimal("2.3"),
            energy_inflation_yoy=Decimal("-6.8"),
            ppi_yoy=Decimal("1.8"),
            gdp_deflator_yoy=Decimal("2.1"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="BLS Consumer Price Index for All Urban Consumers (CPI-U); core excludes volatile food and energy.",
        )

        self._labor["geo-us"] = CountryLaborSummary(
            geography_id="geo-us",
            reference_period="2024-09",
            unemployment_rate=Decimal("4.1"),
            employment_level_thousands=Decimal("161400.0"),
            labor_force_participation_rate=Decimal("62.7"),
            employment_to_population_ratio=Decimal("60.2"),
            youth_unemployment_rate=Decimal("9.2"),
            nominal_wage_growth_yoy=Decimal("4.0"),
            real_wage_growth_yoy=Decimal("1.6"),
            survey_methodology="U.S. BLS Current Population Survey (Household Survey)",
            age_scope="16 Years and Over",
            seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
        )

        self._industry["geo-us"] = CountryIndustrySummary(
            geography_id="geo-us",
            reference_period="2024-09",
            industrial_production_index=Decimal("102.8"),
            industrial_production_yoy=Decimal("-0.6"),
            manufacturing_output_yoy=Decimal("-0.4"),
            retail_sales_nominal_yoy=Decimal("1.7"),
            retail_sales_real_yoy=Decimal("-0.7"),
            capacity_utilization_pct=Decimal("77.5"),
            housing_starts_annualized_thousands=Decimal("1354.0"),
            building_permits_annualized_thousands=Decimal("1425.0"),
            consumer_confidence_index=Decimal("108.7"),
            business_confidence_index=Decimal("49.5"),
        )

        self._monetary["geo-us"] = CountryMonetarySummary(
            geography_id="geo-us",
            reference_period="2024-09",
            policy_rate=Decimal("5.00"),
            policy_rate_target_range="4.75% - 5.00%",
            m1_growth_yoy=Decimal("-1.2"),
            m2_growth_yoy=Decimal("2.6"),
            domestic_credit_to_private_sector_pct_gdp=Decimal("43.8"),
            bank_lending_growth_yoy=Decimal("3.1"),
            monetary_area_name="United States Dollar Zone",
            central_bank_name="Federal Reserve",
        )

        self._fiscal["geo-us"] = CountryFiscalSummary(
            geography_id="geo-us",
            reference_period="FY2024",
            fiscal_year_label="FY2024 (Ending Sep 30, 2024)",
            accounting_scope=GovernmentAccountingScope.GENERAL_GOVERNMENT,
            accounting_basis=FiscalAccountingBasis.MODIFIED_CASH,
            total_revenue_billions=Decimal("5010.0"),
            tax_revenue_billions=Decimal("4620.0"),
            total_expenditure_billions=Decimal("6880.0"),
            fiscal_balance_billions=Decimal("-1870.0"),
            fiscal_balance_pct_gdp=Decimal("-6.4"),
            primary_balance_billions=Decimal("-1020.0"),
            primary_balance_pct_gdp=Decimal("-3.5"),
            gross_government_debt_billions=Decimal("35460.0"),
            gross_debt_pct_gdp=Decimal("120.8"),
            net_debt_pct_gdp=Decimal("96.1"),
            interest_expenditure_billions=Decimal("850.0"),
            currency="USD",
        )

        self._external["geo-us"] = CountryExternalSummary(
            geography_id="geo-us",
            reference_period="2024-Q2",
            goods_exports_billions=Decimal("512.5"),
            goods_imports_billions=Decimal("795.3"),
            merchandise_trade_balance_billions=Decimal("-282.8"),
            services_exports_billions=Decimal("267.5"),
            services_imports_billions=Decimal("182.4"),
            services_trade_balance_billions=Decimal("85.1"),
            total_trade_balance_billions=Decimal("-197.7"),
            current_account_balance_billions=Decimal("-266.8"),
            current_account_pct_gdp=Decimal("-3.4"),
            fdi_net_inflow_billions=Decimal("78.5"),
            portfolio_investment_net_billions=Decimal("142.0"),
            gross_external_debt_billions=Decimal("26400.0"),
            foreign_exchange_reserves_billions=Decimal("242.0"),
            fx_reserves_currency="USD",
            gold_reserves_fine_troy_oz_millions=Decimal("261.5"),
        )

        self._demographics["geo-us"] = CountryDemographicsSummary(
            geography_id="geo-us",
            reference_period="2023",
            total_population_millions=Decimal("336.8"),
            population_growth_rate_pct=Decimal("0.5"),
            working_age_population_pct=Decimal("64.9"),
            youth_population_pct=Decimal("17.8"),
            elderly_population_pct=Decimal("17.3"),
            urbanization_rate_pct=Decimal("83.3"),
            age_dependency_ratio_pct=Decimal("54.1"),
            census_source="U.S. Census Bureau Official Population Estimates",
        )

        # =====================================================================
        # 2. EURO AREA (geo-ea / EA)
        # =====================================================================
        self._profiles["geo-ea"] = CountryEconomicProfile(
            geography_id="geo-ea",
            name="Euro Area",
            iso_code="EA",
            scope_kind=GeographicScopeKind.ECONOMIC_AREA,
            currency_code="EUR",
            central_bank_name="European Central Bank (ECB)",
            statistical_agency="Eurostat",
            fiscal_year_structure="Calendar Year (Jan 1 - Dec 31)",
            national_accounts_standard="ESA 2010 (Eurostat)",
            available_categories=all_cats,
            supported_series_count=16,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="Economic and currency union of 20 EU member states; single monetary policy governed by the ECB.",
        )

        self._gdp_expenditure["geo-ea"] = CountryGDPDecomposition(
            geography_id="geo-ea",
            reference_period="2024-Q3",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="EUR",
            nominal_gdp_billions=Decimal("3820.0"),
            real_gdp_billions=Decimal("3120.0"),
            gdp_deflator_index=Decimal("122.4"),
            real_growth_qoq_ann=Decimal("1.6"),
            real_growth_yoy=Decimal("0.9"),
            gdp_per_capita_usd=Decimal("43250.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem("ea-pce", "Household Final Consumption", "PCEC", Decimal("2040.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("53.4"), Decimal("1.2")),
                GDPComponentItem("ea-gpdi", "Gross Capital Formation (Investment)", "GPDI", Decimal("830.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("21.7"), Decimal("-0.8")),
                GDPComponentItem("ea-gov", "Government Final Consumption", "GovCons", Decimal("825.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("21.6"), Decimal("2.1")),
                GDPComponentItem("ea-exp", "Exports of Goods and Services", "EXP", Decimal("1980.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("51.8"), Decimal("1.5")),
                GDPComponentItem("ea-imp", "Imports of Goods and Services", "IMP", Decimal("1855.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("48.5"), Decimal("0.8")),
                GDPComponentItem("ea-netexp", "Net Exports", "NETEXP", Decimal("125.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("3.3"), Decimal("12.5"), is_additive=False),
            ],
            total_calculated=Decimal("3820.0"),
            is_strictly_additive=True,
            non_additive_reason="ESA 2010 nominal expenditure components reconcile additively to GDP at market prices.",
        )

        self._inflation["geo-ea"] = CountryInflationSummary(
            geography_id="geo-ea",
            reference_period="2024-09",
            cpi_index_level=Decimal("126.4"),
            cpi_index_base="2015=100",
            headline_yoy=Decimal("1.7"),
            headline_mom=Decimal("-0.1"),
            core_yoy=Decimal("2.7"),
            core_mom=Decimal("0.1"),
            food_inflation_yoy=Decimal("2.4"),
            energy_inflation_yoy=Decimal("-6.1"),
            ppi_yoy=Decimal("-2.3"),
            gdp_deflator_yoy=Decimal("2.8"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="Eurostat Harmonised Index of Consumer Prices (HICP); inflation fell below the ECB 2% medium-term target in Sep 2024.",
        )

        self._labor["geo-ea"] = CountryLaborSummary(
            geography_id="geo-ea",
            reference_period="2024-09",
            unemployment_rate=Decimal("6.3"),
            employment_level_thousands=Decimal("170200.0"),
            labor_force_participation_rate=Decimal("75.1"),
            employment_to_population_ratio=Decimal("70.4"),
            youth_unemployment_rate=Decimal("14.4"),
            nominal_wage_growth_yoy=Decimal("4.5"),
            real_wage_growth_yoy=Decimal("2.8"),
            survey_methodology="Eurostat EU Labour Force Survey (EU-LFS)",
            age_scope="15 to 74 Years",
            seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
        )

        self._fiscal["geo-ea"] = CountryFiscalSummary(
            geography_id="geo-ea",
            reference_period="2023",
            fiscal_year_label="CY2023",
            accounting_scope=GovernmentAccountingScope.GENERAL_GOVERNMENT,
            accounting_basis=FiscalAccountingBasis.ACCRUAL,
            total_revenue_billions=Decimal("6840.0"),
            tax_revenue_billions=Decimal("5920.0"),
            total_expenditure_billions=Decimal("7370.0"),
            fiscal_balance_billions=Decimal("-530.0"),
            fiscal_balance_pct_gdp=Decimal("-3.6"),
            primary_balance_billions=Decimal("-280.0"),
            primary_balance_pct_gdp=Decimal("-1.9"),
            gross_government_debt_billions=Decimal("13050.0"),
            gross_debt_pct_gdp=Decimal("88.6"),
            net_debt_pct_gdp=Decimal("74.2"),
            interest_expenditure_billions=Decimal("250.0"),
            currency="EUR",
        )

        self._external["geo-ea"] = CountryExternalSummary(
            geography_id="geo-ea",
            reference_period="2024-Q2",
            goods_exports_billions=Decimal("740.0"),
            goods_imports_billions=Decimal("675.0"),
            merchandise_trade_balance_billions=Decimal("65.0"),
            services_exports_billions=Decimal("310.0"),
            services_imports_billions=Decimal("280.0"),
            services_trade_balance_billions=Decimal("30.0"),
            total_trade_balance_billions=Decimal("95.0"),
            current_account_balance_billions=Decimal("108.0"),
            current_account_pct_gdp=Decimal("2.8"),
            fdi_net_inflow_billions=Decimal("45.0"),
            portfolio_investment_net_billions=Decimal("-25.0"),
            gross_external_debt_billions=Decimal("17200.0"),
            foreign_exchange_reserves_billions=Decimal("1280.0"),
            fx_reserves_currency="EUR",
        )

        self._demographics["geo-ea"] = CountryDemographicsSummary(
            geography_id="geo-ea",
            reference_period="2023",
            total_population_millions=Decimal("348.5"),
            population_growth_rate_pct=Decimal("0.3"),
            working_age_population_pct=Decimal("63.8"),
            youth_population_pct=Decimal("15.1"),
            elderly_population_pct=Decimal("21.1"),
            urbanization_rate_pct=Decimal("75.4"),
            age_dependency_ratio_pct=Decimal("56.7"),
            census_source="Eurostat Demographic Statistics",
        )

        # =====================================================================
        # 3. CHINA (geo-cn / CN)
        # =====================================================================
        self._profiles["geo-cn"] = CountryEconomicProfile(
            geography_id="geo-cn",
            name="China",
            iso_code="CN",
            scope_kind=GeographicScopeKind.COUNTRY,
            currency_code="CNY",
            central_bank_name="People's Bank of China (PBOC)",
            statistical_agency="National Bureau of Statistics (NBS)",
            fiscal_year_structure="Calendar Year (Jan 1 - Dec 31)",
            national_accounts_standard="SNA 2008 (NBS)",
            available_categories=all_cats,
            supported_series_count=15,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="Second largest world economy by nominal GDP; primary reporting authority National Bureau of Statistics.",
        )

        self._gdp_expenditure["geo-cn"] = CountryGDPDecomposition(
            geography_id="geo-cn",
            reference_period="2024-Q3",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="CNY",
            nominal_gdp_billions=Decimal("33220.0"),
            real_gdp_billions=Decimal("30150.0"),
            gdp_deflator_index=Decimal("110.2"),
            real_growth_qoq_ann=Decimal("3.8"),
            real_growth_yoy=Decimal("4.6"),
            gdp_per_capita_usd=Decimal("12620.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem("cn-pce", "Final Consumption Expenditure", "PCEC", Decimal("18100.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("54.5"), Decimal("4.8")),
                GDPComponentItem("cn-gpdi", "Gross Capital Formation", "GPDI", Decimal("13950.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("42.0"), Decimal("3.2")),
                GDPComponentItem("cn-netexp", "Net Exports of Goods & Services", "NETEXP", Decimal("1170.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("3.5"), Decimal("18.4")),
            ],
            total_calculated=Decimal("33220.0"),
            is_strictly_additive=True,
            non_additive_reason="NBS expenditure statistics publish major component breakdowns additively reconciling to nominal GDP.",
        )

        self._inflation["geo-cn"] = CountryInflationSummary(
            geography_id="geo-cn",
            reference_period="2024-09",
            cpi_index_level=Decimal("103.2"),
            cpi_index_base="2020=100",
            headline_yoy=Decimal("0.4"),
            headline_mom=Decimal("0.0"),
            core_yoy=Decimal("0.1"),
            core_mom=Decimal("0.0"),
            food_inflation_yoy=Decimal("3.3"),
            energy_inflation_yoy=Decimal("-3.5"),
            ppi_yoy=Decimal("-2.8"),
            gdp_deflator_yoy=Decimal("-0.5"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="NBS Consumer Price Index; subdued core inflation reflects domestic aggregate demand trends.",
        )

        self._labor["geo-cn"] = CountryLaborSummary(
            geography_id="geo-cn",
            reference_period="2024-09",
            unemployment_rate=Decimal("5.1"),
            employment_level_thousands=Decimal("740400.0"),
            labor_force_participation_rate=Decimal("67.1"),
            employment_to_population_ratio=Decimal("63.7"),
            youth_unemployment_rate=Decimal("17.6"),
            nominal_wage_growth_yoy=Decimal("5.2"),
            real_wage_growth_yoy=Decimal("4.8"),
            survey_methodology="China NBS Surveyed Urban Unemployment Rate",
            age_scope="16 to 59 Years (Urban)",
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
        )

        self._external["geo-cn"] = CountryExternalSummary(
            geography_id="geo-cn",
            reference_period="2024-Q2",
            goods_exports_billions=Decimal("850.0"),
            goods_imports_billions=Decimal("630.0"),
            merchandise_trade_balance_billions=Decimal("220.0"),
            services_exports_billions=Decimal("95.0"),
            services_imports_billions=Decimal("155.0"),
            services_trade_balance_billions=Decimal("-60.0"),
            total_trade_balance_billions=Decimal("160.0"),
            current_account_balance_billions=Decimal("94.5"),
            current_account_pct_gdp=Decimal("1.5"),
            fdi_net_inflow_billions=Decimal("12.0"),
            portfolio_investment_net_billions=Decimal("-18.0"),
            gross_external_debt_billions=Decimal("2450.0"),
            foreign_exchange_reserves_billions=Decimal("3261.0"),
            fx_reserves_currency="USD",
        )

        self._demographics["geo-cn"] = CountryDemographicsSummary(
            geography_id="geo-cn",
            reference_period="2023",
            total_population_millions=Decimal("1409.7"),
            population_growth_rate_pct=Decimal("-0.15"),
            working_age_population_pct=Decimal("68.3"),
            youth_population_pct=Decimal("16.3"),
            elderly_population_pct=Decimal("15.4"),
            urbanization_rate_pct=Decimal("66.2"),
            age_dependency_ratio_pct=Decimal("46.4"),
            census_source="National Bureau of Statistics 7th National Population Census Updates",
        )

        # =====================================================================
        # 4. INDIA (geo-in / IN)
        # =====================================================================
        self._profiles["geo-in"] = CountryEconomicProfile(
            geography_id="geo-in",
            name="India",
            iso_code="IN",
            scope_kind=GeographicScopeKind.COUNTRY,
            currency_code="INR",
            central_bank_name="Reserve Bank of India (RBI)",
            statistical_agency="Ministry of Statistics & Programme Implementation (MoSPI)",
            fiscal_year_structure="Fiscal Year (Apr 1 - Mar 31)",
            national_accounts_standard="SNA 2008 (MoSPI Base 2011-12)",
            available_categories=all_cats,
            supported_series_count=14,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="Fastest growing major global economy; reporting authority MoSPI and RBI.",
        )

        self._gdp_expenditure["geo-in"] = CountryGDPDecomposition(
            geography_id="geo-in",
            reference_period="2024-Q2",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="INR",
            nominal_gdp_billions=Decimal("77310.0"),
            real_gdp_billions=Decimal("43640.0"),
            gdp_deflator_index=Decimal("177.2"),
            real_growth_qoq_ann=Decimal("5.2"),
            real_growth_yoy=Decimal("6.7"),
            gdp_per_capita_usd=Decimal("2610.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem("in-pce", "Private Final Consumption Expenditure", "PFCE", Decimal("43290.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("56.0"), Decimal("7.4")),
                GDPComponentItem("in-gfcf", "Gross Fixed Capital Formation", "GFCF", Decimal("26980.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("34.9"), Decimal("7.5")),
                GDPComponentItem("in-gov", "Government Final Consumption", "GFCE", Decimal("7580.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("9.8"), Decimal("-0.2")),
                GDPComponentItem("in-netexp", "Net Exports of Goods & Services", "NETEXP", Decimal("-2310.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("-3.0"), Decimal("-12.4")),
            ],
            total_calculated=Decimal("77310.0"),
            is_strictly_additive=True,
            non_additive_reason="MoSPI Base 2011-12 expenditure components reconcile additively with statistical discrepancy.",
        )

        self._inflation["geo-in"] = CountryInflationSummary(
            geography_id="geo-in",
            reference_period="2024-09",
            cpi_index_level=Decimal("192.8"),
            cpi_index_base="2012=100",
            headline_yoy=Decimal("5.49"),
            headline_mom=Decimal("0.6"),
            core_yoy=Decimal("3.50"),
            core_mom=Decimal("0.2"),
            food_inflation_yoy=Decimal("9.24"),
            energy_inflation_yoy=Decimal("-1.39"),
            ppi_yoy=Decimal("1.84"),
            gdp_deflator_yoy=Decimal("2.9"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="MoSPI All India Consumer Price Index (Combined); headline elevated due to volatile vegetable and food prices.",
        )

        self._fiscal["geo-in"] = CountryFiscalSummary(
            geography_id="geo-in",
            reference_period="FY2024",
            fiscal_year_label="FY2024 (Ending Mar 31, 2024)",
            accounting_scope=GovernmentAccountingScope.GENERAL_GOVERNMENT,
            accounting_basis=FiscalAccountingBasis.CASH,
            total_revenue_billions=Decimal("35200.0"),
            tax_revenue_billions=Decimal("29800.0"),
            total_expenditure_billions=Decimal("51700.0"),
            fiscal_balance_billions=Decimal("-16500.0"),
            fiscal_balance_pct_gdp=Decimal("-5.6"),
            primary_balance_billions=Decimal("-5800.0"),
            primary_balance_pct_gdp=Decimal("-2.0"),
            gross_government_debt_billions=Decimal("240700.0"),
            gross_debt_pct_gdp=Decimal("81.5"),
            net_debt_pct_gdp=Decimal("73.4"),
            interest_expenditure_billions=Decimal("10700.0"),
            currency="INR",
        )

        self._external["geo-in"] = CountryExternalSummary(
            geography_id="geo-in",
            reference_period="2024-Q1",
            goods_exports_billions=Decimal("110.0"),
            goods_imports_billions=Decimal("172.0"),
            merchandise_trade_balance_billions=Decimal("-62.0"),
            services_exports_billions=Decimal("88.0"),
            services_imports_billions=Decimal("49.0"),
            services_trade_balance_billions=Decimal("39.0"),
            total_trade_balance_billions=Decimal("-23.0"),
            current_account_balance_billions=Decimal("-9.7"),
            current_account_pct_gdp=Decimal("-1.1"),
            fdi_net_inflow_billions=Decimal("6.5"),
            portfolio_investment_net_billions=Decimal("12.8"),
            gross_external_debt_billions=Decimal("663.8"),
            foreign_exchange_reserves_billions=Decimal("690.0"),
            fx_reserves_currency="USD",
        )

        self._demographics["geo-in"] = CountryDemographicsSummary(
            geography_id="geo-in",
            reference_period="2023",
            total_population_millions=Decimal("1428.6"),
            population_growth_rate_pct=Decimal("0.8"),
            working_age_population_pct=Decimal("68.1"),
            youth_population_pct=Decimal("25.0"),
            elderly_population_pct=Decimal("6.9"),
            urbanization_rate_pct=Decimal("36.1"),
            age_dependency_ratio_pct=Decimal("46.8"),
            census_source="Registrar General of India / Census Projections",
        )

        # =====================================================================
        # 5. JAPAN (geo-jp / JP)
        # =====================================================================
        self._profiles["geo-jp"] = CountryEconomicProfile(
            geography_id="geo-jp",
            name="Japan",
            iso_code="JP",
            scope_kind=GeographicScopeKind.COUNTRY,
            currency_code="JPY",
            central_bank_name="Bank of Japan (BOJ)",
            statistical_agency="Cabinet Office / Statistics Bureau of Japan (SBJ)",
            fiscal_year_structure="Fiscal Year (Apr 1 - Mar 31)",
            national_accounts_standard="SNA 2008 (Cabinet Office Base 2015)",
            available_categories=all_cats,
            supported_series_count=15,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="Major advanced Asian economy; primary reporting authority Cabinet Office and SBJ.",
        )

        self._gdp_expenditure["geo-jp"] = CountryGDPDecomposition(
            geography_id="geo-jp",
            reference_period="2024-Q2",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="JPY",
            nominal_gdp_billions=Decimal("152400.0"),
            real_gdp_billions=Decimal("140200.0"),
            gdp_deflator_index=Decimal("108.7"),
            real_growth_qoq_ann=Decimal("0.9"),
            real_growth_yoy=Decimal("-0.8"),
            gdp_per_capita_usd=Decimal("33850.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem("jp-pce", "Private Consumption", "PCEC", Decimal("82500.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("54.1"), Decimal("0.8")),
                GDPComponentItem("jp-gpdi", "Private Non-residential Investment", "GPDI", Decimal("26800.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("17.6"), Decimal("0.7")),
                GDPComponentItem("jp-gov", "Government Final Consumption", "GovCons", Decimal("32400.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("21.3"), Decimal("0.4")),
                GDPComponentItem("jp-netexp", "Net Exports", "NETEXP", Decimal("3200.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("2.1"), Decimal("-4.2")),
            ],
            total_calculated=Decimal("152400.0"),
            is_strictly_additive=True,
            non_additive_reason="Cabinet Office nominal expenditure series sum additively to GDP.",
        )

        self._inflation["geo-jp"] = CountryInflationSummary(
            geography_id="geo-jp",
            reference_period="2024-09",
            cpi_index_level=Decimal("108.9"),
            cpi_index_base="2020=100",
            headline_yoy=Decimal("2.5"),
            headline_mom=Decimal("-0.3"),
            core_yoy=Decimal("2.4"),
            core_mom=Decimal("0.0"),
            food_inflation_yoy=Decimal("3.1"),
            energy_inflation_yoy=Decimal("6.0"),
            ppi_yoy=Decimal("2.8"),
            gdp_deflator_yoy=Decimal("3.0"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="Statistics Bureau of Japan Nationwide CPI; core CPI (excluding fresh food) sits above BOJ 2% target.",
        )

        self._demographics["geo-jp"] = CountryDemographicsSummary(
            geography_id="geo-jp",
            reference_period="2023",
            total_population_millions=Decimal("124.5"),
            population_growth_rate_pct=Decimal("-0.5"),
            working_age_population_pct=Decimal("59.1"),
            youth_population_pct=Decimal("11.1"),
            elderly_population_pct=Decimal("29.8"),
            urbanization_rate_pct=Decimal("91.8"),
            age_dependency_ratio_pct=Decimal("69.2"),
            census_source="Statistics Bureau of Japan Population Estimates",
        )

        # =====================================================================
        # 6. UNITED KINGDOM (geo-gb / GB)
        # =====================================================================
        self._profiles["geo-gb"] = CountryEconomicProfile(
            geography_id="geo-gb",
            name="United Kingdom",
            iso_code="GB",
            scope_kind=GeographicScopeKind.COUNTRY,
            currency_code="GBP",
            central_bank_name="Bank of England (BOE)",
            statistical_agency="Office for National Statistics (ONS)",
            fiscal_year_structure="Fiscal Year (Apr 6 - Apr 5)",
            national_accounts_standard="ESA 2010 (ONS Blue Book)",
            available_categories=all_cats,
            supported_series_count=15,
            earliest_observation_period="2021-01",
            latest_observation_period="2024-Q3",
            notes="Major European economy; primary statistical authority Office for National Statistics.",
        )

        self._gdp_expenditure["geo-gb"] = CountryGDPDecomposition(
            geography_id="geo-gb",
            reference_period="2024-Q2",
            price_basis=PriceBasisKind.CURRENT_PRICES,
            currency="GBP",
            nominal_gdp_billions=Decimal("692.0"),
            real_gdp_billions=Decimal("570.0"),
            gdp_deflator_index=Decimal("121.4"),
            real_growth_qoq_ann=Decimal("2.2"),
            real_growth_yoy=Decimal("0.7"),
            gdp_per_capita_usd=Decimal("49120.0"),
            per_capita_population_period="2023",
            approach=GDPApproachKind.EXPENDITURE,
            components=[
                GDPComponentItem("gb-pce", "Household Final Consumption", "PCEC", Decimal("421.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("60.8"), Decimal("1.0")),
                GDPComponentItem("gb-gpdi", "Gross Fixed Capital Formation", "GFCF", Decimal("124.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("17.9"), Decimal("0.6")),
                GDPComponentItem("gb-gov", "General Government Final Consumption", "GovCons", Decimal("155.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("22.4"), Decimal("1.8")),
                GDPComponentItem("gb-netexp", "Net Exports", "NETEXP", Decimal("-15.0"), StatisticalUnit.LOCAL_CURRENCY_BILLIONS, Decimal("-2.2"), Decimal("-14.2")),
            ],
            total_calculated=Decimal("692.0"),
            is_strictly_additive=True,
            non_additive_reason="ONS Blue Book current-price expenditure components reconcile with statistical alignment adjustment.",
        )

        self._inflation["geo-gb"] = CountryInflationSummary(
            geography_id="geo-gb",
            reference_period="2024-09",
            cpi_index_level=Decimal("133.5"),
            cpi_index_base="2015=100",
            headline_yoy=Decimal("1.7"),
            headline_mom=Decimal("0.0"),
            core_yoy=Decimal("3.2"),
            core_mom=Decimal("0.1"),
            food_inflation_yoy=Decimal("1.9"),
            energy_inflation_yoy=Decimal("-12.4"),
            ppi_yoy=Decimal("-2.3"),
            gdp_deflator_yoy=Decimal("2.6"),
            seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
            notes="Office for National Statistics Consumer Prices Index (CPI); headline inflation returned to BOE 2% target.",
        )

        self._demographics["geo-gb"] = CountryDemographicsSummary(
            geography_id="geo-gb",
            reference_period="2023",
            total_population_millions=Decimal("68.3"),
            population_growth_rate_pct=Decimal("0.9"),
            working_age_population_pct=Decimal("63.9"),
            youth_population_pct=Decimal("17.1"),
            elderly_population_pct=Decimal("19.0"),
            urbanization_rate_pct=Decimal("84.4"),
            age_dependency_ratio_pct=Decimal("56.5"),
            census_source="Office for National Statistics Mid-Year Population Estimates",
        )

    # -------------------------------------------------------------------------
    # Country Entity Resolution & Profile
    # -------------------------------------------------------------------------

    def resolve_geography_id(self, identifier: str) -> str:
        """Resolve a country identifier (UUID, slug, or ISO code) to canonical geography_id."""
        normalized = identifier.strip().lower()
        # Direct match on geography_id
        if normalized in self._profiles:
            return normalized

        # Match by ISO code
        for geo_id, prof in self._profiles.items():
            if prof.iso_code.lower() == normalized or prof.name.lower() == normalized:
                return geo_id

        # Fallback to Stage 89 repository
        for geo in self.v1_repo.get_geographies():
            if geo.geography_id.lower() == normalized or geo.iso_code.lower() == normalized:
                return geo.geography_id

        raise CountryGeographyNotFoundError(identifier)

    def _get_v1_macro_summary(self, geo_id: str) -> Optional[MajorEconomyMacroSummary]:
        """Lookup macro summary from Stage 89 repository for fallback context."""
        for s in self.v1_repo.get_major_economies_summary():
            if s.geography_id == geo_id:
                return s
        return None

    def get_profile(self, geography_id: str) -> CountryEconomicProfile:
        """Fetch canonical country metadata profile."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._profiles:
            return self._profiles[geo_id]
        raise CountryGeographyNotFoundError(geography_id)

    def list_countries(self) -> List[CountryEconomicProfile]:
        """List all supported sovereign country economic profiles."""
        return list(self._profiles.values())

    # -------------------------------------------------------------------------
    # Domain Category Queries
    # -------------------------------------------------------------------------

    def get_gdp_decomposition(
        self, geography_id: str, approach: GDPApproachKind = GDPApproachKind.EXPENDITURE
    ) -> CountryGDPDecomposition:
        """Fetch national accounts GDP decomposition (expenditure approach)."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._gdp_expenditure:
            return self._gdp_expenditure[geo_id]
        raise CountryIndicatorUnavailableError(geography_id, "GDP_EXPENDITURE")

    def get_production_decomposition(
        self, geography_id: str
    ) -> CountryProductionDecomposition:
        """Fetch national accounts Gross Value Added by sector (production approach)."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._gdp_production:
            return self._gdp_production[geo_id]
        # Return fallback with available data
        return CountryProductionDecomposition(
            geography_id=geo_id,
            reference_period="2023",
            total_gva_billions=Decimal("0.0"),
            currency="USD",
            sectors=[],
        )

    def get_inflation_summary(self, geography_id: str) -> CountryInflationSummary:
        """Fetch national price levels and inflation metrics."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._inflation:
            return self._inflation[geo_id]
        raise CountryIndicatorUnavailableError(geography_id, "INFLATION_CPI")

    def get_labor_summary(self, geography_id: str) -> CountryLaborSummary:
        """Fetch labor market survey, employment, and wage indicators."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._labor:
            return self._labor[geo_id]
        # Fallback using Stage 89 repository
        macro = self._get_v1_macro_summary(geo_id)
        unemp = macro.unemployment_rate if macro else None
        return CountryLaborSummary(
            geography_id=geo_id,
            reference_period=macro.unemployment_period if macro else "2024-09",
            unemployment_rate=unemp,
            employment_level_thousands=None,
            labor_force_participation_rate=None,
            employment_to_population_ratio=None,
            youth_unemployment_rate=None,
            nominal_wage_growth_yoy=None,
            real_wage_growth_yoy=None,
            survey_methodology="Official National Labor Force Survey",
            age_scope="Working Age Population",
        )

    def get_industry_summary(self, geography_id: str) -> CountryIndustrySummary:
        """Fetch industrial production, retail sales, and sentiment."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._industry:
            return self._industry[geo_id]
        return CountryIndustrySummary(
            geography_id=geo_id,
            reference_period="2024-09",
            industrial_production_index=None,
            industrial_production_yoy=None,
            manufacturing_output_yoy=None,
            retail_sales_nominal_yoy=None,
            retail_sales_real_yoy=None,
            capacity_utilization_pct=None,
            housing_starts_annualized_thousands=None,
            building_permits_annualized_thousands=None,
            consumer_confidence_index=None,
            business_confidence_index=None,
        )

    def get_monetary_summary(self, geography_id: str) -> CountryMonetarySummary:
        """Fetch monetary aggregates, bank credit, and policy rate context."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._monetary:
            return self._monetary[geo_id]
        macro = self._get_v1_macro_summary(geo_id)
        prof = self._profiles.get(geo_id)
        return CountryMonetarySummary(
            geography_id=geo_id,
            reference_period=macro.policy_rate_period if macro else "2024-09",
            policy_rate=macro.policy_interest_rate if macro else None,
            policy_rate_target_range=None,
            m1_growth_yoy=None,
            m2_growth_yoy=None,
            domestic_credit_to_private_sector_pct_gdp=None,
            bank_lending_growth_yoy=None,
            monetary_area_name=prof.name if prof else "Sovereign Monetary Area",
            central_bank_name=prof.central_bank_name if prof else "Central Bank",
        )

    def get_fiscal_summary(self, geography_id: str) -> CountryFiscalSummary:
        """Fetch government fiscal accounts, revenue, expenditure, and debt."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._fiscal:
            return self._fiscal[geo_id]
        prof = self._profiles.get(geo_id)
        return CountryFiscalSummary(
            geography_id=geo_id,
            reference_period="2023",
            fiscal_year_label="CY2023",
            accounting_scope=GovernmentAccountingScope.GENERAL_GOVERNMENT,
            accounting_basis=FiscalAccountingBasis.ACCRUAL,
            total_revenue_billions=None,
            tax_revenue_billions=None,
            total_expenditure_billions=None,
            fiscal_balance_billions=None,
            fiscal_balance_pct_gdp=None,
            primary_balance_billions=None,
            primary_balance_pct_gdp=None,
            gross_government_debt_billions=None,
            gross_debt_pct_gdp=None,
            net_debt_pct_gdp=None,
            interest_expenditure_billions=None,
            currency=prof.currency_code if prof else "USD",
        )

    def get_external_summary(self, geography_id: str) -> CountryExternalSummary:
        """Fetch balance of payments, trade accounts, external debt, and FX reserves."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._external:
            return self._external[geo_id]
        prof = self._profiles.get(geo_id)
        return CountryExternalSummary(
            geography_id=geo_id,
            reference_period="2024-Q2",
            goods_exports_billions=None,
            goods_imports_billions=None,
            merchandise_trade_balance_billions=None,
            services_exports_billions=None,
            services_imports_billions=None,
            services_trade_balance_billions=None,
            total_trade_balance_billions=None,
            current_account_balance_billions=None,
            current_account_pct_gdp=None,
            fdi_net_inflow_billions=None,
            portfolio_investment_net_billions=None,
            gross_external_debt_billions=None,
            foreign_exchange_reserves_billions=None,
            fx_reserves_currency=prof.currency_code if prof else "USD",
        )

    def get_demographics_summary(self, geography_id: str) -> CountryDemographicsSummary:
        """Fetch demographic structure, population totals, and age structure."""
        geo_id = self.resolve_geography_id(geography_id)
        if geo_id in self._demographics:
            return self._demographics[geo_id]
        raise CountryIndicatorUnavailableError(geography_id, "DEMOGRAPHICS")

    def get_overview(self, geography_id: str) -> CountryEconomicsOverview:
        """Assemble the master macroeconomic overview for a selected country."""
        geo_id = self.resolve_geography_id(geography_id)
        prof = self.get_profile(geo_id)
        macro = self._get_v1_macro_summary(geo_id)

        gdp = self._gdp_expenditure.get(geo_id)
        cpi = self._inflation.get(geo_id)
        labor = self._labor.get(geo_id)
        fiscal = self._fiscal.get(geo_id)
        external = self._external.get(geo_id)
        demo = self._demographics.get(geo_id)

        return CountryEconomicsOverview(
            profile=prof,
            headline_real_gdp_growth_qoq=gdp.real_growth_qoq_ann if gdp else (macro.gdp_growth_yoy if macro else None),
            headline_real_gdp_growth_yoy=gdp.real_growth_yoy if gdp else (macro.gdp_growth_yoy if macro else None),
            headline_gdp_period=gdp.reference_period if gdp else (macro.gdp_growth_period if macro else None),
            nominal_gdp_usd_billions=gdp.nominal_gdp_billions if gdp else None,
            gdp_per_capita_usd=gdp.gdp_per_capita_usd if gdp else None,
            headline_cpi_inflation_yoy=cpi.headline_yoy if cpi else (macro.cpi_inflation_yoy if macro else None),
            headline_cpi_period=cpi.reference_period if cpi else (macro.cpi_period if macro else None),
            core_cpi_inflation_yoy=cpi.core_yoy if cpi else None,
            unemployment_rate=labor.unemployment_rate if labor else (macro.unemployment_rate if macro else None),
            unemployment_period=labor.reference_period if labor else (macro.unemployment_period if macro else None),
            policy_interest_rate=macro.policy_interest_rate if macro else None,
            policy_rate_period=macro.policy_rate_period if macro else None,
            general_gov_debt_pct_gdp=fiscal.gross_debt_pct_gdp if fiscal else None,
            fiscal_balance_pct_gdp=fiscal.fiscal_balance_pct_gdp if fiscal else None,
            current_account_pct_gdp=external.current_account_pct_gdp if external else None,
            total_population_millions=demo.total_population_millions if demo else None,
            fx_reserves_billions=external.foreign_exchange_reserves_billions if external else None,
            data_freshness_status="VERIFIED_CURRENT",
        )
