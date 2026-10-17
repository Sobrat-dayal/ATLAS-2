"""Configuration and domain constants for ATLAS Charts V1 (Stage 66).

Defines the verified baseline interval, quotation conventions, pagination limits,
supported chart rendering modes, and canonical chartable instrument definitions.
"""

from enum import StrEnum
from typing import Dict, List
from uuid import UUID, uuid5

# Deterministic namespace for Charts V1 canonical financial instruments
CHARTS_NAMESPACE = UUID("66666666-6666-5666-a666-000000000001")


def gen_chart_instrument_id(symbol: str) -> UUID:
    """Generate deterministic UUID for chartable canonical instruments."""
    return uuid5(CHARTS_NAMESPACE, f"chart-instrument:{symbol.upper()}")


class ChartInterval(StrEnum):
    """Supported canonical intervals for ATLAS Charts (Stage 68)."""

    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class ChartRenderMode(StrEnum):
    """Foundational and expanded chart visualization modes for Stage 68."""

    CANDLESTICK = "candlestick"
    BAR = "bar"
    LINE = "line"
    AREA = "area"


class ChartIntervalAvailability(StrEnum):
    """Availability classification of an interval for a canonical series."""

    AVAILABLE_NATIVE = "AVAILABLE_NATIVE"
    AVAILABLE_DERIVED = "AVAILABLE_DERIVED"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class ChartPriceBasis(StrEnum):
    """Authoritative price quotation basis."""

    TRADE_PRICE = "trade_price"
    MIDPOINT = "midpoint"
    CLEAN_PRICE = "clean_price"
    DIRTY_PRICE = "dirty_price"
    SETTLEMENT = "settlement"


class ChartAdjustmentBasis(StrEnum):
    """Historical bar adjustment policy."""

    SPLIT_ADJUSTED = "split_adjusted"
    RAW = "raw"
    TOTAL_RETURN = "total_return"
    UNADJUSTED = "unadjusted"


# Bounded pagination constraints for historical queries
DEFAULT_BARS_LIMIT = 300
MAX_BARS_LIMIT = 2000
MIN_BARS_LIMIT = 10

# Baseline interval definition
BASELINE_INTERVAL_CODE = ChartInterval.ONE_DAY.value

# Canonical list of ordered intervals presented in the interface
CANONICAL_INTERVAL_ORDER = [
    ChartInterval.ONE_MINUTE.value,
    ChartInterval.FIVE_MINUTES.value,
    ChartInterval.FIFTEEN_MINUTES.value,
    ChartInterval.THIRTY_MINUTES.value,
    ChartInterval.ONE_HOUR.value,
    ChartInterval.FOUR_HOURS.value,
    ChartInterval.ONE_DAY.value,
    ChartInterval.ONE_WEEK.value,
    ChartInterval.ONE_MONTH.value,
]

INTERVAL_DISPLAY_LABELS: Dict[str, str] = {
    ChartInterval.ONE_MINUTE.value: "1m",
    ChartInterval.FIVE_MINUTES.value: "5m",
    ChartInterval.FIFTEEN_MINUTES.value: "15m",
    ChartInterval.THIRTY_MINUTES.value: "30m",
    ChartInterval.ONE_HOUR.value: "1h",
    ChartInterval.FOUR_HOURS.value: "4h",
    ChartInterval.ONE_DAY.value: "1D",
    ChartInterval.ONE_WEEK.value: "1W",
    ChartInterval.ONE_MONTH.value: "1M",
}


# ============================================================================
# Stage 67 Live Chart Streaming Enums & Invariants
# ============================================================================


class ChartConnectionState(StrEnum):
    """Transport-layer connection states for the live chart streaming client."""

    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


class ChartMarketDataFreshness(StrEnum):
    """Market-data freshness and delay classification (Stage 44 integration)."""

    LIVE = "LIVE"
    DELAYED = "DELAYED"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
    UNAVAILABLE = "UNAVAILABLE"


class ChartLiveCapability(StrEnum):
    """Supported live charting capabilities for the selected instrument."""

    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    LIVE_PRICE_AVAILABLE = "LIVE_PRICE_AVAILABLE"
    LIVE_BAR_AVAILABLE = "LIVE_BAR_AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"


class ChartDisplayState(StrEnum):
    """Chart workspace presentation state combining live stream and viewport controls."""

    HISTORICAL_ONLY = "HISTORICAL_ONLY"
    LIVE_PRICE_AVAILABLE = "LIVE_PRICE_AVAILABLE"
    LIVE_BAR_AVAILABLE = "LIVE_BAR_AVAILABLE"
    PAUSED = "PAUSED"
    RECONCILING = "RECONCILING"


# Stage 67 live stream buffers and timing parameters
DEFAULT_LIVE_FRESH_SECONDS = 60
DEFAULT_LIVE_STALE_SECONDS = 300
DEFAULT_COALESCE_INTERVAL_MS = 100
MAX_BOOTSTRAP_BUFFER_SIZE = 100


