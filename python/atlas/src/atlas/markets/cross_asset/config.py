"""Canonical Configuration for ATLAS Cross-Asset Markets V1 (Stage 65).

Defines cross-asset universes, asset classes, analytical modes, comparison windows,
alignment policies, proxy categories, and typed exclusion taxonomy.
"""

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field


class CrossAssetMode(str, Enum):
    """Analytical comparison mode for cross-asset workspace."""

    NATIVE_OVERVIEW = "native_overview"
    ALIGNED_PERFORMANCE = "aligned_performance"


class CrossAssetWindow(str, Enum):
    """Supported standardized observation comparison windows."""

    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"


class AssetClassEnum(str, Enum):
    """Financial market asset class classification."""

    EQUITIES = "equities"
    ETFS = "etfs"
    FX = "fx"
    CRYPTO = "crypto"
    BONDS = "bonds"
    FUTURES = "futures"


class NativeMetricKind(str, Enum):
    """Asset-class-specific native financial measurement semantics."""

    EQUITY_PRICE_CHANGE = "EQUITY_PRICE_CHANGE"
    ETF_MARKET_PRICE_CHANGE = "ETF_MARKET_PRICE_CHANGE"
    FX_SPOT_RATE_CHANGE = "FX_SPOT_RATE_CHANGE"
    CRYPTO_SPOT_24H_CHANGE = "CRYPTO_SPOT_24H_CHANGE"
    BOND_YIELD_BPS_CHANGE = "BOND_YIELD_BPS_CHANGE"
    FUTURES_SETTLEMENT_CHANGE = "FUTURES_SETTLEMENT_CHANGE"


class ProxyKind(str, Enum):
    """Distinction between an underlying benchmark index and a proxy instrument."""

    NONE = "none"
    ETF_PROXY = "ETF Proxy"
    FUTURES_PROXY = "Futures Proxy"
    BENCHMARK_INDEX = "Benchmark Index"


class CrossAssetExclusionReason(str, Enum):
    """Typed exclusion taxonomy for why an instrument cannot participate in aligned comparison."""

    NO_CURRENT_OBSERVATION = "NO_CURRENT_OBSERVATION"
    NO_START_REFERENCE = "NO_START_REFERENCE"
    NO_END_REFERENCE = "NO_END_REFERENCE"
    STALE_OBSERVATION = "STALE_OBSERVATION"
    UNKNOWN_FRESHNESS = "UNKNOWN_FRESHNESS"
    WINDOW_MISALIGNED = "WINDOW_MISALIGNED"
    INCOMPATIBLE_PRICE_BASIS = "INCOMPATIBLE_PRICE_BASIS"
    INCOMPATIBLE_CURRENCY = "INCOMPATIBLE_CURRENCY"
    INCOMPATIBLE_QUOTE_UNIT = "INCOMPATIBLE_QUOTE_UNIT"
    INCOMPATIBLE_SERIES = "INCOMPATIBLE_SERIES"
    UNVERIFIED_ADJUSTMENT = "UNVERIFIED_ADJUSTMENT"
    INVALID_DENOMINATOR = "INVALID_DENOMINATOR"
    NEGATIVE_REFERENCE_UNSUPPORTED = "NEGATIVE_REFERENCE_UNSUPPORTED"
    NO_OVERLAPPING_HISTORY = "NO_OVERLAPPING_HISTORY"
    MARKET_CLOSED = "MARKET_CLOSED"
    UNSUPPORTED_METRIC = "UNSUPPORTED_METRIC"
    INSTRUMENT_EXPIRED = "INSTRUMENT_EXPIRED"
    NOT_ENTITLED = "NOT_ENTITLED"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    OTHER = "OTHER"


class CrossAssetCoverageStatus(str, Enum):
    """Institutional evaluation status of cross-asset universe coverage."""

    COMPLETE_FOR_DEFINED_SET = "COMPLETE_FOR_DEFINED_SET"
    PARTIAL = "PARTIAL"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"


