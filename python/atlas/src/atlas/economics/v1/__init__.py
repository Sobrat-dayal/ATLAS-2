"""Atlas Economics V1 Domain Package (Stage 89)."""

from .enums import (
    GeographicScopeKind,
    IndicatorCategory,
    ObservationStatus,
    PriceBasisKind,
    ReportingFrequency,
    SeasonalAdjustmentKind,
    StatisticalUnit,
    TransformationType,
)
from .errors import (
    EconomicCalculationError,
    EconomicGeographyNotFoundError,
    EconomicIndicatorNotFoundError,
    EconomicPeriodInvalidError,
    EconomicSeriesNotFoundError,
    EconomicsV1Error,
    EconomicTransformationUnsupportedError,
)
from .models import (
    EconomicGeography,
    EconomicIndicator,
    EconomicObservationRecord,
    EconomicSeries,
    EconomicVintageRecord,
    MajorEconomyMacroSummary,
    TransformationDefinition,
)
from .repository import EconomicsV1Repository
from .schemas import (
    EconomicCoverageResponseDTO,
    EconomicGeographyDTO,
    EconomicIndicatorDTO,
    EconomicObservationDTO,
    EconomicSeriesDTO,
    EconomicSeriesObservationsResponseDTO,
    EconomicVintageDTO,
    GlobalMacroOverviewResponseDTO,
    MajorEconomyMacroSummaryDTO,
    TransformationDefinitionDTO,
)
from .service import EconomicsV1Service
from .transformations import SUPPORTED_TRANSFORMATIONS, apply_transformation

__all__ = [
    # Enums
    "IndicatorCategory",
    "StatisticalUnit",
    "ReportingFrequency",
    "SeasonalAdjustmentKind",
    "PriceBasisKind",
    "ObservationStatus",
    "TransformationType",
    "GeographicScopeKind",
    # Errors
    "EconomicsV1Error",
    "EconomicIndicatorNotFoundError",
    "EconomicSeriesNotFoundError",
    "EconomicGeographyNotFoundError",
    "EconomicTransformationUnsupportedError",
    "EconomicPeriodInvalidError",
    "EconomicCalculationError",
    # Models
    "EconomicGeography",
    "EconomicIndicator",
    "EconomicSeries",
    "EconomicObservationRecord",
    "EconomicVintageRecord",
    "MajorEconomyMacroSummary",
    "TransformationDefinition",
    # Repository & Service
    "EconomicsV1Repository",
    "EconomicsV1Service",
    # Schemas
    "EconomicGeographyDTO",
    "EconomicIndicatorDTO",
    "EconomicSeriesDTO",
    "EconomicObservationDTO",
    "EconomicVintageDTO",
    "TransformationDefinitionDTO",
    "MajorEconomyMacroSummaryDTO",
    "GlobalMacroOverviewResponseDTO",
    "EconomicSeriesObservationsResponseDTO",
    "EconomicCoverageResponseDTO",
    # Transformations
    "SUPPORTED_TRANSFORMATIONS",
    "apply_transformation",
]
