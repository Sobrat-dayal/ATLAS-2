"""Configuration, Universe Definitions, and Hierarchy Policies for
ATLAS Market Heatmaps V1 (Stage 64).

Defines canonical heatmap universes, visualization modes (Equal-Size vs Market-Cap Weighted),
hierarchy grouping policies, color domain limits, and exclusion reasons according to institutional
market visualization and mathematical integrity standards.
"""

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class HeatmapVisualizationMode(str, Enum):
    """Supported heatmap visualization modes."""

    EQUAL_SIZE = "equal_size"
    MARKET_CAP_WEIGHTED = "market_cap_weighted"


class HeatmapHierarchyMode(str, Enum):
    """Supported hierarchy grouping modes."""

    NONE = "none"
    SECTOR = "sector"
    INDUSTRY = "industry"


class HeatmapComparisonWindow(str, Enum):
    """Qualified market comparison windows."""

    PREVIOUS_REGULAR_SESSION = "previous_regular_session"
    ROLLING_24H = "rolling_24h"
    PREVIOUS_SESSION_SETTLEMENT = "previous_session_settlement"


class HeatmapExclusionReason(str, Enum):
    """Institutional exclusion reasons explaining why an instrument cannot be visualized."""

    NO_CURRENT_QUOTE = "NO_CURRENT_QUOTE"
    NO_REFERENCE = "NO_REFERENCE"
    MISSING_WEIGHT = "MISSING_WEIGHT"
    INVALID_WEIGHT = "INVALID_WEIGHT"
    STALE_OBSERVATION = "STALE_OBSERVATION"
    INCOMPATIBLE_WINDOW = "INCOMPATIBLE_WINDOW"
    INVALID_DENOMINATOR = "INVALID_DENOMINATOR"
    INACTIVE_SECURITY = "INACTIVE_SECURITY"
    NOT_ENTITLED = "NOT_ENTITLED"
    DATA_SOURCE_UNAVAILABLE = "DATA_SOURCE_UNAVAILABLE"


class HeatmapCoverageStatus(str, Enum):
    """Coverage completeness status for the defined universe."""

    COMPLETE_FOR_DEFINED_UNIVERSE = "COMPLETE_FOR_DEFINED_UNIVERSE"
    PARTIAL_COVERAGE = "PARTIAL_COVERAGE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


# ---------------------------------------------------------------------------
# Sector and Industry Taxonomies (GICS Standard)
# ---------------------------------------------------------------------------
GICS_SECTORS: List[str] = [
    "Technology",
    "Consumer Cyclical",
    "Communication Services",
    "Financial Services",
    "Healthcare",
    "Energy",
    "Industrials",
    "Consumer Defensive",
    "Utilities",
    "Real Estate",
    "Basic Materials",
    "Unclassified",
]


# ---------------------------------------------------------------------------
# Universe Definition Model
# ---------------------------------------------------------------------------
class HeatmapUniverseDefinition(BaseModel):
    """Specification of an authoritative, authorized heatmap candidate universe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    universe_id: str = Field(..., min_length=2, max_length=64)
    display_name: str = Field(..., min_length=2, max_length=128)
    asset_class: str = Field(..., description="equity, crypto, futures, fx, bond")
    market_scope: str
    exchange_scope: List[str]
    supported_modes: List[HeatmapVisualizationMode]
    supported_hierarchies: List[HeatmapHierarchyMode]
    supported_windows: List[HeatmapComparisonWindow]
    default_window: HeatmapComparisonWindow
    default_mode: HeatmapVisualizationMode
    default_hierarchy: HeatmapHierarchyMode
    weight_metric_label: Optional[str] = None
    weight_unit: Optional[str] = None
    taxonomy: Optional[str] = None
    is_active: bool = True


# ---------------------------------------------------------------------------
# Authoritative Supported Universes
# ---------------------------------------------------------------------------
SUPPORTED_HEATMAP_UNIVERSES: List[HeatmapUniverseDefinition] = [
    HeatmapUniverseDefinition(
        universe_id="univ_us_equities",
        display_name="Covered US Equities",
        asset_class="equity",
        market_scope="US",
        exchange_scope=["XNAS", "XNYS"],
        supported_modes=[
            HeatmapVisualizationMode.EQUAL_SIZE,
            HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
        ],
        supported_hierarchies=[
            HeatmapHierarchyMode.NONE,
            HeatmapHierarchyMode.SECTOR,
            HeatmapHierarchyMode.INDUSTRY,
        ],
        supported_windows=[HeatmapComparisonWindow.PREVIOUS_REGULAR_SESSION],
        default_window=HeatmapComparisonWindow.PREVIOUS_REGULAR_SESSION,
        default_mode=HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
        default_hierarchy=HeatmapHierarchyMode.SECTOR,
        weight_metric_label="Market Capitalization",
        weight_unit="USD",
        taxonomy="GICS",
        is_active=True,
    ),
    HeatmapUniverseDefinition(
        universe_id="univ_crypto_spot",
        display_name="Covered Cryptocurrency Spot",
        asset_class="crypto",
        market_scope="GLOBAL",
        exchange_scope=["BINANCE"],
        supported_modes=[
            HeatmapVisualizationMode.EQUAL_SIZE,
            HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
        ],
        supported_hierarchies=[HeatmapHierarchyMode.NONE],
        supported_windows=[HeatmapComparisonWindow.ROLLING_24H],
        default_window=HeatmapComparisonWindow.ROLLING_24H,
        default_mode=HeatmapVisualizationMode.MARKET_CAP_WEIGHTED,
        default_hierarchy=HeatmapHierarchyMode.NONE,
        weight_metric_label="Circulating Market Cap",
        weight_unit="USDT",
        taxonomy=None,
        is_active=True,
    ),
    HeatmapUniverseDefinition(
        universe_id="univ_futures",
        display_name="Exchange-Traded Futures",
        asset_class="futures",
        market_scope="US",
        exchange_scope=["NYMEX", "COMEX", "CME", "CBOT"],
        supported_modes=[HeatmapVisualizationMode.EQUAL_SIZE],  # No fake market cap on futures
        supported_hierarchies=[HeatmapHierarchyMode.NONE, HeatmapHierarchyMode.SECTOR],
        supported_windows=[HeatmapComparisonWindow.PREVIOUS_SESSION_SETTLEMENT],
        default_window=HeatmapComparisonWindow.PREVIOUS_SESSION_SETTLEMENT,
        default_mode=HeatmapVisualizationMode.EQUAL_SIZE,
        default_hierarchy=HeatmapHierarchyMode.SECTOR,
        weight_metric_label=None,
        weight_unit=None,
        taxonomy="Commodity Class",
        is_active=True,
    ),
]

HEATMAP_UNIVERSES_BY_ID: Dict[str, HeatmapUniverseDefinition] = {
    u.universe_id: u for u in SUPPORTED_HEATMAP_UNIVERSES
}