class CrossAssetUniverseDefinition(BaseModel):
    """Metadata record for a canonical multi-asset comparison universe."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    universe_id: str = Field(..., min_length=3, max_length=64)
    display_name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., max_length=512)
    asset_classes: List[AssetClassEnum]
    member_count: int = Field(..., ge=1)
    default_symbols: List[str]


# ---------------------------------------------------------------------------
# Standard Alignment Policies
# ---------------------------------------------------------------------------
DEFAULT_ALIGNMENT_TOLERANCE_SECONDS: int = 7200  # 2 hours tolerance for intraday boundary
MAX_SELECTION_COUNT: int = 12  # Server-side bounded comparison limit
DEFAULT_CURRENCY_POLICY: str = "LOCAL_QUOTE_CURRENCY_PRICE_RETURN"

WINDOW_DURATIONS_HOURS: Dict[CrossAssetWindow, int] = {
    CrossAssetWindow.LAST_24H: 24,
    CrossAssetWindow.LAST_7D: 168,
    CrossAssetWindow.LAST_30D: 720,
}

# ---------------------------------------------------------------------------
# Predefined Multi-Asset Canonical Universes
# ---------------------------------------------------------------------------
SUPPORTED_CROSS_ASSET_UNIVERSES: List[CrossAssetUniverseDefinition] = [
    CrossAssetUniverseDefinition(
        universe_id="univ_cross_asset_macro",
        display_name="Global Macro Cross-Asset Universe",
        description=(
            "Comprehensive cross-market view spanning equities (AAPL), ETF proxy (SPY), "
            "FX (EUR/USD, USD/JPY), crypto (BTC, ETH), sovereign debt (US 10Y), and "
            "commodities futures (Crude Oil, Gold)."
        ),
        asset_classes=[
            AssetClassEnum.EQUITIES,
            AssetClassEnum.ETFS,
            AssetClassEnum.FX,
            AssetClassEnum.CRYPTO,
            AssetClassEnum.BONDS,
            AssetClassEnum.FUTURES,
        ],
        member_count=9,
        default_symbols=[
            "SPY",
            "AAPL",
            "EURUSD",
            "USDJPY",
            "BTCUSDT",
            "ETHUSDT",
            "US10Y",
            "CLZ26",
            "GCZ26",
        ],
    ),
    CrossAssetUniverseDefinition(
        universe_id="univ_cross_asset_us_liquidity",
        display_name="US Dollar & Rates Liquidity Universe",
        description=(
            "US market liquidity and financial conditions monitor: S&P 500 ETF proxy (SPY), "
            "Nasdaq 100 ETF proxy (QQQ), key FX pairs, benchmark Treasury yield, and Gold futures."
        ),
        asset_classes=[
            AssetClassEnum.ETFS,
            AssetClassEnum.FX,
            AssetClassEnum.BONDS,
            AssetClassEnum.FUTURES,
        ],
        member_count=6,
        default_symbols=["SPY", "QQQ", "EURUSD", "USDJPY", "US10Y", "GCZ26"],
    ),
    CrossAssetUniverseDefinition(
        universe_id="univ_cross_asset_commodities_fx",
        display_name="Commodities, FX & Inflation Universe",
        description=(
            "Global inflation and resource cross-market monitor: Crude Oil (CLZ26), "
            "Gold (GCZ26), E-mini S&P (ESZ26), FX pairs (EUR/USD, USD/JPY), and "
            "Digital Gold (BTC/USDT)."
        ),
        asset_classes=[
            AssetClassEnum.FUTURES,
            AssetClassEnum.FX,
            AssetClassEnum.CRYPTO,
            AssetClassEnum.BONDS,
        ],
        member_count=6,
        default_symbols=["CLZ26", "GCZ26", "ESZ26", "EURUSD", "USDJPY", "BTCUSDT"],
    ),
]
