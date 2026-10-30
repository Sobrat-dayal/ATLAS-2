"""ATLAS Portfolios V1 — Performance Attribution Enums (Stage 113).

Defines canonical attribution methods, classification dimensions,
reconciliation states, data completeness tiers, and multi-period linking policies.
"""

from enum import Enum


class AttributionMethod(str, Enum):
    """Supported performance attribution methodologies."""
    BRINSON_FACHLER = "BRINSON_FACHLER"
    BRINSON_HOOD_BEEBOWER = "BRINSON_HOOD_BEEBOWER"
    ABSOLUTE_RETURN_CONTRIBUTION = "ABSOLUTE_RETURN_CONTRIBUTION"
    MULTIPERIOD_CARINO_LINKED = "MULTIPERIOD_CARINO_LINKED"
    CURRENCY_LOCAL_FX_DECOMPOSITION = "CURRENCY_LOCAL_FX_DECOMPOSITION"


class AttributionDimension(str, Enum):
    """Categorical classification dimension for attribution decomposition."""
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    ASSET_CLASS = "ASSET_CLASS"
    GEOGRAPHY = "GEOGRAPHY"
    CURRENCY = "CURRENCY"


class ReconciliationStatus(str, Enum):
    """Mathematical audit reconciliation status."""
    RECONCILED = "RECONCILED"
    RECONCILED_WITH_ROUNDING_TOLERANCE = "RECONCILED_WITH_ROUNDING_TOLERANCE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    METHODOLOGY_MISMATCH = "METHODOLOGY_MISMATCH"
    SOURCE_DATA_INCONSISTENT = "SOURCE_DATA_INCONSISTENT"
    UNRECONCILED = "UNRECONCILED"
    FAILED = "FAILED"


class AttributionCompleteness(str, Enum):
    """Attribution data completeness and coverage tiers."""
    COMPLETE = "COMPLETE"
    COMPLETE_WITH_FALLBACKS = "COMPLETE_WITH_FALLBACKS"
    PARTIAL_UNMAPPED = "PARTIAL_UNMAPPED"
    INCOMPLETE = "INCOMPLETE"
    BENCHMARK_CONSTITUENTS_MISSING = "BENCHMARK_CONSTITUENTS_MISSING"


class MultiPeriodLinkingMethod(str, Enum):
    """Multi-period attribution linking algorithms."""
    CARINO = "CARINO"
    MENCHERO = "MENCHERO"
    GEOMETRIC_ANNUALIZED = "GEOMETRIC_ANNUALIZED"
    UNLINKED_ARITHMETIC = "UNLINKED_ARITHMETIC"