class CanonicalChartInstrumentConfig:
    """Configuration record for a canonical chartable financial instrument."""

    def __init__(
        self,
        symbol: str,
        display_name: str,
        asset_class: str,
        market_or_venue: str,
        price_currency: str,
        quotation_unit: str,
        price_basis: ChartPriceBasis,
        adjustment_basis: ChartAdjustmentBasis,
        provider_key: str,
        has_volume: bool = True,
        is_futures: bool = False,
        allows_negative_price: bool = False,
        contract_expiration: str | None = None,
        base_asset: str | None = None,
        quote_asset: str | None = None,
        supported_native_intervals: List[str] | None = None,
        supported_derived_intervals: List[str] | None = None,
        unsupported_intervals_reasons: Dict[str, str] | None = None,
    ):
        self.symbol = symbol.upper()
        self.entity_id = gen_chart_instrument_id(symbol)
        self.display_name = display_name
        self.asset_class = asset_class
        self.market_or_venue = market_or_venue
        self.price_currency = price_currency
        self.quotation_unit = quotation_unit
        self.price_basis = price_basis
        self.adjustment_basis = adjustment_basis
        self.provider_key = provider_key
        self.has_volume = has_volume
        self.is_futures = is_futures
        self.allows_negative_price = allows_negative_price
        self.contract_expiration = contract_expiration
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.supported_native_intervals = supported_native_intervals or ["1d"]
        self.supported_derived_intervals = supported_derived_intervals or ["1w", "1M"]
        self.unsupported_intervals_reasons = unsupported_intervals_reasons or {}

    def get_supported_intervals(self) -> List[str]:
        """Returns ordered list of all supported intervals (both native and derived)."""
        combined = set(self.supported_native_intervals + self.supported_derived_intervals)
        return [i for i in CANONICAL_INTERVAL_ORDER if i in combined]


