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
    """Supported baseline interval for Stage 66.

    Stage 66 enforces a single verified baseline interval ('1d').
    Stage 68 will introduce expanded intraday and multi-resolution intervals.
    """

    ONE_DAY = "1d"


class ChartRenderMode(StrEnum):
    """Foundational chart visualization modes for Stage 66."""

    CANDLESTICK = "candlestick"
    LINE = "line"


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


# Verified catalog of canonical chartable instruments across financial asset classes
DEFAULT_CANONICAL_CHART_INSTRUMENTS: List[CanonicalChartInstrumentConfig] = [
    # Equities
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
    ),
    # Foreign Exchange (OTC FX - volume is explicitly None)
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
    ),
    # Cryptocurrency Spot
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
    ),
    # Sovereign Debt / Fixed Income (Clean price % of par, OTC - no trade volume)
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
    ),
]

CANONICAL_CHART_INSTRUMENT_MAP: Dict[str, CanonicalChartInstrumentConfig] = {
    item.symbol: item for item in DEFAULT_CANONICAL_CHART_INSTRUMENTS
}

CANONICAL_CHART_INSTRUMENT_BY_ID: Dict[UUID, CanonicalChartInstrumentConfig] = {
    item.entity_id: item for item in DEFAULT_CANONICAL_CHART_INSTRUMENTS
}
