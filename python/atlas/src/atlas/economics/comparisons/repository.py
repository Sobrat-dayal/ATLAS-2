"""Repository for Macroeconomic Comparisons & Benchmarking (Stage 93).

Maintains authoritative cross-country datasets for sovereign economies,
predefined geographic cohorts, indicator compatibility definitions, and historical series.
"""

from typing import Dict, List, Optional, Tuple

from .enums import (
    ComparisonMetricKind,
    GeographicCohortKind,
)
from .errors import (
    MacroComparisonIndicatorUnavailableError,
    MacroComparisonInvalidGeographyError,
)
from .models import (
    ComparableIndicatorDefinition,
    CountryMetricObservation,
    GeographicCohort,
)


class MacroComparisonsRepository:
    """In-memory authoritative repository for cross-country macroeconomic data."""

    def __init__(self):
        self._indicators: Dict[ComparisonMetricKind, ComparableIndicatorDefinition] = {}
        self._cohorts: Dict[str, GeographicCohort] = {}
        self._country_metadata: Dict[str, Dict[str, str]] = {}
        # Multi-key index: (geography_id, metric_kind, reference_period) -> CountryMetricObservation
        self._observations: Dict[Tuple[str, ComparisonMetricKind, str], CountryMetricObservation] = {}
        # Historical index: (geography_id, metric_kind) -> List[CountryMetricObservation] (chronological)
        self._historical_series: Dict[Tuple[str, ComparisonMetricKind], List[CountryMetricObservation]] = {}

        self._seed_indicator_definitions()
        self._seed_cohorts()
        self._seed_country_metadata()
        self._seed_observations()

    # -------------------------------------------------------------------------
    # Indicator Definitions
    # -------------------------------------------------------------------------

    def _seed_indicator_definitions(self) -> None:
        defs = [
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GDP_NOMINAL_USD,
                name="Nominal GDP (Current USD)",
                category="NATIONAL_ACCOUNTS",
                default_unit="USD_BILLIONS",
                description="Gross Domestic Product converted to current US dollars at official market exchange rates.",
                higher_is_better=True,
                methodology_notes="Market exchange rate conversion (SNA 2008 / ESA 2010). Reflects nominal size of economy.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GDP_REAL_GROWTH_YOY,
                name="Real GDP Growth (YoY)",
                category="NATIONAL_ACCOUNTS",
                default_unit="PERCENT",
                description="Annual percentage change in constant-price inflation-adjusted Gross Domestic Product.",
                higher_is_better=True,
                methodology_notes="Year-over-year chain-volume or constant price measures. Non-annualized.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GDP_PER_CAPITA_USD,
                name="Nominal GDP per Capita (USD)",
                category="NATIONAL_ACCOUNTS",
                default_unit="USD",
                description="Gross Domestic Product per person at market exchange rates.",
                higher_is_better=True,
                methodology_notes="Derived as Total Nominal GDP (USD) divided by mid-year resident population.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GDP_PPP_INT_USD,
                name="GDP at Purchasing Power Parity (Int'l $)",
                category="NATIONAL_ACCOUNTS",
                default_unit="INT_USD_BILLIONS",
                description="GDP evaluated at purchasing power parity exchange rates in international dollars.",
                higher_is_better=True,
                methodology_notes="World Bank / IMF International Comparison Program (ICP). Eliminates price level differences.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GDP_PPP_PER_CAPITA,
                name="GDP PPP per Capita (Int'l $)",
                category="NATIONAL_ACCOUNTS",
                default_unit="INT_USD",
                description="Purchasing power parity GDP per person in current international dollars.",
                higher_is_better=True,
                methodology_notes="Standardized measure of real output volume per capita.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY,
                name="Headline CPI Inflation (YoY)",
                category="INFLATION",
                default_unit="PERCENT",
                description="Annual percentage rate of change in the headline Consumer Price Index basket.",
                higher_is_better=False,
                methodology_notes="National official CPI baskets; Euro Area uses HICP. Standard 12-month change.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.INFLATION_CORE_YOY,
                name="Core Inflation (YoY)",
                category="INFLATION",
                default_unit="PERCENT",
                description="Underlying Consumer Price Index excluding volatile components (Food and Energy).",
                higher_is_better=False,
                methodology_notes="Ex-Food & Energy. Strips transitory commodity shocks.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.UNEMPLOYMENT_RATE,
                name="Unemployment Rate",
                category="LABOR_MARKET",
                default_unit="PERCENT",
                description="Jobless persons actively seeking work as a percentage of the total civilian labor force.",
                higher_is_better=False,
                methodology_notes="ILO standard labor force survey definitions (seasonally adjusted).",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.LABOR_FORCE_PARTICIPATION,
                name="Labor Force Participation Rate",
                category="LABOR_MARKET",
                default_unit="PERCENT",
                description="Civilian labor force as a percentage of working-age population (15-64 or 16+).",
                higher_is_better=True,
                methodology_notes="Reflects active economic engagement. Age ranges documented per jurisdiction.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.POLICY_INTEREST_RATE,
                name="Central Bank Policy Rate",
                category="MONETARY",
                default_unit="PERCENT",
                description="Primary monetary policy target rate, operational target midpoint, or key policy rate.",
                higher_is_better=None,
                methodology_notes="Federal Funds midpoint for US; DFR for ECB; Bank Rate for BoE; Policy Repo for RBI.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP,
                name="General Government Gross Debt (% of GDP)",
                category="FISCAL",
                default_unit="PERCENT_OF_GDP",
                description="Total gross financial liabilities of general government as a percentage of nominal GDP.",
                higher_is_better=False,
                methodology_notes="IMF / OECD General Government definition (Central + Regional + Social Funds).",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.FISCAL_BALANCE_TO_GDP,
                name="Fiscal Balance (% of GDP)",
                category="FISCAL",
                default_unit="PERCENT_OF_GDP",
                description="General government net lending (+) or net borrowing (-) as a percentage of nominal GDP.",
                higher_is_better=True,
                methodology_notes="Negative values indicate budget deficits; positive values indicate fiscal surpluses.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.TRADE_BALANCE_TO_GDP,
                name="Trade Balance (% of GDP)",
                category="EXTERNAL_SECTOR",
                default_unit="PERCENT_OF_GDP",
                description="Net international exports minus imports of goods and services as a percentage of GDP.",
                higher_is_better=True,
                methodology_notes="Balance of Payments (BPM6) standards. Goods and services combined.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP,
                name="Current Account Balance (% of GDP)",
                category="EXTERNAL_SECTOR",
                default_unit="PERCENT_OF_GDP",
                description="Current account balance including trade, primary income, and secondary transfers as a % of GDP.",
                higher_is_better=True,
                methodology_notes="Comprehensive international balance of payments position.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.FOREIGN_RESERVES_USD,
                name="Foreign Exchange Reserves (USD Billions)",
                category="EXTERNAL_SECTOR",
                default_unit="USD_BILLIONS",
                description="Total official external reserves held by central monetary authorities in US dollars.",
                higher_is_better=True,
                methodology_notes="Includes foreign currency assets, gold holdings, SDRs, and IMF reserve tranches.",
            ),
            ComparableIndicatorDefinition(
                metric_kind=ComparisonMetricKind.POPULATION_MILLIONS,
                name="Total Population (Millions)",
                category="DEMOGRAPHICS",
                default_unit="MILLIONS",
                description="Total resident de jure or de facto population in millions of persons.",
                higher_is_better=None,
                methodology_notes="National statistical bureau mid-year resident estimates.",
            ),
        ]
        for d in defs:
            self._indicators[d.metric_kind] = d

    # -------------------------------------------------------------------------
    # Cohort Presets
    # -------------------------------------------------------------------------

    def _seed_cohorts(self) -> None:
        cohorts = [
            GeographicCohort(
                cohort_id="cohort-g7",
                name="Group of Seven (G7)",
                cohort_kind=GeographicCohortKind.G7,
                member_geography_ids=["geo-us", "geo-gb", "geo-jp"],
                description="Advanced industrialized economies coordinating global financial governance.",
            ),
            GeographicCohort(
                cohort_id="cohort-g20",
                name="Group of Twenty (G20)",
                cohort_kind=GeographicCohortKind.G20,
                member_geography_ids=["geo-us", "geo-ea", "geo-gb", "geo-jp", "geo-in", "geo-cn"],
                description="Major advanced and emerging market economies accounting for over 80% of global GDP.",
            ),
            GeographicCohort(
                cohort_id="cohort-brics",
                name="BRICS Economies",
                cohort_kind=GeographicCohortKind.BRICS,
                member_geography_ids=["geo-in", "geo-cn"],
                description="Major emerging economic powerhouses with rapid industrialization and demographic scale.",
            ),
            GeographicCohort(
                cohort_id="cohort-oecd",
                name="OECD Advanced Economies",
                cohort_kind=GeographicCohortKind.OECD,
                member_geography_ids=["geo-us", "geo-ea", "geo-gb", "geo-jp"],
                description="Developed democratic market economies with high human development standards.",
            ),
            GeographicCohort(
                cohort_id="cohort-eu",
                name="Euro Area / European Union",
                cohort_kind=GeographicCohortKind.EU_EURO_AREA,
                member_geography_ids=["geo-ea"],
                description="Single European currency union and central monetary authority.",
            ),
        ]
        for c in cohorts:
            self._cohorts[c.cohort_id] = c

    def _seed_country_metadata(self) -> None:
        self._country_metadata = {
            "geo-us": {"name": "United States", "iso": "US", "currency": "USD", "region": "North America"},
            "geo-ea": {"name": "Euro Area", "iso": "EU", "currency": "EUR", "region": "Europe"},
            "geo-gb": {"name": "United Kingdom", "iso": "GB", "currency": "GBP", "region": "Europe"},
            "geo-jp": {"name": "Japan", "iso": "JP", "currency": "JPY", "region": "Asia-Pacific"},
            "geo-in": {"name": "India", "iso": "IN", "currency": "INR", "region": "South Asia"},
            "geo-cn": {"name": "China", "iso": "CN", "currency": "CNY", "region": "East Asia"},
        }

    # -------------------------------------------------------------------------
    # Seed Observations Across G6 Economies
    # -------------------------------------------------------------------------

    def _add_obs(
        self,
        geo_id: str,
        metric: ComparisonMetricKind,
        period: str,
        val: float,
        unit: str,
        agency: str,
        series_id: str,
        qualifications: Optional[List[str]] = None,
    ) -> None:
        geo_info = self._country_metadata.get(geo_id, {"name": geo_id, "iso": geo_id})
        obs = CountryMetricObservation(
            geography_id=geo_id,
            country_name=geo_info["name"],
            iso_code=geo_info["iso"],
            metric_kind=metric,
            reference_period=period,
            raw_value=val,
            formatted_value=f"{val:,.2f}" if isinstance(val, float) else str(val),
            unit=unit,
            source_agency=agency,
            source_series_id=series_id,
            vintage_date=f"{period}-REV",
            is_preliminary=False,
            methodology_qualifications=qualifications or [],
        )
        self._observations[(geo_id, metric, period)] = obs
        key = (geo_id, metric)
        if key not in self._historical_series:
            self._historical_series[key] = []
        self._historical_series[key].append(obs)

    def _seed_observations(self) -> None:
        """Seed verified official macroeconomic figures for 2021, 2022, 2023, and 2024."""
        # 1. UNITED STATES (geo-us)
        # GDP Nominal USD (Billions)
        self._add_obs("geo-us", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 23315.0, "USD_BILLIONS", "BEA", "GDP")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 25462.7, "USD_BILLIONS", "BEA", "GDP")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 27360.9, "USD_BILLIONS", "BEA", "GDP")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 28781.1, "USD_BILLIONS", "BEA", "GDP")

        # Real GDP Growth YoY (%)
        self._add_obs("geo-us", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 5.9, "PERCENT", "BEA", "GDPC1_PCH")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 1.9, "PERCENT", "BEA", "GDPC1_PCH")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 2.5, "PERCENT", "BEA", "GDPC1_PCH")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 2.8, "PERCENT", "BEA", "GDPC1_PCH")

        # GDP Per Capita USD
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2021", 70250.0, "USD", "BEA/Census", "A939RC0")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2022", 76370.0, "USD", "BEA/Census", "A939RC0")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2023", 81690.0, "USD", "BEA/Census", "A939RC0")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 85370.0, "USD", "BEA/Census", "A939RC0")

        # GDP PPP Int'l USD (Billions)
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 28781.1, "INT_USD_BILLIONS", "World Bank", "NY.GDP.MKTP.PP.CD")
        self._add_obs("geo-us", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 85370.0, "INT_USD", "World Bank", "NY.GDP.PCAP.PP.CD")

        # Inflation Headline CPI YoY (%)
        self._add_obs("geo-us", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 7.0, "PERCENT", "BLS", "CPIAUCSL")
        self._add_obs("geo-us", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 6.5, "PERCENT", "BLS", "CPIAUCSL")
        self._add_obs("geo-us", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 3.4, "PERCENT", "BLS", "CPIAUCSL")
        self._add_obs("geo-us", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 2.6, "PERCENT", "BLS", "CPIAUCSL")

        # Core Inflation YoY (%)
        self._add_obs("geo-us", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 3.3, "PERCENT", "BLS", "CPILFESL")

        # Labor & Policy
        self._add_obs("geo-us", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 4.1, "PERCENT", "BLS", "UNRATE")
        self._add_obs("geo-us", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 62.7, "PERCENT", "BLS", "CIVPART")
        self._add_obs("geo-us", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 4.75, "PERCENT", "Federal Reserve", "DFEDTARMD")
        self._add_obs("geo-us", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 122.3, "PERCENT_OF_GDP", "IMF/Treasury", "US_DEBT_GDP")
        self._add_obs("geo-us", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -6.4, "PERCENT_OF_GDP", "OMB/Treasury", "US_DEFICIT_GDP")
        self._add_obs("geo-us", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", -2.8, "PERCENT_OF_GDP", "BEA", "BOPGSTB")
        self._add_obs("geo-us", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", -3.0, "PERCENT_OF_GDP", "BEA", "US_CA_GDP")
        self._add_obs("geo-us", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 242.0, "USD_BILLIONS", "Treasury/Fed", "US_RESERVES")
        self._add_obs("geo-us", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 336.0, "MILLIONS", "Census Bureau", "POPTHM")

        # 2. EURO AREA (geo-ea)
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 14520.0, "USD_BILLIONS", "Eurostat", "EA_GDP_USD")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 14180.0, "USD_BILLIONS", "Eurostat", "EA_GDP_USD")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 15530.0, "USD_BILLIONS", "Eurostat", "EA_GDP_USD")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 16140.0, "USD_BILLIONS", "Eurostat", "EA_GDP_USD")

        self._add_obs("geo-ea", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 5.9, "PERCENT", "Eurostat", "EA_GDP_REAL")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 3.4, "PERCENT", "Eurostat", "EA_GDP_REAL")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 0.4, "PERCENT", "Eurostat", "EA_GDP_REAL")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 0.9, "PERCENT", "Eurostat", "EA_GDP_REAL")

        self._add_obs("geo-ea", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 46110.0, "USD", "Eurostat", "EA_GDP_PC")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 21350.0, "INT_USD_BILLIONS", "IMF", "EA_PPP_GDP")
        self._add_obs("geo-ea", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 61000.0, "INT_USD", "IMF", "EA_PPP_PC")

        self._add_obs("geo-ea", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 5.0, "PERCENT", "Eurostat", "HICP_EA")
        self._add_obs("geo-ea", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 9.2, "PERCENT", "Eurostat", "HICP_EA")
        self._add_obs("geo-ea", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 2.9, "PERCENT", "Eurostat", "HICP_EA")
        self._add_obs("geo-ea", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 2.0, "PERCENT", "Eurostat", "HICP_EA", qualifications=["Eurostat Harmonised Index of Consumer Prices (HICP)"])
        self._add_obs("geo-ea", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 2.7, "PERCENT", "Eurostat", "HICP_CORE")

        self._add_obs("geo-ea", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 6.3, "PERCENT", "Eurostat", "UNE_EA")
        self._add_obs("geo-ea", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 65.4, "PERCENT", "Eurostat", "LFP_EA")
        self._add_obs("geo-ea", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 3.25, "PERCENT", "ECB", "ECB_DFR", qualifications=["ECB Deposit Facility Rate"])
        self._add_obs("geo-ea", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 88.6, "PERCENT_OF_GDP", "Eurostat", "EA_DEBT_GDP")
        self._add_obs("geo-ea", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -3.6, "PERCENT_OF_GDP", "Eurostat", "EA_DEFICIT_GDP")
        self._add_obs("geo-ea", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", 2.1, "PERCENT_OF_GDP", "Eurostat", "EA_TRADE_GDP")
        self._add_obs("geo-ea", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", 2.8, "PERCENT_OF_GDP", "ECB", "EA_CA_GDP")
        self._add_obs("geo-ea", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 1280.0, "USD_BILLIONS", "ECB", "EA_RESERVES")
        self._add_obs("geo-ea", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 350.0, "MILLIONS", "Eurostat", "EA_POP")

        # 3. UNITED KINGDOM (geo-gb)
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 3140.0, "USD_BILLIONS", "ONS", "UK_GDP_USD")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 3080.0, "USD_BILLIONS", "ONS", "UK_GDP_USD")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 3340.0, "USD_BILLIONS", "ONS", "UK_GDP_USD")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 3495.0, "USD_BILLIONS", "ONS", "UK_GDP_USD")

        self._add_obs("geo-gb", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 8.7, "PERCENT", "ONS", "UK_GDP_REAL")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 4.3, "PERCENT", "ONS", "UK_GDP_REAL")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 0.3, "PERCENT", "ONS", "UK_GDP_REAL")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 1.1, "PERCENT", "ONS", "UK_GDP_REAL")

        self._add_obs("geo-gb", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 51070.0, "USD", "ONS", "UK_GDP_PC")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 4030.0, "INT_USD_BILLIONS", "IMF", "UK_PPP_GDP")
        self._add_obs("geo-gb", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 58900.0, "INT_USD", "IMF", "UK_PPP_PC")

        self._add_obs("geo-gb", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 5.4, "PERCENT", "ONS", "UK_CPI")
        self._add_obs("geo-gb", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 10.5, "PERCENT", "ONS", "UK_CPI")
        self._add_obs("geo-gb", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 4.0, "PERCENT", "ONS", "UK_CPI")
        self._add_obs("geo-gb", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 1.7, "PERCENT", "ONS", "UK_CPI")
        self._add_obs("geo-gb", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 3.2, "PERCENT", "ONS", "UK_CORE_CPI")

        self._add_obs("geo-gb", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 4.3, "PERCENT", "ONS", "UK_UNRATE")
        self._add_obs("geo-gb", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 78.2, "PERCENT", "ONS", "UK_LFP", qualifications=["Aged 16-64"])
        self._add_obs("geo-gb", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 4.75, "PERCENT", "Bank of England", "BOE_RATE", qualifications=["BoE MPC Official Bank Rate"])
        self._add_obs("geo-gb", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 98.2, "PERCENT_OF_GDP", "ONS/OBR", "UK_DEBT_GDP")
        self._add_obs("geo-gb", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -4.4, "PERCENT_OF_GDP", "ONS", "UK_DEFICIT_GDP")
        self._add_obs("geo-gb", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", -1.9, "PERCENT_OF_GDP", "ONS", "UK_TRADE_GDP")
        self._add_obs("geo-gb", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", -3.3, "PERCENT_OF_GDP", "ONS", "UK_CA_GDP")
        self._add_obs("geo-gb", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 180.0, "USD_BILLIONS", "Bank of England", "UK_RESERVES")
        self._add_obs("geo-gb", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 68.4, "MILLIONS", "ONS", "UK_POP")

        # 4. JAPAN (geo-jp)
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 5035.0, "USD_BILLIONS", "Cabinet Office", "JP_GDP_USD")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 4260.0, "USD_BILLIONS", "Cabinet Office", "JP_GDP_USD")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 4210.0, "USD_BILLIONS", "Cabinet Office", "JP_GDP_USD")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 4210.0, "USD_BILLIONS", "Cabinet Office", "JP_GDP_USD")

        self._add_obs("geo-jp", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 2.2, "PERCENT", "Cabinet Office", "JP_GDP_REAL")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 1.0, "PERCENT", "Cabinet Office", "JP_GDP_REAL")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 1.9, "PERCENT", "Cabinet Office", "JP_GDP_REAL")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 0.3, "PERCENT", "Cabinet Office", "JP_GDP_REAL")

        self._add_obs("geo-jp", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 33800.0, "USD", "Cabinet Office", "JP_GDP_PC")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 6490.0, "INT_USD_BILLIONS", "IMF", "JP_PPP_GDP")
        self._add_obs("geo-jp", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 52100.0, "INT_USD", "IMF", "JP_PPP_PC")

        self._add_obs("geo-jp", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 0.8, "PERCENT", "Statistics Bureau", "JP_CPI")
        self._add_obs("geo-jp", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 4.0, "PERCENT", "Statistics Bureau", "JP_CPI")
        self._add_obs("geo-jp", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 2.6, "PERCENT", "Statistics Bureau", "JP_CPI")
        self._add_obs("geo-jp", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 2.5, "PERCENT", "Statistics Bureau", "JP_CPI")
        self._add_obs("geo-jp", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 2.1, "PERCENT", "Statistics Bureau", "JP_CORE_CPI")

        self._add_obs("geo-jp", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 2.5, "PERCENT", "Statistics Bureau", "JP_UNRATE")
        self._add_obs("geo-jp", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 63.1, "PERCENT", "Statistics Bureau", "JP_LFP")
        self._add_obs("geo-jp", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 0.25, "PERCENT", "Bank of Japan", "BOJ_RATE", qualifications=["BoJ Uncollateralized Overnight Call Rate"])
        self._add_obs("geo-jp", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 255.2, "PERCENT_OF_GDP", "MoF/IMF", "JP_DEBT_GDP")
        self._add_obs("geo-jp", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -5.8, "PERCENT_OF_GDP", "MoF", "JP_DEFICIT_GDP")
        self._add_obs("geo-jp", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", -0.8, "PERCENT_OF_GDP", "MoF", "JP_TRADE_GDP")
        self._add_obs("geo-jp", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", 3.5, "PERCENT_OF_GDP", "MoF", "JP_CA_GDP")
        self._add_obs("geo-jp", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 1240.0, "USD_BILLIONS", "MoF/BoJ", "JP_RESERVES")
        self._add_obs("geo-jp", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 124.5, "MILLIONS", "Statistics Bureau", "JP_POP")

        # 5. INDIA (geo-in)
        self._add_obs("geo-in", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 3150.0, "USD_BILLIONS", "MoSPI", "IN_GDP_USD")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 3390.0, "USD_BILLIONS", "MoSPI", "IN_GDP_USD")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 3570.0, "USD_BILLIONS", "MoSPI", "IN_GDP_USD")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 3940.0, "USD_BILLIONS", "MoSPI", "IN_GDP_USD")

        self._add_obs("geo-in", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 9.1, "PERCENT", "MoSPI", "IN_GDP_REAL")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 7.2, "PERCENT", "MoSPI", "IN_GDP_REAL")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 8.2, "PERCENT", "MoSPI", "IN_GDP_REAL")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 6.7, "PERCENT", "MoSPI", "IN_GDP_REAL")

        self._add_obs("geo-in", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 2730.0, "USD", "MoSPI", "IN_GDP_PC")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 14590.0, "INT_USD_BILLIONS", "IMF", "IN_PPP_GDP")
        self._add_obs("geo-in", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 10120.0, "INT_USD", "IMF", "IN_PPP_PC")

        self._add_obs("geo-in", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 5.6, "PERCENT", "MoSPI", "IN_CPI")
        self._add_obs("geo-in", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 5.7, "PERCENT", "MoSPI", "IN_CPI")
        self._add_obs("geo-in", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 5.69, "PERCENT", "MoSPI", "IN_CPI")
        self._add_obs("geo-in", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 5.49, "PERCENT", "MoSPI", "IN_CPI", qualifications=["All-India Combined CPI"])
        self._add_obs("geo-in", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 3.7, "PERCENT", "MoSPI", "IN_CORE_CPI")

        self._add_obs("geo-in", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 3.2, "PERCENT", "MoSPI", "IN_UNRATE", qualifications=["PLFS Annual Activity Status"])
        self._add_obs("geo-in", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 58.4, "PERCENT", "MoSPI", "IN_LFP")
        self._add_obs("geo-in", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 6.50, "PERCENT", "RBI", "RBI_REPO", qualifications=["RBI Policy Repo Rate"])
        self._add_obs("geo-in", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 83.1, "PERCENT_OF_GDP", "MoF/IMF", "IN_DEBT_GDP")
        self._add_obs("geo-in", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -5.6, "PERCENT_OF_GDP", "MoF", "IN_DEFICIT_GDP")
        self._add_obs("geo-in", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", -6.5, "PERCENT_OF_GDP", "Commerce Ministry", "IN_TRADE_GDP")
        self._add_obs("geo-in", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", -1.2, "PERCENT_OF_GDP", "RBI", "IN_CA_GDP")
        self._add_obs("geo-in", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 690.0, "USD_BILLIONS", "RBI", "IN_RESERVES")
        self._add_obs("geo-in", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 1440.0, "MILLIONS", "MoSPI/UN", "IN_POP")

        # 6. CHINA (geo-cn)
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_NOMINAL_USD, "2021", 17820.0, "USD_BILLIONS", "NBS", "CN_GDP_USD")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_NOMINAL_USD, "2022", 18100.0, "USD_BILLIONS", "NBS", "CN_GDP_USD")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_NOMINAL_USD, "2023", 17790.0, "USD_BILLIONS", "NBS", "CN_GDP_USD")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_NOMINAL_USD, "2024", 18530.0, "USD_BILLIONS", "NBS", "CN_GDP_USD")

        self._add_obs("geo-cn", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2021", 8.4, "PERCENT", "NBS", "CN_GDP_REAL")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2022", 3.0, "PERCENT", "NBS", "CN_GDP_REAL")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2023", 5.2, "PERCENT", "NBS", "CN_GDP_REAL")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_REAL_GROWTH_YOY, "2024", 4.8, "PERCENT", "NBS", "CN_GDP_REAL")

        self._add_obs("geo-cn", ComparisonMetricKind.GDP_PER_CAPITA_USD, "2024", 13150.0, "USD", "NBS", "CN_GDP_PC")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_PPP_INT_USD, "2024", 35290.0, "INT_USD_BILLIONS", "IMF", "CN_PPP_GDP")
        self._add_obs("geo-cn", ComparisonMetricKind.GDP_PPP_PER_CAPITA, "2024", 25050.0, "INT_USD", "IMF", "CN_PPP_PC")

        self._add_obs("geo-cn", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2021", 1.5, "PERCENT", "NBS", "CN_CPI")
        self._add_obs("geo-cn", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2022", 1.8, "PERCENT", "NBS", "CN_CPI")
        self._add_obs("geo-cn", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2023", 0.2, "PERCENT", "NBS", "CN_CPI")
        self._add_obs("geo-cn", ComparisonMetricKind.INFLATION_HEADLINE_CPI_YOY, "2024", 0.4, "PERCENT", "NBS", "CN_CPI")
        self._add_obs("geo-cn", ComparisonMetricKind.INFLATION_CORE_YOY, "2024", 0.1, "PERCENT", "NBS", "CN_CORE_CPI")

        self._add_obs("geo-cn", ComparisonMetricKind.UNEMPLOYMENT_RATE, "2024", 5.1, "PERCENT", "NBS", "CN_UNRATE", qualifications=["Urban Surveyed Unemployment Rate"])
        self._add_obs("geo-cn", ComparisonMetricKind.LABOR_FORCE_PARTICIPATION, "2024", 66.8, "PERCENT", "NBS", "CN_LFP")
        self._add_obs("geo-cn", ComparisonMetricKind.POLICY_INTEREST_RATE, "2024", 3.10, "PERCENT", "PBoC", "PBOC_1Y_LPR", qualifications=["PBoC 1-Year Loan Prime Rate"])
        self._add_obs("geo-cn", ComparisonMetricKind.GOVERNMENT_DEBT_TO_GDP, "2024", 83.6, "PERCENT_OF_GDP", "MoF/IMF", "CN_DEBT_GDP", qualifications=["Central and official local government debt; excludes LGFVs"])
        self._add_obs("geo-cn", ComparisonMetricKind.FISCAL_BALANCE_TO_GDP, "2024", -7.1, "PERCENT_OF_GDP", "MoF/IMF", "CN_DEFICIT_GDP")
        self._add_obs("geo-cn", ComparisonMetricKind.TRADE_BALANCE_TO_GDP, "2024", 4.5, "PERCENT_OF_GDP", "Customs", "CN_TRADE_GDP")
        self._add_obs("geo-cn", ComparisonMetricKind.CURRENT_ACCOUNT_TO_GDP, "2024", 1.5, "PERCENT_OF_GDP", "SAFE", "CN_CA_GDP")
        self._add_obs("geo-cn", ComparisonMetricKind.FOREIGN_RESERVES_USD, "2024", 3260.0, "USD_BILLIONS", "SAFE", "CN_RESERVES")
        self._add_obs("geo-cn", ComparisonMetricKind.POPULATION_MILLIONS, "2024", 1409.0, "MILLIONS", "NBS", "CN_POP")

    # -------------------------------------------------------------------------
    # Public Read APIs
    # -------------------------------------------------------------------------

    def list_indicators(self) -> List[ComparableIndicatorDefinition]:
        return list(self._indicators.values())

    def get_indicator(self, metric_kind: ComparisonMetricKind) -> ComparableIndicatorDefinition:
        if metric_kind not in self._indicators:
            raise MacroComparisonIndicatorUnavailableError(metric_kind, "GLOBAL")
        return self._indicators[metric_kind]

    def list_cohorts(self) -> List[GeographicCohort]:
        return list(self._cohorts.values())

    def get_cohort(self, cohort_id: str) -> Optional[GeographicCohort]:
        return self._cohorts.get(cohort_id)

    def list_supported_geographies(self) -> List[Dict[str, str]]:
        return [
            {"geography_id": gid, "name": meta["name"], "iso_code": meta["iso"], "currency": meta["currency"], "region": meta["region"]}
            for gid, meta in self._country_metadata.items()
        ]

    def get_observation(
        self,
        geography_id: str,
        metric_kind: ComparisonMetricKind,
        period: Optional[str] = None,
    ) -> Optional[CountryMetricObservation]:
        if geography_id not in self._country_metadata:
            raise MacroComparisonInvalidGeographyError(geography_id)

        if period:
            return self._observations.get((geography_id, metric_kind, period))

        # If period not specified, retrieve latest available period
        series = self._historical_series.get((geography_id, metric_kind), [])
        return series[-1] if series else None

    def get_historical_series(
        self,
        geography_id: str,
        metric_kind: ComparisonMetricKind,
    ) -> List[CountryMetricObservation]:
        if geography_id not in self._country_metadata:
            raise MacroComparisonInvalidGeographyError(geography_id)
        return self._historical_series.get((geography_id, metric_kind), [])