# Verified catalog of canonical chartable instruments across financial asset classes
DEFAULT_CANONICAL_CHART_INSTRUMENTS: List[CanonicalChartInstrumentConfig] = [
    # Equities (High liquidity supports native intraday 1m-1d; derived 1w, 1M)
    CanonicalChartInstrumentConfig(
        symbol="AAPL",
        display_name="Apple Inc.",
        asset_class="equities",
        market_or_venue="NASDAQ",
        price_currency="USD",
        quotation_unit="USD/share",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.SPLIT_ADJUSTED,
        provider_key="OPENBB_POLYGON",
        has_volume=True,
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    CanonicalChartInstrumentConfig(
        symbol="MSFT",
        display_name="Microsoft Corporation",
        asset_class="equities",
        market_or_venue="NASDAQ",
        price_currency="USD",
        quotation_unit="USD/share",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.SPLIT_ADJUSTED,
        provider_key="OPENBB_POLYGON",
        has_volume=True,
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    CanonicalChartInstrumentConfig(
        symbol="NVDA",
        display_name="NVIDIA Corporation",
        asset_class="equities",
        market_or_venue="NASDAQ",
        price_currency="USD",
        quotation_unit="USD/share",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.SPLIT_ADJUSTED,
        provider_key="OPENBB_POLYGON",
        has_volume=True,
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    # ETFs
    CanonicalChartInstrumentConfig(
        symbol="SPY",
        display_name="SPDR S&P 500 ETF Trust",
        asset_class="etfs",
        market_or_venue="NYSE Arca",
        price_currency="USD",
        quotation_unit="USD/share",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.SPLIT_ADJUSTED,
        provider_key="OPENBB_POLYGON",
        has_volume=True,
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    CanonicalChartInstrumentConfig(
        symbol="QQQ",
        display_name="Invesco QQQ Trust Series 1",
        asset_class="etfs",
        market_or_venue="NASDAQ",
        price_currency="USD",
        quotation_unit="USD/share",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.SPLIT_ADJUSTED,
        provider_key="OPENBB_POLYGON",
        has_volume=True,
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    # Foreign Exchange (OTC FX - volume is explicitly None, 1m is license-restricted)
    CanonicalChartInstrumentConfig(
        symbol="EURUSD",
        display_name="Euro / US Dollar Spot",
        asset_class="fx",
        market_or_venue="Interbank FX",
        price_currency="USD",
        quotation_unit="USD per EUR",
        price_basis=ChartPriceBasis.MIDPOINT,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="CANONICAL_FX_FEED",
        has_volume=False,
        supported_native_intervals=["5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "Intraday 1-minute OTC interbank feed is restricted by license."
        },
    ),
    CanonicalChartInstrumentConfig(
        symbol="USDJPY",
        display_name="US Dollar / Japanese Yen Spot",
        asset_class="fx",
        market_or_venue="Interbank FX",
        price_currency="JPY",
        quotation_unit="JPY per USD",
        price_basis=ChartPriceBasis.MIDPOINT,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="CANONICAL_FX_FEED",
        has_volume=False,
        supported_native_intervals=["5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "Intraday 1-minute OTC interbank feed is restricted by license."
        },
    ),
    # Cryptocurrency Spot (24/7 continuous trading, supports all native and derived intervals)
    CanonicalChartInstrumentConfig(
        symbol="BTCUSDT",
        display_name="Bitcoin / Tether Spot",
        asset_class="crypto",
        market_or_venue="Binance Spot",
        price_currency="USDT",
        quotation_unit="USDT per BTC",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="BINANCE_REST",
        has_volume=True,
        base_asset="BTC",
        quote_asset="USDT",
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    CanonicalChartInstrumentConfig(
        symbol="ETHUSDT",
        display_name="Ethereum / Tether Spot",
        asset_class="crypto",
        market_or_venue="Binance Spot",
        price_currency="USDT",
        quotation_unit="USDT per ETH",
        price_basis=ChartPriceBasis.TRADE_PRICE,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="BINANCE_REST",
        has_volume=True,
        base_asset="ETH",
        quote_asset="USDT",
        supported_native_intervals=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
    ),
    # Sovereign Debt / Fixed Income (Clean price % par; OTC evaluated pricing: Daily only)
    CanonicalChartInstrumentConfig(
        symbol="US10Y",
        display_name="US 10-Year Benchmark Treasury Note",
        asset_class="bonds",
        market_or_venue="US Treasury OTC",
        price_currency="USD",
        quotation_unit="% of par (Clean Price)",
        price_basis=ChartPriceBasis.CLEAN_PRICE,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="EVALUATED_PRICING_FEED",
        has_volume=False,
        supported_native_intervals=["1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
            "5m": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
            "15m": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
            "30m": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
            "1h": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
            "4h": "Intraday bar feed is not published for OTC evaluated benchmark sovereign debt.",
        },
    ),
    # Exchange-Traded Futures (Individual contracts, supports negative prices for commodities)
    CanonicalChartInstrumentConfig(
        symbol="CLZ26",
        display_name="Crude Oil Dec 2026 Futures",
        asset_class="futures",
        market_or_venue="NYMEX",
        price_currency="USD",
        quotation_unit="USD/barrel",
        price_basis=ChartPriceBasis.SETTLEMENT,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="CME_FEED",
        has_volume=True,
        is_futures=True,
        allows_negative_price=True,
        contract_expiration="2026-11-20T20:00:00Z",
        supported_native_intervals=["1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "High-frequency minute data requires CME Level 2 entitlement.",
            "5m": "High-frequency minute data requires CME Level 2 entitlement.",
            "15m": "High-frequency minute data requires CME Level 2 entitlement.",
            "30m": "High-frequency minute data requires CME Level 2 entitlement.",
        },
    ),
    CanonicalChartInstrumentConfig(
        symbol="GCZ26",
        display_name="Gold Dec 2026 Futures",
        asset_class="futures",
        market_or_venue="COMEX",
        price_currency="USD",
        quotation_unit="USD/troy oz",
        price_basis=ChartPriceBasis.SETTLEMENT,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="CME_FEED",
        has_volume=True,
        is_futures=True,
        allows_negative_price=False,
        contract_expiration="2026-12-28T18:30:00Z",
        supported_native_intervals=["1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "High-frequency minute data requires CME Level 2 entitlement.",
            "5m": "High-frequency minute data requires CME Level 2 entitlement.",
            "15m": "High-frequency minute data requires CME Level 2 entitlement.",
            "30m": "High-frequency minute data requires CME Level 2 entitlement.",
        },
    ),
    CanonicalChartInstrumentConfig(
        symbol="ESZ26",
        display_name="E-mini S&P 500 Dec 2026 Futures",
        asset_class="futures",
        market_or_venue="CME",
        price_currency="USD",
        quotation_unit="Index points",
        price_basis=ChartPriceBasis.SETTLEMENT,
        adjustment_basis=ChartAdjustmentBasis.UNADJUSTED,
        provider_key="CME_FEED",
        has_volume=True,
        is_futures=True,
        allows_negative_price=False,
        contract_expiration="2026-12-18T14:30:00Z",
        supported_native_intervals=["5m", "15m", "30m", "1h", "4h", "1d"],
        supported_derived_intervals=["1w", "1M"],
        unsupported_intervals_reasons={
            "1m": "1-minute feed requires dedicated CME Globex intraday subscription."
        },
    ),
]

CANONICAL_CHART_INSTRUMENT_MAP: Dict[str, CanonicalChartInstrumentConfig] = {
    item.symbol: item for item in DEFAULT_CANONICAL_CHART_INSTRUMENTS
}

CANONICAL_CHART_INSTRUMENT_BY_ID: Dict[UUID, CanonicalChartInstrumentConfig] = {
    item.entity_id: item for item in DEFAULT_CANONICAL_CHART_INSTRUMENTS
}
