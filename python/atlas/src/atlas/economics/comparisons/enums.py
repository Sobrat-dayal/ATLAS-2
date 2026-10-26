"""Enumerations for Macroeconomic Comparisons & Benchmarking (Stage 93).

Defines controlled taxonomies for comparison metrics, compatibility states,
geographic cohorts, period alignment policies, ranking directions, and weighting rules.
"""

from enum import StrEnum


class CaseInsensitiveStrEnum(StrEnum):
    """Base StrEnum that supports case-insensitive and delimiter-insensitive lookup."""
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_norm = value.strip().upper().replace("-", "_")
            for member in cls:
                if member.value == val_norm or member.name == val_norm:
                    return member
        return super()._missing_(value)


class ComparisonMetricKind(CaseInsensitiveStrEnum):
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

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_norm = value.strip().upper().replace("-", "_")
            # Specific alias mappings
            aliases = {
                "CPI_HEADLINE_YOY": cls.INFLATION_HEADLINE_CPI_YOY,
                "HEADLINE_CPI_YOY": cls.INFLATION_HEADLINE_CPI_YOY,
                "CPI_YOY": cls.INFLATION_HEADLINE_CPI_YOY,
                "CPI_CORE_YOY": cls.INFLATION_CORE_YOY,
                "CORE_CPI_YOY": cls.INFLATION_CORE_YOY,
                "CENTRAL_BANK_POLICY_RATE": cls.POLICY_INTEREST_RATE,
                "POLICY_RATE": cls.POLICY_INTEREST_RATE,
                "INTEREST_RATE": cls.POLICY_INTEREST_RATE,
                "LABOR_PARTICIPATION_RATE": cls.LABOR_FORCE_PARTICIPATION,
                "LFP": cls.LABOR_FORCE_PARTICIPATION,
                "GDP_PPP_INTL_DOLLARS": cls.GDP_PPP_INT_USD,
                "GDP_PPP": cls.GDP_PPP_INT_USD,
                "GDP_PPP_PER_CAPITA_INTL": cls.GDP_PPP_PER_CAPITA,
                "FOREIGN_EXCHANGE_RESERVES_USD": cls.FOREIGN_RESERVES_USD,
                "FX_RESERVES": cls.FOREIGN_RESERVES_USD,
            }
            if val_norm in aliases:
                return aliases[val_norm]
            for member in cls:
                if member.value == val_norm or member.name == val_norm:
                    return member
        return super()._missing_(value)


class CompatibilityStatus(CaseInsensitiveStrEnum):
    """Statistical comparability classification between cross-country series."""
    DIRECTLY_COMPARABLE = "DIRECTLY_COMPARABLE"               # Aligned concepts, units, and methodology
    COMPARABLE_WITH_QUALIFICATION = "COMPARABLE_WITH_QUALIFICATION" # Usable with explicit methodological caveats
    TRANSFORMABLE = "TRANSFORMABLE"                           # Requires deterministic unit or period transformation
    INCOMPATIBLE = "INCOMPATIBLE"                             # Conceptually or statistically invalid to compare
    INSUFFICIENT_METADATA = "INSUFFICIENT_METADATA"           # Missing source documentation to establish compatibility


class GeographicCohortKind(CaseInsensitiveStrEnum):
    """Standardized geopolitical and economic grouping presets."""
    G7 = "G7"                         # Group of Seven (US, UK, Japan, Germany, France, Italy, Canada)
    G20 = "G20"                       # Group of Twenty major economies
    BRICS = "BRICS"                   # Brazil, Russia, India, China, South Africa + Expansion
    OECD = "OECD"                     # Organisation for Economic Co-operation and Development
    EU_EURO_AREA = "EU_EURO_AREA"     # Euro Area / European Union members
    CUSTOM_SELECTION = "CUSTOM_SELECTION" # User-defined multi-country selection


class PeriodAlignmentPolicy(CaseInsensitiveStrEnum):
    """Temporal alignment policy for multi-country observation matrices."""
    EXACT_PERIOD = "EXACT_PERIOD"             # Strict matching on reference period (e.g., 2024-Q3)
    LATEST_COMMON = "LATEST_COMMON"           # Latest period where ALL selected countries have data
    LATEST_PER_COUNTRY = "LATEST_PER_COUNTRY" # Most recent available observation per country (with date badges)

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_norm = value.strip().upper().replace("-", "_")
            if val_norm in ("LATEST_COMMON_PERIOD", "LATEST_COMMON"):
                return cls.LATEST_COMMON
            if val_norm in ("LATEST_PER_COUNTRY", "LATEST"):
                return cls.LATEST_PER_COUNTRY
            if val_norm in ("EXACT_PERIOD", "EXACT"):
                return cls.EXACT_PERIOD
        return super()._missing_(value)


class RankingDirection(CaseInsensitiveStrEnum):
    """Directional ordering for economic rankings."""
    DESCENDING = "DESCENDING" # Highest value ranked #1 (e.g., GDP level, growth rate)
    ASCENDING = "ASCENDING"   # Lowest value ranked #1 (e.g., inflation rate, debt ratio, unemployment)


class TieBreakerPolicy(CaseInsensitiveStrEnum):
    """Policy for handling ties in economic ranking computations."""
    STANDARD_COMPETITION = "STANDARD_COMPETITION" # 1, 2, 2, 4 (Standard Olympics / competition ranking)
    DENSE = "DENSE"                               # 1, 2, 2, 3 (Dense ranking)

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_norm = value.strip().upper().replace("-", "_")
            if "DENSE" in val_norm:
                return cls.DENSE
            if "COMPETITION" in val_norm or "STANDARD" in val_norm:
                return cls.STANDARD_COMPETITION
        return super()._missing_(value)


class WeightingPolicy(CaseInsensitiveStrEnum):
    """Weighting scheme for aggregate and distribution calculations."""
    EQUAL_WEIGHT = "EQUAL_WEIGHT"           # Arithmetic unweighted average across countries
    POPULATION_WEIGHT = "POPULATION_WEIGHT" # Weighted by sovereign population
    GDP_WEIGHT = "GDP_WEIGHT"               # Weighted by nominal GDP (USD)

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            val_norm = value.strip().upper().replace("-", "_")
            if val_norm.startswith("POPULATION"):
                return cls.POPULATION_WEIGHT
            if val_norm.startswith("GDP"):
                return cls.GDP_WEIGHT
            if val_norm.startswith("EQUAL"):
                return cls.EQUAL_WEIGHT
        return super()._missing_(value)


class CorrelationMethod(CaseInsensitiveStrEnum):
    """Statistical correlation algorithm for paired economic time series."""
    PEARSON = "PEARSON"   # Linear correlation coefficient
    SPEARMAN = "SPEARMAN" # Rank-order non-parametric correlation coefficient


class VintagePolicy(CaseInsensitiveStrEnum):
    """Historical data vintage retrieval policy."""
    LATEST_REVISED = "LATEST_REVISED" # Current historical observations with all revisions
    AS_KNOWN_AT = "AS_KNOWN_AT"       # Point-in-time observations as known on a specified historical date

