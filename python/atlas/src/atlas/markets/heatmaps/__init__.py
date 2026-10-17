"""ATLAS Market Heatmaps V1 (Stage 64).

Provides institutional-quality market heatmaps, sector/industry treemaps,
market-capitalization weighting, equal-size performance visualization,
and coverage transparency.
"""

from .config import (
    HEATMAP_UNIVERSES_BY_ID,
    SUPPORTED_HEATMAP_UNIVERSES,
    HeatmapComparisonWindow,
    HeatmapCoverageStatus,
    HeatmapExclusionReason,
    HeatmapHierarchyMode,
    HeatmapUniverseDefinition,
    HeatmapVisualizationMode,
)
from .models import (
    HeatmapCoverage,
    HeatmapGroupNode,
    HeatmapLeafNode,
    HeatmapOptionsResponse,
    HeatmapUniverseResponse,
    MarketHeatmapResponse,
)
from .repository import HeatmapCandidateObservation, MarketHeatmapRepository
from .router import router
from .service import MarketHeatmapService

__all__ = [
    "HEATMAP_UNIVERSES_BY_ID",
    "SUPPORTED_HEATMAP_UNIVERSES",
    "HeatmapCandidateObservation",
    "HeatmapComparisonWindow",
    "HeatmapCoverage",
    "HeatmapCoverageStatus",
    "HeatmapExclusionReason",
    "HeatmapGroupNode",
    "HeatmapHierarchyMode",
    "HeatmapLeafNode",
    "HeatmapOptionsResponse",
    "HeatmapUniverseDefinition",
    "HeatmapUniverseResponse",
    "HeatmapVisualizationMode",
    "MarketHeatmapRepository",
    "MarketHeatmapResponse",
    "MarketHeatmapService",
    "router",
]
