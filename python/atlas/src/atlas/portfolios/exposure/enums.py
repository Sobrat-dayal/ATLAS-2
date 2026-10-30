"""ATLAS Portfolios V1 — Portfolio Allocation & Exposure Enums (Stage 112).

Defines canonical dimensions, policies, asset classes, and data completeness states
for institutional portfolio allocation, look-through, and concentration analytics.
"""

from enum import Enum


class ExposureBasis(str, Enum):
    """Underlying accounting basis for exposure calculation."""
    DIRECT = "DIRECT"  # Actual held securities and cash
    LOOK_THROUGH = "LOOK_THROUGH"  # Funds decomposed into eligible underlying constituents
    GROSS = "GROSS"  # Absolute value weights for long/short
    NET = "NET"  # Signed economic value weights
    NET_ASSET_VALUE = "NET_ASSET_VALUE"  # Denominator is Net Asset Value (NAV)
    LONG_ONLY = "LONG_ONLY"
    SHORT_ONLY = "SHORT_ONLY"


class ExposureDimension(str, Enum):
    """Categorical aggregation dimension."""
    ASSET_CLASS = "ASSET_CLASS"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    COUNTRY = "COUNTRY"
    REGION = "REGION"
    CURRENCY = "CURRENCY"
    SECURITY = "SECURITY"
    ISSUER = "ISSUER"


class AssetClass(str, Enum):
    """Canonical asset-class taxonomy."""
    EQUITY = "EQUITY"
    FUND = "FUND"
    FIXED_INCOME = "FIXED_INCOME"
    CASH = "CASH"
    CASH_EQUIVALENT = "CASH_EQUIVALENT"
    COMMODITY = "COMMODITY"
    DIGITAL_ASSET = "DIGITAL_ASSET"
    DERIVATIVE = "DERIVATIVE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class SectorTaxonomy(str, Enum):
    """Standardized industrial sector classification taxonomy."""
    GICS = "GICS"  # Global Industry Classification Standard
    ICB = "ICB"    # Industry Classification Benchmark
    ATLAS_STANDARD = "ATLAS_STANDARD"


class GeographyPolicy(str, Enum):
    """Analytical perspective for assigning geographic country exposure."""
    ISSUER_DOMICILE = "ISSUER_DOMICILE"  # Legal country of incorporation / domicile
    HEADQUARTERS = "HEADQUARTERS"        # Country of principal executive offices
    LISTING_VENUE = "LISTING_VENUE"      # Country of primary trading exchange
    REVENUE_GEOGRAPHY = "REVENUE_GEOGRAPHY"  # Geographic segment revenue disclosure


class ConcentrationScope(str, Enum):
    """Unit of analysis for portfolio concentration."""
    SECURITY = "SECURITY"  # Distinct instrument / listing level
    ISSUER = "ISSUER"      # Consolidated parent company / economic issuer level


class LookThroughStatus(str, Enum):
    """Constituent coverage status of an expanded fund."""
    COMPLETE = "COMPLETE"          # 100% of fund holdings mapped
    PARTIAL = "PARTIAL"            # Constituents available with residual unclassified bucket
    UNAVAILABLE = "UNAVAILABLE"    # Fund holdings disclosures not available
    NOT_APPLICABLE = "NOT_APPLICABLE"  # Direct security or cash position


class ExposureDataCompleteness(str, Enum):
    """Comprehensive data completeness audit status for an exposure run."""
    COMPLETE = "COMPLETE"
    COMPLETE_WITH_WARNINGS = "COMPLETE_WITH_WARNINGS"
    PARTIAL_CLASSIFICATION = "PARTIAL_CLASSIFICATION"
    PARTIAL_FUND_HOLDINGS = "PARTIAL_FUND_HOLDINGS"
    PARTIAL_VALUATION = "PARTIAL_VALUATION"
    PARTIAL_FX = "PARTIAL_FX"
    SOURCE_RESTRICTED = "SOURCE_RESTRICTED"
    EMPTY = "EMPTY"
    FAILED = "FAILED"

