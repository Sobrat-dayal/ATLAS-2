"""Enumerations for Macroeconomic Comparisons & Benchmarking (Stage 93).

Defines controlled taxonomies for comparison metrics, compatibility states,
geographic cohorts, period alignment policies, ranking directions, and weighting rules.
"""

from enum import StrEnum


class ComparisonMetricKind(StrEnum):
    """Canonical macroeconomic comparison metrics across sovereign economies."""
    # National Accounts & Economic Output
    GDP_NOMINAL_USD = "GDP_NOMINAL_USD"                   # Current USD Billions (Market Exchange Rates)
    GDP_REAL_GROWTH_YOY = "GDP_REAL_GROWTH_YOY"           # Real GDP growth YoY (%)
    GDP_PER_CAPITA_USD = "GDP_PER_CAPITA_USD"             # Nominal GDP per capita (USD)
    GDP_PPP_INT_USD = "GDP_PPP_INT_USD"                   # GDP at Purchasing Power Parity (Current Int'l USD Billions)
    GDP_PPP_PER_CAPITA = "GDP_PPP_PER_CAPITA"             # GDP PPP per capita (Current Int'l USD)

    # Price Stability & Inflation
    INFLATION_HEADLINE_CPI_YOY = "INFLATION_HEADLINE_CPI_YOY" # Headline Consumer Price Index YoY (%)
    INFLATION_CORE_YOY = "INFLATION_CORE_YOY"             # Core Inflation YoY (ex-Food & Energy) (%)

    # Labor Market
    UNEMPLOYMENT_RATE = "UNEMPLOYMENT_RATE"               # Harmonized / Official Unemployment Rate (%)
    LABOR_FORCE_PARTICIPATION = "LABOR_FORCE_PARTICIPATION" # Labor force participation rate (%)

    # Monetary Policy
    POLICY_INTEREST_RATE = "POLICY_INTEREST_RATE"         # Primary policy rate / target midpoint (%)

    # Fiscal & Public Debt
    GOVERNMENT_DEBT_TO_GDP = "GOVERNMENT_DEBT_TO_GDP"     # General/Central government gross debt (% of GDP)
    FISCAL_BALANCE_TO_GDP = "FISCAL_BALANCE_TO_GDP"       # Fiscal balance / Net lending/borrowing (% of GDP)

    # External Sector & Trade
    TRADE_BALANCE_TO_GDP = "TRADE_BALANCE_TO_GDP"         # Trade balance (% of GDP)
    CURRENT_ACCOUNT_TO_GDP = "CURRENT_ACCOUNT_TO_GDP"     # Current account balance (% of GDP)
    FOREIGN_RESERVES_USD = "FOREIGN_RESERVES_USD"         # Total Foreign Exchange Reserves (USD Billions)

    # Demographics
    POPULATION_MILLIONS = "POPULATION_MILLIONS"           # Total population (Millions of persons)


class CompatibilityStatus(StrEnum):
    """Statistical comparability classification between cross-country series."""
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"               # Aligned concepts, units, and methodology
    COMPARABLE_WITH_QUALIFICATION = "COMPARABLE_WITH_QUALIFICATION" # Usable with explicit methodological caveats
    TRANSFORMABLE = "TRANSFORMABLE"                           # Requires deterministic unit or period transformation
    INCOMPATIBLE = "INCOMPATIBLE"                             # Conceptually or statistically invalid to compare
    INSUFFICIENT_METADATA = "INSUFFICIENT_METADATA"           # Missing source documentation to establish compatibility


class GeographicCohortKind(StrEnum):
    """Standardized geopolitical and economic grouping presets."""
    G7 = "G7"                         # Group of Seven (US, UK, Japan, Germany, France, Italy, Canada)
    G20 = "G20"                       # Group of Twenty major economies
    BRICS = "BRICS"                   # Brazil, Russia, India, China, South Africa + Expansion
    OECD = "OECD"                     # Organisation for Economic Co-operation and Development
    EU_EURO_AREA = "EU_EURO_AREA"     # Euro Area / European Union members
    CUSTOM_SELECTION = "CUSTOM_SELECTION" # User-defined multi-country selection


class PeriodAlignmentPolicy(StrEnum):
    """Temporal alignment policy for multi-country observation matrices."""
    EXACT_PERIOD = "EXACT_PERIOD"             # Strict matching on reference period (e.g., 2024-Q3)
    LATEST_COMMON = "LATEST_COMMON"           # Latest period where ALL selected countries have data
    LATEST_PER_COUNTRY = "LATEST_PER_COUNTRY" # Most recent available observation per country (with date badges)


class RankingDirection(StrEnum):
    """Directional ordering for economic rankings."""
    DESCENDING = "DESCENDING" # Highest value ranked #1 (e.g., GDP level, growth rate)
    ASCENDING = "ASCENDING"   # Lowest value ranked #1 (e.g., inflation rate, debt ratio, unemployment)


class TieBreakerPolicy(StrEnum):
    """Policy for handling ties in economic ranking computations."""
    STANDARD_COMPETITION = "STANDARD_COMPETITION" # 1, 2, 2, 4 (Standard Olympics / competition ranking)
    DENSE = "DENSE"                               # 1, 2, 2, 3 (Dense ranking)


class WeightingPolicy(StrEnum):
    """Weighting scheme for aggregate and distribution calculations."""
    EQUAL_WEIGHT = "EQUAL_WEIGHT"           # Arithmetic unweighted average across countries
    POPULATION_WEIGHT = "POPULATION_WEIGHT" # Weighted by sovereign population
    GDP_WEIGHT = "GDP_WEIGHT"               # Weighted by nominal GDP (USD)


class CorrelationMethod(StrEnum):
    """Statistical correlation algorithm for paired economic time series."""
    PEARSON = "PEARSON"   # Linear correlation coefficient
    SPEARMAN = "SPEARMAN" # Rank-order non-parametric correlation coefficient


class VintagePolicy(StrEnum):
    """Historical data vintage retrieval policy."""
    LATEST_REVISED = "LATEST_REVISED" # Current historical observations with all revisions
    AS_KNOWN_AT = "AS_KNOWN_AT"       # Point-in-time observations as known on a specified historical date
