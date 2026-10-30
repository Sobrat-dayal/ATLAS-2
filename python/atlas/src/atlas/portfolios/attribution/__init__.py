"""ATLAS Portfolios V1 — Performance Attribution Package (Stage 113).

Exports canonical Brinson attribution, security contribution, currency decomposition,
multi-period linking, and mathematical reconciliation facilities.
"""

from atlas.portfolios.attribution.benchmark import (
    BenchmarkCompositionEngine,
    BenchmarkConstituentRecord,
    BenchmarkPointInTimeSnapshot,
    BenchmarkSectorSnapshot,
)
from atlas.portfolios.attribution.brinson import BrinsonEngine
from atlas.portfolios.attribution.contributions import SecurityContributionEngine
from atlas.portfolios.attribution.currency import CurrencyAttributionEngine
from atlas.portfolios.attribution.enums import (
    AttributionCompleteness,
    AttributionDimension,
    AttributionMethod,
    MultiPeriodLinkingMethod,
    ReconciliationStatus,
)
from atlas.portfolios.attribution.errors import (
    PortfolioAttributionAccessDeniedError,
    PortfolioAttributionBenchmarkConstituentsMissingError,
    PortfolioAttributionBenchmarkNotFoundError,
    PortfolioAttributionClassificationMissingError,
    PortfolioAttributionCurrencyMismatchError,
    PortfolioAttributionError,
    PortfolioAttributionMethodUnsupportedError,
    PortfolioAttributionMultiPeriodLinkingError,
    PortfolioAttributionNotFoundError,
    PortfolioAttributionPeriodInvalidError,
    PortfolioAttributionReconciliationFailedError,
)
from atlas.portfolios.attribution.linking import MultiPeriodLinkingEngine
from atlas.portfolios.attribution.models import (
    AttributionCategoryResult,
    AttributionDataQuality,
    AttributionReconciliation,
    CurrencyEffectItem,
    HistoricalPeriodAttribution,
    MultiPeriodLinkedAttribution,
    PortfolioAttributionRun,
    SecurityContributionItem,
)
from atlas.portfolios.attribution.reconciliation import AttributionReconciliationEngine
from atlas.portfolios.attribution.schemas import (
    AttributionBenchmarkSummaryResponse,
    AttributionCategoryResponse,
    AttributionDataQualityResponse,
    AttributionReconciliationResponse,
    AttributionRunsListResponse,
    CalculateAttributionRequest,
    CurrencyEffectResponse,
    HistoricalPeriodResponse,
    MultiPeriodLinkedResponse,
    PortfolioAttributionRunResponse,
    SecurityContributionResponse,
)
from atlas.portfolios.attribution.service import PortfolioAttributionService

__all__ = [
    "AttributionCompleteness",
    "AttributionDimension",
    "AttributionMethod",
    "MultiPeriodLinkingMethod",
    "ReconciliationStatus",
    "PortfolioAttributionError",
    "PortfolioAttributionNotFoundError",
    "PortfolioAttributionAccessDeniedError",
    "PortfolioAttributionBenchmarkNotFoundError",
    "PortfolioAttributionBenchmarkConstituentsMissingError",
    "PortfolioAttributionPeriodInvalidError",
    "PortfolioAttributionCurrencyMismatchError",
    "PortfolioAttributionClassificationMissingError",
    "PortfolioAttributionMethodUnsupportedError",
    "PortfolioAttributionReconciliationFailedError",
    "PortfolioAttributionMultiPeriodLinkingError",
    "BenchmarkCompositionEngine",
    "BenchmarkConstituentRecord",
    "BenchmarkSectorSnapshot",
    "BenchmarkPointInTimeSnapshot",
    "BrinsonEngine",
    "SecurityContributionEngine",
    "CurrencyAttributionEngine",
    "MultiPeriodLinkingEngine",
    "AttributionReconciliationEngine",
    "AttributionCategoryResult",
    "SecurityContributionItem",
    "CurrencyEffectItem",
    "HistoricalPeriodAttribution",
    "MultiPeriodLinkedAttribution",
    "AttributionReconciliation",
    "AttributionDataQuality",
    "PortfolioAttributionRun",
    "CalculateAttributionRequest",
    "AttributionCategoryResponse",
    "SecurityContributionResponse",
    "CurrencyEffectResponse",
    "HistoricalPeriodResponse",
    "MultiPeriodLinkedResponse",
    "AttributionReconciliationResponse",
    "AttributionDataQualityResponse",
    "PortfolioAttributionRunResponse",
    "AttributionBenchmarkSummaryResponse",
    "AttributionRunsListResponse",
    "PortfolioAttributionService",
]

