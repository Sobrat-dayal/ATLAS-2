"""In-Memory Repository for Institutional Economics V1 (Stage 89).

Seeded with canonical indicators, official provider series, major economies
(US, Euro Area, China, India, Japan, UK), multi-period historical observations,
and point-in-time revision vintages.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from .enums import (
    GeographicScopeKind,
    IndicatorCategory,
    ObservationStatus,
    PriceBasisKind,
    ReportingFrequency,
    SeasonalAdjustmentKind,
    StatisticalUnit,
)
from .models import (
    EconomicGeography,
    EconomicIndicator,
    EconomicObservationRecord,
    EconomicSeries,
    EconomicVintageRecord,
    MajorEconomyMacroSummary,
)


class EconomicsV1Repository:
    """Authoritative repository for economic indicators, series, and observations."""

    def __init__(self) -> None:
        self._geographies: Dict[str, EconomicGeography] = {}
        self._indicators: Dict[str, EconomicIndicator] = {}
        self._series: Dict[str, EconomicSeries] = {}
        self._observations: Dict[str, List[EconomicObservationRecord]] = {}
        self._vintages: Dict[str, List[EconomicVintageRecord]] = {}

        self._seed_geographies()
        self._seed_indicators()
        self._seed_series()
        self._seed_observations()
        self._seed_vintages()

    def get_geographies(self) -> List[EconomicGeography]:
        return list(self._geographies.values())

    def get_geography(self, geography_id: str) -> Optional[EconomicGeography]:
        return self._geographies.get(geography_id)

    def get_indicators(self, category: Optional[IndicatorCategory] = None) -> List[EconomicIndicator]:
        indicators = list(self._indicators.values())
        if category:
            indicators = [i for i in indicators if i.category == category]
        return indicators

    def get_indicator(self, indicator_id: str) -> Optional[EconomicIndicator]:
        return self._indicators.get(indicator_id)

    def get_series_list(
        self,
        indicator_id: Optional[str] = None,
        geography_id: Optional[str] = None,
        category: Optional[IndicatorCategory] = None,
    ) -> List[EconomicSeries]:
        results = list(self._series.values())
        if indicator_id:
            results = [s for s in results if s.indicator_id == indicator_id]
        if geography_id:
            results = [s for s in results if s.geography_id == geography_id]
        if category:
            matching_ind_ids = {
                ind.indicator_id for ind in self._indicators.values() if ind.category == category
            }
            results = [s for s in results if s.indicator_id in matching_ind_ids]
        return results

    def get_series(self, series_id: str) -> Optional[EconomicSeries]:
        return self._series.get(series_id)

    def get_observations(self, series_id: str) -> List[EconomicObservationRecord]:
        return list(self._observations.get(series_id, []))

    def get_vintages(self, series_id: str) -> List[EconomicVintageRecord]:
        return list(self._vintages.get(series_id, []))

    def get_major_economies_summary(self) -> List[MajorEconomyMacroSummary]:
        summaries: List[MajorEconomyMacroSummary] = []
        core_geos = [g for g in self._geographies.values() if g.is_core]

        for geo in core_geos:
            # Locate series for GDP, CPI, Unemp, Policy Rate
            gdp_series = next(
                (s for s in self._series.values() if s.geography_id == geo.geography_id and s.indicator_id == "ind-gdp-growth-yoy"),
                None,
            )
            cpi_series = next(
                (s for s in self._series.values() if s.geography_id == geo.geography_id and s.indicator_id == "ind-cpi-yoy"),
                None,
            )
            unemp_series = next(
                (s for s in self._series.values() if s.geography_id == geo.geography_id and s.indicator_id == "ind-unemp-rate"),
                None,
            )
            rate_series = next(
                (s for s in self._series.values() if s.geography_id == geo.geography_id and s.indicator_id == "ind-policy-rate"),
                None,
            )

            # Latest observations
            gdp_obs = self._observations.get(gdp_series.series_id, [])[-1] if gdp_series and self._observations.get(gdp_series.series_id) else None
            cpi_obs = self._observations.get(cpi_series.series_id, [])[-1] if cpi_series and self._observations.get(cpi_series.series_id) else None
            unemp_obs = self._observations.get(unemp_series.series_id, [])[-1] if unemp_series and self._observations.get(unemp_series.series_id) else None
            rate_obs = self._observations.get(rate_series.series_id, [])[-1] if rate_series and self._observations.get(rate_series.series_id) else None

            summaries.append(
                MajorEconomyMacroSummary(
                    geography_id=geo.geography_id,
                    geography_name=geo.name,
                    iso_code=geo.iso_code,
                    currency_code=geo.currency_code,
                    gdp_growth_yoy=gdp_obs.value if gdp_obs else None,
                    gdp_growth_period=gdp_obs.period if gdp_obs else None,
                    gdp_source=gdp_series.provider_id if gdp_series else None,
                    cpi_inflation_yoy=cpi_obs.value if cpi_obs else None,
                    cpi_period=cpi_obs.period if cpi_obs else None,
                    cpi_source=cpi_series.provider_id if cpi_series else None,
                    unemployment_rate=unemp_obs.value if unemp_obs else None,
                    unemployment_period=unemp_obs.period if unemp_obs else None,
                    unemployment_source=unemp_series.provider_id if unemp_series else None,
                    policy_interest_rate=rate_obs.value if rate_obs else None,
                    policy_rate_period=rate_obs.period if rate_obs else None,
                    policy_rate_source=rate_series.provider_id if rate_series else None,
                    latest_observation_date="2024-10-31",
                    source_freshness="PUBLISHED_CURRENT",
                )
            )
        return summaries

    # -------------------------------------------------------------------------
    # Internal Seeding Methods
    # -------------------------------------------------------------------------

    def _seed_geographies(self) -> None:
        geos = [
            EconomicGeography(
                geography_id="geo-us",
                name="United States",
                iso_code="USA",
                scope_kind=GeographicScopeKind.COUNTRY,
                currency_code="USD",
                flag_emoji_code="US",
                is_core=True,
                notes="Largest global economy by nominal GDP; Federal Reserve monetary jurisdiction.",
            ),
            EconomicGeography(
                geography_id="geo-ea",
                name="Euro Area",
                iso_code="EA19",
                scope_kind=GeographicScopeKind.ECONOMIC_AREA,
                currency_code="EUR",
                flag_emoji_code="EU",
                is_core=True,
                notes="Monetary union of 20 EU member states under the European Central Bank.",
            ),
            EconomicGeography(
                geography_id="geo-cn",
                name="China",
                iso_code="CHN",
                scope_kind=GeographicScopeKind.COUNTRY,
                currency_code="CNY",
                flag_emoji_code="CN",
                is_core=True,
                notes="Second-largest global economy; statistical reporting via National Bureau of Statistics (NBS).",
            ),
            EconomicGeography(
                geography_id="geo-in",
                name="India",
                iso_code="IND",
                scope_kind=GeographicScopeKind.COUNTRY,
                currency_code="INR",
                flag_emoji_code="IN",
                is_core=True,
                notes="Fastest growing major G20 economy; reporting via MoSPI and Reserve Bank of India.",
            ),
            EconomicGeography(
                geography_id="geo-jp",
                name="Japan",
                iso_code="JPN",
                scope_kind=GeographicScopeKind.COUNTRY,
                currency_code="JPY",
                flag_emoji_code="JP",
                is_core=True,
                notes="Third-largest national economy; reporting via Statistics Bureau and Bank of Japan.",
            ),
            EconomicGeography(
                geography_id="geo-gb",
                name="United Kingdom",
                iso_code="GBR",
                scope_kind=GeographicScopeKind.COUNTRY,
                currency_code="GBP",
                flag_emoji_code="GB",
                is_core=True,
                notes="Major advanced economy; reporting via Office for National Statistics (ONS) and Bank of England.",
            ),
        ]
        for g in geos:
            self._geographies[g.geography_id] = g

    def _seed_indicators(self) -> None:
        inds = [
            EconomicIndicator(
                indicator_id="ind-gdp-growth-yoy",
                code="GDP_GROWTH_YOY",
                name="Real GDP Growth (Year-over-Year)",
                description="Annual percentage growth of real gross domestic product measured at constant prices or chained volume.",
                category=IndicatorCategory.NATIONAL_ACCOUNTS,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                methodology_summary="SNA 2008 / ESA 2010 chained volume measure compared with corresponding quarter of previous year.",
                is_headline=True,
            ),
            EconomicIndicator(
                indicator_id="ind-gdp-real-level",
                code="GDP_REAL_LEVEL",
                name="Real GDP Level",
                description="Gross domestic product measured in constant local currency or chained volume index.",
                category=IndicatorCategory.NATIONAL_ACCOUNTS,
                default_unit=StatisticalUnit.LOCAL_CURRENCY_BILLIONS,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                methodology_summary="Chained volume level expressed in national currency billions at base-year price levels.",
                is_headline=False,
            ),
            EconomicIndicator(
                indicator_id="ind-cpi-yoy",
                code="CPI_INFLATION_YOY",
                name="Consumer Price Inflation (Headline YoY)",
                description="Annual percentage change in the headline Consumer Price Index for all urban consumers or harmonized basket.",
                category=IndicatorCategory.INFLATION,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                methodology_summary="Laspeyres / Fisher price index tracking representative consumer goods and services basket.",
                is_headline=True,
            ),
            EconomicIndicator(
                indicator_id="ind-cpi-index",
                code="CPI_INDEX_LEVEL",
                name="Consumer Price Index Level",
                description="Index points level representing consumer price basket changes relative to a designated base period (100).",
                category=IndicatorCategory.INFLATION,
                default_unit=StatisticalUnit.INDEX_POINTS,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                methodology_summary="Official statistical index series. Must not be confused with percentage inflation rate.",
                is_headline=False,
            ),
            EconomicIndicator(
                indicator_id="ind-unemp-rate",
                code="UNEMPLOYMENT_RATE",
                name="Harmonized Unemployment Rate",
                description="Unemployed persons as a percentage of the total civilian labor force seeking employment.",
                category=IndicatorCategory.LABOR_MARKET,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                methodology_summary="ILO standard labor force survey definition: persons without work actively seeking employment.",
                is_headline=True,
            ),
            EconomicIndicator(
                indicator_id="ind-policy-rate",
                code="POLICY_INTEREST_RATE",
                name="Central Bank Policy Rate",
                description="Primary monetary policy target or operational benchmark set by the sovereign central bank.",
                category=IndicatorCategory.INTEREST_RATES,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                methodology_summary="Official operational target (Fed Funds, ECB Deposit Facility/MRO, RBI Repo, BOJ Policy Rate, BOE Bank Rate).",
                is_headline=True,
            ),
            EconomicIndicator(
                indicator_id="ind-ind-prod-yoy",
                code="IND_PROD_YOY",
                name="Industrial Production Growth (YoY)",
                description="Year-over-year percentage change in real industrial output across manufacturing, mining, and utilities.",
                category=IndicatorCategory.INDUSTRIAL_ACTIVITY,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                methodology_summary="Volume output index measuring physical manufacturing, mining, and electric utility output.",
                is_headline=False,
            ),
            EconomicIndicator(
                indicator_id="ind-govt-debt-gdp",
                code="GOVT_DEBT_GDP",
                name="General Government Debt (% of GDP)",
                description="Total gross financial liabilities of general government expressed as a percentage of annual nominal GDP.",
                category=IndicatorCategory.FISCAL,
                default_unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                methodology_summary="Maastricht / IMF GFS definition of consolidated general government gross debt over nominal GDP.",
                is_headline=False,
            ),
        ]
        for ind in inds:
            self._indicators[ind.indicator_id] = ind

    def _seed_series(self) -> None:
        series_defs = [
            # United States
            EconomicSeries(
                series_id="ser-us-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-us",
                geography_name="United States",
                provider_id="BEA (U.S. Bureau of Economic Analysis)",
                source_series_code="A191RL1Q225SBEA",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Real gross domestic product, percent change from quarter one year ago, chained 2017 dollars.",
                source_url="https://www.bea.gov/data/gdp/gross-domestic-product",
            ),
            EconomicSeries(
                series_id="ser-us-cpi-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-us",
                geography_name="United States",
                provider_id="BLS (U.S. Bureau of Labor Statistics)",
                source_series_code="CPIAUCSL_PC1",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Consumer Price Index for All Urban Consumers: All Items, 12-Month Percent Change.",
                source_url="https://www.bls.gov/cpi/",
            ),
            EconomicSeries(
                series_id="ser-us-cpi-index",
                indicator_id="ind-cpi-index",
                indicator_code="CPI_INDEX_LEVEL",
                indicator_name="Consumer Price Index Level",
                geography_id="geo-us",
                geography_name="United States",
                provider_id="BLS (U.S. Bureau of Labor Statistics)",
                source_series_code="CPIAUCSL",
                unit=StatisticalUnit.INDEX_POINTS,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Consumer Price Index for All Urban Consumers: All Items in U.S. City Average (1982-1984=100).",
                source_url="https://www.bls.gov/cpi/",
            ),
            EconomicSeries(
                series_id="ser-us-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-us",
                geography_name="United States",
                provider_id="BLS (U.S. Bureau of Labor Statistics)",
                source_series_code="UNRATE",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Civilian Unemployment Rate, 16 years and over, Seasonally Adjusted.",
                source_url="https://www.bls.gov/cps/",
            ),
            EconomicSeries(
                series_id="ser-us-fedfunds",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-us",
                geography_name="United States",
                provider_id="Federal Reserve Board",
                source_series_code="DFEDTARU",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="Federal Funds Target Upper Bound, percentage per annum.",
                source_url="https://www.federalreserve.gov/monetarypolicy/openmarket.htm",
            ),

            # Euro Area
            EconomicSeries(
                series_id="ser-ea-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-ea",
                geography_name="Euro Area",
                provider_id="Eurostat",
                source_series_code="namq_10_gdp_ea",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CHAIN_VOLUME,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Euro Area 20 GDP growth, percentage change over previous year, chain-linked volumes.",
                source_url="https://ec.europa.eu/eurostat/web/national-accounts",
            ),
            EconomicSeries(
                series_id="ser-ea-hicp-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-ea",
                geography_name="Euro Area",
                provider_id="Eurostat",
                source_series_code="prc_hicp_manr_ea",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Harmonised Index of Consumer Prices (HICP) Headline Annual Inflation Rate, Euro Area.",
                source_url="https://ec.europa.eu/eurostat/web/hicp",
            ),
            EconomicSeries(
                series_id="ser-ea-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-ea",
                geography_name="Euro Area",
                provider_id="Eurostat",
                source_series_code="une_rt_m_ea",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Euro Area Standardised Unemployment Rate, percentage of active population.",
                source_url="https://ec.europa.eu/eurostat/web/lfs",
            ),
            EconomicSeries(
                series_id="ser-ea-ecb-rate",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-ea",
                geography_name="Euro Area",
                provider_id="European Central Bank (ECB)",
                source_series_code="FM.D.U2.EUR.4F.KR.DFR.LEV",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="ECB Deposit Facility Rate, operational monetary policy anchor.",
                source_url="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/",
            ),

            # China
            EconomicSeries(
                series_id="ser-cn-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-cn",
                geography_name="China",
                provider_id="NBS (National Bureau of Statistics of China)",
                source_series_code="CN_NBS_GDP_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Gross Domestic Product YoY growth rate at comparable constant prices.",
                source_url="http://www.stats.gov.cn/english/",
            ),
            EconomicSeries(
                series_id="ser-cn-cpi-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-cn",
                geography_name="China",
                provider_id="NBS (National Bureau of Statistics of China)",
                source_series_code="CN_NBS_CPI_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="National Consumer Price Index year-over-year percentage change.",
                source_url="http://www.stats.gov.cn/english/",
            ),
            EconomicSeries(
                series_id="ser-cn-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-cn",
                geography_name="China",
                provider_id="NBS (National Bureau of Statistics of China)",
                source_series_code="CN_NBS_URBAN_UNEMP",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Nationwide surveyed urban unemployment rate in China.",
                source_url="http://www.stats.gov.cn/english/",
            ),
            EconomicSeries(
                series_id="ser-cn-lpr-1y",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-cn",
                geography_name="China",
                provider_id="People's Bank of China (PBOC)",
                source_series_code="CN_PBOC_LPR_1Y",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="PBOC 1-Year Loan Prime Rate (LPR) benchmark.",
                source_url="http://www.pbc.gov.cn/en/",
            ),

            # India
            EconomicSeries(
                series_id="ser-in-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-in",
                geography_name="India",
                provider_id="MoSPI (Ministry of Statistics and Programme Implementation)",
                source_series_code="IN_MOSPI_GDP_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CONSTANT_PRICES,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Real Gross Domestic Product at constant 2011-12 prices YoY growth rate.",
                source_url="https://mospi.gov.in/",
            ),
            EconomicSeries(
                series_id="ser-in-cpi-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-in",
                geography_name="India",
                provider_id="MoSPI (Ministry of Statistics and Programme Implementation)",
                source_series_code="IN_MOSPI_CPI_COMBINED_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Consumer Price Index (Combined Rural + Urban) Headline YoY inflation (Base 2012=100).",
                source_url="https://mospi.gov.in/",
            ),
            EconomicSeries(
                series_id="ser-in-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-in",
                geography_name="India",
                provider_id="MoSPI (PLFS) / CMIE Benchmark",
                source_series_code="IN_PLFS_UNEMP_RATE",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Periodic Labour Force Survey / Monthly urban & rural unemployment rate.",
                source_url="https://mospi.gov.in/",
            ),
            EconomicSeries(
                series_id="ser-in-rbi-repo",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-in",
                geography_name="India",
                provider_id="Reserve Bank of India (RBI)",
                source_series_code="IN_RBI_POLICY_REPO",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="RBI Policy Repo Rate under Liquidity Adjustment Facility (LAF).",
                source_url="https://www.rbi.org.in/",
            ),

            # Japan
            EconomicSeries(
                series_id="ser-jp-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-jp",
                geography_name="Japan",
                provider_id="Cabinet Office of Japan (ESRI)",
                source_series_code="JP_ESRI_GDP_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CHAIN_VOLUME,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Quarterly Estimates of GDP, Real Chained 2015 Calendar Year Prices YoY.",
                source_url="https://www.esri.cao.go.jp/en/sna/menu.html",
            ),
            EconomicSeries(
                series_id="ser-jp-cpi-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-jp",
                geography_name="Japan",
                provider_id="Statistics Bureau of Japan",
                source_series_code="JP_STAT_CPI_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Consumer Price Index for Japan: All Items, Year-on-Year percentage change.",
                source_url="https://www.stat.go.jp/english/data/cpi/",
            ),
            EconomicSeries(
                series_id="ser-jp-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-jp",
                geography_name="Japan",
                provider_id="Statistics Bureau of Japan",
                source_series_code="JP_STAT_UNEMP",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Labour Force Survey Unemployment Rate (Seasonally Adjusted).",
                source_url="https://www.stat.go.jp/english/data/roudou/",
            ),
            EconomicSeries(
                series_id="ser-jp-boj-rate",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-jp",
                geography_name="Japan",
                provider_id="Bank of Japan (BOJ)",
                source_series_code="JP_BOJ_UNCOLLAT_CALL",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="BOJ Policy Rate / Uncollateralized Overnight Call Rate Target.",
                source_url="https://www.boj.or.jp/en/statistics/",
            ),

            # United Kingdom
            EconomicSeries(
                series_id="ser-gb-gdp-growth",
                indicator_id="ind-gdp-growth-yoy",
                indicator_code="GDP_GROWTH_YOY",
                indicator_name="Real GDP Growth (Year-over-Year)",
                geography_id="geo-gb",
                geography_name="United Kingdom",
                provider_id="ONS (Office for National Statistics)",
                source_series_code="UK_ONS_ABMI_YOY",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.QUARTERLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.CHAIN_VOLUME,
                first_period="2022-Q1",
                latest_period="2024-Q3",
                observation_count=11,
                source_definition="Gross Domestic Product at market prices: Chained volume measure YoY.",
                source_url="https://www.ons.gov.uk/economy/grossdomesticproductgdp",
            ),
            EconomicSeries(
                series_id="ser-gb-cpi-yoy",
                indicator_id="ind-cpi-yoy",
                indicator_code="CPI_INFLATION_YOY",
                indicator_name="Consumer Price Inflation (Headline YoY)",
                geography_id="geo-gb",
                geography_name="United Kingdom",
                provider_id="ONS (Office for National Statistics)",
                source_series_code="UK_ONS_D7G7",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.CURRENT_PRICES,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="CPI All Items Index Annual Rate (00: All Items 2015=100).",
                source_url="https://www.ons.gov.uk/economy/inflationandpriceindices",
            ),
            EconomicSeries(
                series_id="ser-gb-unemp",
                indicator_id="ind-unemp-rate",
                indicator_code="UNEMPLOYMENT_RATE",
                indicator_name="Harmonized Unemployment Rate",
                geography_id="geo-gb",
                geography_name="United Kingdom",
                provider_id="ONS (Office for National Statistics)",
                source_series_code="UK_ONS_MGSX",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.MONTHLY,
                seasonal_adjustment=SeasonalAdjustmentKind.SEASONALLY_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-09",
                observation_count=21,
                source_definition="Unemployment rate (aged 16 and over, seasonally adjusted, 3-month rolling).",
                source_url="https://www.ons.gov.uk/employmentandlabourmarket",
            ),
            EconomicSeries(
                series_id="ser-gb-boe-rate",
                indicator_id="ind-policy-rate",
                indicator_code="POLICY_INTEREST_RATE",
                indicator_name="Central Bank Policy Rate",
                geography_id="geo-gb",
                geography_name="United Kingdom",
                provider_id="Bank of England (BOE)",
                source_series_code="UK_BOE_BANK_RATE",
                unit=StatisticalUnit.PERCENT,
                frequency=ReportingFrequency.DAILY,
                seasonal_adjustment=SeasonalAdjustmentKind.NOT_ADJUSTED,
                price_basis=PriceBasisKind.NOT_APPLICABLE,
                first_period="2023-01",
                latest_period="2024-10",
                observation_count=22,
                source_definition="Bank of England Official Bank Rate.",
                source_url="https://www.bankofengland.co.uk/monetary-policy/the-interest-rate-bank-rate",
            ),
        ]
        for s in series_defs:
            self._series[s.series_id] = s

    def _seed_observations(self) -> None:
        """Seed authentic historical observation series for all registered series."""
        # 1. US Real GDP Growth YoY (Quarterly)
        us_gdp_data = [
            ("2022-Q1", date(2022, 1, 1), date(2022, 3, 31), Decimal("3.6"), ObservationStatus.FINAL, datetime(2022, 4, 28, 12, 30, tzinfo=timezone.utc)),
            ("2022-Q2", date(2022, 4, 1), date(2022, 6, 30), Decimal("1.9"), ObservationStatus.FINAL, datetime(2022, 7, 28, 12, 30, tzinfo=timezone.utc)),
            ("2022-Q3", date(2022, 7, 1), date(2022, 9, 30), Decimal("1.7"), ObservationStatus.FINAL, datetime(2022, 10, 27, 12, 30, tzinfo=timezone.utc)),
            ("2022-Q4", date(2022, 10, 1), date(2022, 12, 31), Decimal("0.7"), ObservationStatus.FINAL, datetime(2023, 1, 26, 13, 30, tzinfo=timezone.utc)),
            ("2023-Q1", date(2023, 1, 1), date(2023, 3, 31), Decimal("1.7"), ObservationStatus.FINAL, datetime(2023, 4, 27, 12, 30, tzinfo=timezone.utc)),
            ("2023-Q2", date(2023, 4, 1), date(2023, 6, 30), Decimal("2.4"), ObservationStatus.FINAL, datetime(2023, 7, 27, 12, 30, tzinfo=timezone.utc)),
            ("2023-Q3", date(2023, 7, 1), date(2023, 9, 30), Decimal("2.9"), ObservationStatus.FINAL, datetime(2023, 10, 26, 12, 30, tzinfo=timezone.utc)),
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("3.1"), ObservationStatus.FINAL, datetime(2024, 1, 25, 13, 30, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("2.9"), ObservationStatus.FINAL, datetime(2024, 4, 25, 12, 30, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("3.0"), ObservationStatus.REVISED, datetime(2024, 8, 29, 12, 30, tzinfo=timezone.utc)),
            ("2024-Q3", date(2024, 7, 1), date(2024, 9, 30), Decimal("2.8"), ObservationStatus.PRELIMINARY, datetime(2024, 10, 30, 12, 30, tzinfo=timezone.utc)),
        ]
        self._add_obs_list("ser-us-gdp-growth", StatisticalUnit.PERCENT, us_gdp_data)

        # 2. US CPI Headline YoY (Monthly 2023-01 to 2024-09)
        us_cpi_rates = [
            ("2023-01", date(2023, 1, 1), date(2023, 1, 31), Decimal("6.4")),
            ("2023-02", date(2023, 2, 1), date(2023, 2, 28), Decimal("6.0")),
            ("2023-03", date(2023, 3, 1), date(2023, 3, 31), Decimal("5.0")),
            ("2023-04", date(2023, 4, 1), date(2023, 4, 30), Decimal("4.9")),
            ("2023-05", date(2023, 5, 1), date(2023, 5, 31), Decimal("4.0")),
            ("2023-06", date(2023, 6, 1), date(2023, 6, 30), Decimal("3.0")),
            ("2023-07", date(2023, 7, 1), date(2023, 7, 31), Decimal("3.2")),
            ("2023-08", date(2023, 8, 1), date(2023, 8, 31), Decimal("3.7")),
            ("2023-09", date(2023, 9, 1), date(2023, 9, 30), Decimal("3.7")),
            ("2023-10", date(2023, 10, 1), date(2023, 10, 31), Decimal("3.2")),
            ("2023-11", date(2023, 11, 1), date(2023, 11, 30), Decimal("3.1")),
            ("2023-12", date(2023, 12, 1), date(2023, 12, 31), Decimal("3.4")),
            ("2024-01", date(2024, 1, 1), date(2024, 1, 31), Decimal("3.1")),
            ("2024-02", date(2024, 2, 1), date(2024, 2, 29), Decimal("3.2")),
            ("2024-03", date(2024, 3, 1), date(2024, 3, 31), Decimal("3.5")),
            ("2024-04", date(2024, 4, 1), date(2024, 4, 30), Decimal("3.4")),
            ("2024-05", date(2024, 5, 1), date(2024, 5, 31), Decimal("3.3")),
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("3.0")),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("2.9")),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("2.5")),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("2.4")),
        ]
        self._add_obs_list("ser-us-cpi-yoy", StatisticalUnit.PERCENT, [
            (p, s, e, v, ObservationStatus.FINAL, datetime(e.year, e.month, 12, 12, 30, tzinfo=timezone.utc))
            for p, s, e, v in us_cpi_rates
        ])

        # 3. US CPI Index Levels (Base 1982-1984=100)
        cpi_indices = [
            ("2023-01", date(2023, 1, 1), date(2023, 1, 31), Decimal("300.536")),
            ("2023-02", date(2023, 2, 1), date(2023, 2, 28), Decimal("301.648")),
            ("2023-03", date(2023, 3, 1), date(2023, 3, 31), Decimal("301.808")),
            ("2023-04", date(2023, 4, 1), date(2023, 4, 30), Decimal("302.918")),
            ("2023-05", date(2023, 5, 1), date(2023, 5, 31), Decimal("303.294")),
            ("2023-06", date(2023, 6, 1), date(2023, 6, 30), Decimal("303.841")),
            ("2023-07", date(2023, 7, 1), date(2023, 7, 31), Decimal("304.348")),
            ("2023-08", date(2023, 8, 1), date(2023, 8, 31), Decimal("306.269")),
            ("2023-09", date(2023, 9, 1), date(2023, 9, 30), Decimal("307.481")),
            ("2023-10", date(2023, 10, 1), date(2023, 10, 31), Decimal("307.531")),
            ("2023-11", date(2023, 11, 1), date(2023, 11, 30), Decimal("308.024")),
            ("2023-12", date(2023, 12, 1), date(2023, 12, 31), Decimal("308.742")),
            ("2024-01", date(2024, 1, 1), date(2024, 1, 31), Decimal("309.680")),
            ("2024-02", date(2024, 2, 1), date(2024, 2, 29), Decimal("311.054")),
            ("2024-03", date(2024, 3, 1), date(2024, 3, 31), Decimal("312.230")),
            ("2024-04", date(2024, 4, 1), date(2024, 4, 30), Decimal("313.207")),
            ("2024-05", date(2024, 5, 1), date(2024, 5, 31), Decimal("313.225")),
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("313.049")),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("313.534")),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("314.120")),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("314.796")),
        ]
        self._add_obs_list("ser-us-cpi-index", StatisticalUnit.INDEX_POINTS, [
            (p, s, e, v, ObservationStatus.FINAL, datetime(e.year, e.month, 12, 12, 30, tzinfo=timezone.utc))
            for p, s, e, v in cpi_indices
        ])

        # 4. US Unemployment Rate (Monthly 2023-01 to 2024-09)
        unemp_data = [
            ("2023-01", date(2023, 1, 1), date(2023, 1, 31), Decimal("3.4")),
            ("2023-02", date(2023, 2, 1), date(2023, 2, 28), Decimal("3.6")),
            ("2023-03", date(2023, 3, 1), date(2023, 3, 31), Decimal("3.5")),
            ("2023-04", date(2023, 4, 1), date(2023, 4, 30), Decimal("3.4")),
            ("2023-05", date(2023, 5, 1), date(2023, 5, 31), Decimal("3.7")),
            ("2023-06", date(2023, 6, 1), date(2023, 6, 30), Decimal("3.6")),
            ("2023-07", date(2023, 7, 1), date(2023, 7, 31), Decimal("3.5")),
            ("2023-08", date(2023, 8, 1), date(2023, 8, 31), Decimal("3.8")),
            ("2023-09", date(2023, 9, 1), date(2023, 9, 30), Decimal("3.8")),
            ("2023-10", date(2023, 10, 1), date(2023, 10, 31), Decimal("3.8")),
            ("2023-11", date(2023, 11, 1), date(2023, 11, 30), Decimal("3.7")),
            ("2023-12", date(2023, 12, 1), date(2023, 12, 31), Decimal("3.7")),
            ("2024-01", date(2024, 1, 1), date(2024, 1, 31), Decimal("3.7")),
            ("2024-02", date(2024, 2, 1), date(2024, 2, 29), Decimal("3.9")),
            ("2024-03", date(2024, 3, 1), date(2024, 3, 31), Decimal("3.8")),
            ("2024-04", date(2024, 4, 1), date(2024, 4, 30), Decimal("3.9")),
            ("2024-05", date(2024, 5, 1), date(2024, 5, 31), Decimal("4.0")),
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("4.1")),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("4.3")),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("4.2")),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("4.1")),
        ]
        self._add_obs_list("ser-us-unemp", StatisticalUnit.PERCENT, [
            (p, s, e, v, ObservationStatus.FINAL, datetime(e.year, e.month, 5, 12, 30, tzinfo=timezone.utc))
            for p, s, e, v in unemp_data
        ])

        # 5. US Fed Funds Target Upper Bound (2023-2024)
        fed_rates = [
            ("2023-01", date(2023, 1, 1), date(2023, 1, 31), Decimal("4.50")),
            ("2023-02", date(2023, 2, 1), date(2023, 2, 28), Decimal("4.75")),
            ("2023-03", date(2023, 3, 1), date(2023, 3, 31), Decimal("5.00")),
            ("2023-05", date(2023, 5, 1), date(2023, 5, 31), Decimal("5.25")),
            ("2023-07", date(2023, 7, 1), date(2023, 7, 31), Decimal("5.50")),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("5.00")),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("5.00")),
        ]
        self._add_obs_list("ser-us-fedfunds", StatisticalUnit.PERCENT, [
            (p, s, e, v, ObservationStatus.FINAL, datetime(s.year, s.month, s.day, 18, 0, tzinfo=timezone.utc))
            for p, s, e, v in fed_rates
        ])

        # 6. Euro Area Series
        ea_gdp = [
            ("2023-Q1", date(2023, 1, 1), date(2023, 3, 31), Decimal("1.2"), ObservationStatus.FINAL, datetime(2023, 4, 28, 9, 0, tzinfo=timezone.utc)),
            ("2023-Q2", date(2023, 4, 1), date(2023, 6, 30), Decimal("0.5"), ObservationStatus.FINAL, datetime(2023, 7, 28, 9, 0, tzinfo=timezone.utc)),
            ("2023-Q3", date(2023, 7, 1), date(2023, 9, 30), Decimal("0.1"), ObservationStatus.FINAL, datetime(2023, 10, 31, 10, 0, tzinfo=timezone.utc)),
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("0.2"), ObservationStatus.FINAL, datetime(2024, 1, 30, 10, 0, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("0.5"), ObservationStatus.FINAL, datetime(2024, 4, 30, 9, 0, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("0.6"), ObservationStatus.FINAL, datetime(2024, 7, 30, 9, 0, tzinfo=timezone.utc)),
            ("2024-Q3", date(2024, 7, 1), date(2024, 9, 30), Decimal("0.9"), ObservationStatus.PRELIMINARY, datetime(2024, 10, 30, 10, 0, tzinfo=timezone.utc)),
        ]
        self._add_obs_list("ser-ea-gdp-growth", StatisticalUnit.PERCENT, ea_gdp)

        ea_hicp = [
            ("2024-05", date(2024, 5, 1), date(2024, 5, 31), Decimal("2.6"), ObservationStatus.FINAL, datetime(2024, 6, 18, 9, 0, tzinfo=timezone.utc)),
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("2.5"), ObservationStatus.FINAL, datetime(2024, 7, 17, 9, 0, tzinfo=timezone.utc)),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("2.6"), ObservationStatus.FINAL, datetime(2024, 8, 20, 9, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("2.2"), ObservationStatus.FINAL, datetime(2024, 9, 18, 9, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("1.7"), ObservationStatus.FINAL, datetime(2024, 10, 17, 9, 0, tzinfo=timezone.utc)),
        ]
        self._add_obs_list("ser-ea-hicp-yoy", StatisticalUnit.PERCENT, ea_hicp)

        self._add_obs_list("ser-ea-unemp", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("6.4"), ObservationStatus.FINAL, datetime(2024, 9, 2, 9, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("6.4"), ObservationStatus.FINAL, datetime(2024, 10, 2, 9, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("6.3"), ObservationStatus.FINAL, datetime(2024, 10, 31, 10, 0, tzinfo=timezone.utc)),
        ])

        self._add_obs_list("ser-ea-ecb-rate", StatisticalUnit.PERCENT, [
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("3.75"), ObservationStatus.FINAL, datetime(2024, 6, 12, 12, 15, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("3.50"), ObservationStatus.FINAL, datetime(2024, 9, 18, 12, 15, tzinfo=timezone.utc)),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("3.25"), ObservationStatus.FINAL, datetime(2024, 10, 23, 12, 15, tzinfo=timezone.utc)),
        ])

        # 7. China Series
        self._add_obs_list("ser-cn-gdp-growth", StatisticalUnit.PERCENT, [
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("5.2"), ObservationStatus.FINAL, datetime(2024, 1, 17, 2, 0, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("5.3"), ObservationStatus.FINAL, datetime(2024, 4, 16, 2, 0, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("4.7"), ObservationStatus.FINAL, datetime(2024, 7, 15, 2, 0, tzinfo=timezone.utc)),
            ("2024-Q3", date(2024, 7, 1), date(2024, 9, 30), Decimal("4.6"), ObservationStatus.FINAL, datetime(2024, 10, 18, 2, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-cn-cpi-yoy", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("0.5"), ObservationStatus.FINAL, datetime(2024, 8, 9, 1, 30, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("0.6"), ObservationStatus.FINAL, datetime(2024, 9, 9, 1, 30, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("0.4"), ObservationStatus.FINAL, datetime(2024, 10, 13, 1, 30, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-cn-unemp", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("5.2"), ObservationStatus.FINAL, datetime(2024, 8, 15, 2, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("5.3"), ObservationStatus.FINAL, datetime(2024, 9, 14, 2, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("5.1"), ObservationStatus.FINAL, datetime(2024, 10, 18, 2, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-cn-lpr-1y", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("3.35"), ObservationStatus.FINAL, datetime(2024, 7, 22, 1, 15, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("3.35"), ObservationStatus.FINAL, datetime(2024, 8, 20, 1, 15, tzinfo=timezone.utc)),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("3.10"), ObservationStatus.FINAL, datetime(2024, 10, 21, 1, 15, tzinfo=timezone.utc)),
        ])

        # 8. India Series
        self._add_obs_list("ser-in-gdp-growth", StatisticalUnit.PERCENT, [
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("8.4"), ObservationStatus.FINAL, datetime(2024, 2, 29, 12, 0, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("7.8"), ObservationStatus.FINAL, datetime(2024, 5, 31, 12, 0, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("6.7"), ObservationStatus.FINAL, datetime(2024, 8, 30, 12, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-in-cpi-yoy", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("3.60"), ObservationStatus.FINAL, datetime(2024, 8, 12, 12, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("3.65"), ObservationStatus.FINAL, datetime(2024, 9, 12, 12, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("5.49"), ObservationStatus.FINAL, datetime(2024, 10, 14, 12, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-in-unemp", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("7.9"), ObservationStatus.FINAL, datetime(2024, 8, 1, 12, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("8.5"), ObservationStatus.FINAL, datetime(2024, 9, 1, 12, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("7.8"), ObservationStatus.FINAL, datetime(2024, 10, 1, 12, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-in-rbi-repo", StatisticalUnit.PERCENT, [
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("6.50"), ObservationStatus.FINAL, datetime(2024, 6, 7, 4, 30, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("6.50"), ObservationStatus.FINAL, datetime(2024, 8, 8, 4, 30, tzinfo=timezone.utc)),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("6.50"), ObservationStatus.FINAL, datetime(2024, 10, 9, 4, 30, tzinfo=timezone.utc)),
        ])

        # 9. Japan Series
        self._add_obs_list("ser-jp-gdp-growth", StatisticalUnit.PERCENT, [
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("0.1"), ObservationStatus.FINAL, datetime(2024, 2, 15, 0, 50, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("-0.9"), ObservationStatus.FINAL, datetime(2024, 5, 16, 0, 50, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("-1.0"), ObservationStatus.FINAL, datetime(2024, 8, 15, 0, 50, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-jp-cpi-yoy", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("2.8"), ObservationStatus.FINAL, datetime(2024, 8, 23, 0, 30, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("3.0"), ObservationStatus.FINAL, datetime(2024, 9, 20, 0, 30, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("2.5"), ObservationStatus.FINAL, datetime(2024, 10, 18, 0, 30, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-jp-unemp", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("2.7"), ObservationStatus.FINAL, datetime(2024, 8, 30, 0, 30, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("2.5"), ObservationStatus.FINAL, datetime(2024, 10, 1, 0, 30, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("2.4"), ObservationStatus.FINAL, datetime(2024, 10, 29, 0, 30, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-jp-boj-rate", StatisticalUnit.PERCENT, [
            ("2024-03", date(2024, 3, 1), date(2024, 3, 31), Decimal("0.10"), ObservationStatus.FINAL, datetime(2024, 3, 19, 3, 30, tzinfo=timezone.utc)),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("0.25"), ObservationStatus.FINAL, datetime(2024, 7, 31, 3, 30, tzinfo=timezone.utc)),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("0.25"), ObservationStatus.FINAL, datetime(2024, 10, 31, 3, 30, tzinfo=timezone.utc)),
        ])

        # 10. United Kingdom Series
        self._add_obs_list("ser-gb-gdp-growth", StatisticalUnit.PERCENT, [
            ("2023-Q4", date(2023, 10, 1), date(2023, 12, 31), Decimal("-0.2"), ObservationStatus.FINAL, datetime(2024, 2, 15, 7, 0, tzinfo=timezone.utc)),
            ("2024-Q1", date(2024, 1, 1), date(2024, 3, 31), Decimal("0.3"), ObservationStatus.FINAL, datetime(2024, 5, 10, 6, 0, tzinfo=timezone.utc)),
            ("2024-Q2", date(2024, 4, 1), date(2024, 6, 30), Decimal("0.7"), ObservationStatus.FINAL, datetime(2024, 8, 15, 6, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-gb-cpi-yoy", StatisticalUnit.PERCENT, [
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("2.2"), ObservationStatus.FINAL, datetime(2024, 8, 14, 6, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("2.2"), ObservationStatus.FINAL, datetime(2024, 9, 18, 6, 0, tzinfo=timezone.utc)),
            ("2024-09", date(2024, 9, 1), date(2024, 9, 30), Decimal("1.7"), ObservationStatus.FINAL, datetime(2024, 10, 16, 6, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-gb-unemp", StatisticalUnit.PERCENT, [
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("4.2"), ObservationStatus.FINAL, datetime(2024, 8, 13, 6, 0, tzinfo=timezone.utc)),
            ("2024-07", date(2024, 7, 1), date(2024, 7, 31), Decimal("4.1"), ObservationStatus.FINAL, datetime(2024, 9, 10, 6, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("4.0"), ObservationStatus.FINAL, datetime(2024, 10, 15, 6, 0, tzinfo=timezone.utc)),
        ])
        self._add_obs_list("ser-gb-boe-rate", StatisticalUnit.PERCENT, [
            ("2024-06", date(2024, 6, 1), date(2024, 6, 30), Decimal("5.25"), ObservationStatus.FINAL, datetime(2024, 6, 20, 11, 0, tzinfo=timezone.utc)),
            ("2024-08", date(2024, 8, 1), date(2024, 8, 31), Decimal("5.00"), ObservationStatus.FINAL, datetime(2024, 8, 1, 11, 0, tzinfo=timezone.utc)),
            ("2024-10", date(2024, 10, 1), date(2024, 10, 31), Decimal("5.00"), ObservationStatus.FINAL, datetime(2024, 9, 19, 11, 0, tzinfo=timezone.utc)),
        ])

    def _add_obs_list(self, series_id: str, unit: StatisticalUnit, records: list) -> None:
        obs_records: List[EconomicObservationRecord] = []
        for idx, item in enumerate(records):
            period = item[0]
            start_d = item[1]
            end_d = item[2]
            val = item[3]
            stat = item[4]
            pub_dt = item[5]
            obs_records.append(
                EconomicObservationRecord(
                    observation_id=f"obs-{series_id}-{period}",
                    series_id=series_id,
                    period=period,
                    period_start=start_d,
                    period_end=end_d,
                    reference_date=end_d,
                    value=val,
                    unit=unit,
                    status=stat,
                    published_at=pub_dt,
                    ingested_at=datetime(2024, 10, 31, 12, 0, tzinfo=timezone.utc),
                    revision_number=idx,
                    notes=f"Official {stat.value} statistic",
                )
            )
        self._observations[series_id] = obs_records

    def _seed_vintages(self) -> None:
        """Seed point-in-time historical revisions for key releases."""
        # US Real GDP 2024-Q2 revisions: Advance (2.8%) -> Second (3.0%) -> Third (3.0%)
        self._vintages["ser-us-gdp-growth"] = [
            EconomicVintageRecord(
                vintage_id="vin-us-gdp-2024q2-adv",
                series_id="ser-us-gdp-growth",
                period="2024-Q2",
                vintage_date=date(2024, 7, 25),
                value=Decimal("2.8"),
                status=ObservationStatus.PRELIMINARY,
                published_at=datetime(2024, 7, 25, 12, 30, tzinfo=timezone.utc),
                notes="Advance estimate release by BEA.",
            ),
            EconomicVintageRecord(
                vintage_id="vin-us-gdp-2024q2-sec",
                series_id="ser-us-gdp-growth",
                period="2024-Q2",
                vintage_date=date(2024, 8, 29),
                value=Decimal("3.0"),
                status=ObservationStatus.REVISED,
                published_at=datetime(2024, 8, 29, 12, 30, tzinfo=timezone.utc),
                notes="Second estimate reflecting upward revisions to personal consumption expenditures.",
            ),
            EconomicVintageRecord(
                vintage_id="vin-us-gdp-2024q2-tri",
                series_id="ser-us-gdp-growth",
                period="2024-Q2",
                vintage_date=date(2024, 9, 26),
                value=Decimal("3.0"),
                status=ObservationStatus.FINAL,
                published_at=datetime(2024, 9, 26, 12, 30, tzinfo=timezone.utc),
                notes="Third (final) estimate for 2024-Q2.",
            ),
        ]
