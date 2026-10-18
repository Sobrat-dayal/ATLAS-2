"""ATLAS Technical Indicator Infrastructure (Stage 69).

Provides:
- Allowlisted IndicatorRegistry and IndicatorDefinition models.
- Parameter validation with strict bounds.
- Deterministic calculation engine with Decimal precision.
- Reference Simple Moving Average (atlas.sma) calculator.
- TechnicalIndicatorService and FastAPI router.
"""

from .calculators import IndicatorCalculator, SmaCalculator
from .models import (
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    IndicatorCalculationResult,
    IndicatorCatalogResponse,
    IndicatorCategory,
    IndicatorDefinition,
    IndicatorInstanceConfig,
    IndicatorOutputSeries,
    IndicatorParameterDefinition,
    IndicatorParameterType,
    IndicatorPoint,
    IndicatorRenderingTarget,
    IndicatorStatus,
)
from .registry import IndicatorRegistry, default_indicator_registry
from .router import router as indicator_router
from .service import TechnicalIndicatorService
from .talib_adapter import TALibCapability, TALibIndicatorCalculator

__all__ = [
    "IndicatorCalculator",
    "SmaCalculator",
    "TALibCapability",
    "TALibIndicatorCalculator",
    "IndicatorCategory",
    "IndicatorCalculationRequest",
    "IndicatorCalculationResponse",
    "IndicatorCalculationResult",
    "IndicatorCatalogResponse",
    "IndicatorDefinition",
    "IndicatorInstanceConfig",
    "IndicatorOutputSeries",
    "IndicatorParameterDefinition",
    "IndicatorParameterType",
    "IndicatorPoint",
    "IndicatorRenderingTarget",
    "IndicatorStatus",
    "IndicatorRegistry",
    "default_indicator_registry",
    "TechnicalIndicatorService",
    "indicator_router",
]
