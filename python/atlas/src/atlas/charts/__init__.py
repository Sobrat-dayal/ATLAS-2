"""ATLAS Charts V1 Module (Stage 66).

Provides the foundational institutional financial charting engine, historical OHLCV
retrieval, baseline interval policies, and canonical instrument discovery.
"""

from .aggregation import aggregate_ohlcv, get_interval_duration_seconds
from .config import (
    BASELINE_INTERVAL_CODE,
    CANONICAL_CHART_INSTRUMENT_BY_ID,
    CANONICAL_CHART_INSTRUMENT_MAP,
    CANONICAL_INTERVAL_ORDER,
    DEFAULT_BARS_LIMIT,
    DEFAULT_CANONICAL_CHART_INSTRUMENTS,
    INTERVAL_DISPLAY_LABELS,
    MAX_BARS_LIMIT,
    MIN_BARS_LIMIT,
    ChartAdjustmentBasis,
    ChartConnectionState,
    ChartDisplayState,
    ChartInterval,
    ChartIntervalAvailability,
    ChartLiveCapability,
    ChartMarketDataFreshness,
    ChartPriceBasis,
    ChartRenderMode,
    gen_chart_instrument_id,
)
from .live_service import LiveChartService
from .models import (
    ChartBarDTO,
    ChartCoverageDTO,
    ChartHistoryResponse,
    ChartInstrumentMetadata,
    ChartIntervalOptionDTO,
    ChartIntervalsResponse,
    ChartLiveStateResponse,
    ChartPaginationDTO,
    ChartSearchResponse,
    LiveQuoteDTO,
)
from .repository import HistoricalChartRepository
from .router import router
from .service import HistoricalChartService

__all__ = [
    "BASELINE_INTERVAL_CODE",
    "CANONICAL_CHART_INSTRUMENT_BY_ID",
    "CANONICAL_CHART_INSTRUMENT_MAP",
    "CANONICAL_INTERVAL_ORDER",
    "ChartAdjustmentBasis",
    "ChartBarDTO",
    "ChartConnectionState",
    "ChartCoverageDTO",
    "ChartDisplayState",
    "ChartHistoryResponse",
    "ChartInstrumentMetadata",
    "ChartInterval",
    "ChartIntervalAvailability",
    "ChartIntervalOptionDTO",
    "ChartIntervalsResponse",
    "ChartLiveCapability",
    "ChartLiveStateResponse",
    "ChartMarketDataFreshness",
    "ChartPaginationDTO",
    "ChartPriceBasis",
    "ChartRenderMode",
    "ChartSearchResponse",
    "DEFAULT_BARS_LIMIT",
    "DEFAULT_CANONICAL_CHART_INSTRUMENTS",
    "HistoricalChartRepository",
    "HistoricalChartService",
    "INTERVAL_DISPLAY_LABELS",
    "LiveChartService",
    "LiveQuoteDTO",
    "MAX_BARS_LIMIT",
    "MIN_BARS_LIMIT",
    "aggregate_ohlcv",
    "gen_chart_instrument_id",
    "get_interval_duration_seconds",
    "router",
]
