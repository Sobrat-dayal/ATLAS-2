"""Financial and Economic Exposure Engine (Stage 137).

Institutional-grade exposure intelligence across:
- Company and issuer revenue & asset concentration
- Long/short portfolio weights and gross/net exposure
- Multi-hop fund look-through with cycle detection
- Consolidated corporate groups without double-counting
- Documented supply chains and commodity dependencies
- Physical facility presence vs financial loss boundaries
- Point-in-time FX rates and deterministic scenarios
"""

from atlas.exposure.domain import (
    AnalysisRunStatus,
    AtlasExposureResult,
    ConsolidationBasis,
    CountryExposureBasis,
    CoverageStatus,
    ExposureAnalysisRun,
    ExposureCoverageSummary,
    ExposureDomain,
    ExposureEvidenceClass,
    ExposureMeasureDefinition,
    ExposureRelationshipStrength,
    ExposureScenarioDefinition,
    ExposureScenarioRun,
    ExposureScenarioShock,
    ExposureType,
    UncertaintyClass,
)
from atlas.exposure.errors import (
    CurrencyMismatchError,
    CycleDetectedError,
    DoubleCountingError,
    ExposureDomainError,
    IncompatiblePeriodError,
    InvalidDenominatorError,
    LookAheadViolationError,
    MethodNotAllowedError,
    MissingCurrencyRateError,
    ProhibitedInferenceError,
    SourceLicenseRevokedError,
    TenantExposureAccessDeniedError,
)
from atlas.exposure.measures.definitions import MEASURE_REGISTRY, get_measure_definition
from atlas.exposure.service import AtlasExposureEngineService

__all__ = [
    # Domain Models
    "AnalysisRunStatus",
    "AtlasExposureResult",
    "ConsolidationBasis",
    "CountryExposureBasis",
    "CoverageStatus",
    "ExposureAnalysisRun",
    "ExposureCoverageSummary",
    "ExposureDomain",
    "ExposureEvidenceClass",
    "ExposureMeasureDefinition",
    "ExposureRelationshipStrength",
    "ExposureScenarioDefinition",
    "ExposureScenarioRun",
    "ExposureScenarioShock",
    "ExposureType",
    "UncertaintyClass",
    # Errors
    "CurrencyMismatchError",
    "CycleDetectedError",
    "DoubleCountingError",
    "ExposureDomainError",
    "IncompatiblePeriodError",
    "InvalidDenominatorError",
    "LookAheadViolationError",
    "MethodNotAllowedError",
    "MissingCurrencyRateError",
    "ProhibitedInferenceError",
    "SourceLicenseRevokedError",
    "TenantExposureAccessDeniedError",
    # Measures & Service
    "MEASURE_REGISTRY",
    "get_measure_definition",
    "AtlasExposureEngineService",
]
