"""
Canonical Market Data models and protocols for ATLAS.
"""

from atlas.market_data.bars import OHLCVBar
from atlas.market_data.capabilities import MarketDataProviderCapabilities
from atlas.market_data.enums import (
    BarInterval,
    MarketDataOperation,
    MarketDataTimeliness,
    MarketDataTimestampSource,
    MarketSession,
    PriceAdjustment,
    TradeSide,
)
from atlas.market_data.errors import (
    MarketDataAdjustmentUnsupportedError,
    MarketDataError,
    MarketDataIntervalUnsupportedError,
    MarketDataInvalidRequestError,
    MarketDataOperationUnsupportedError,
)
from atlas.market_data.numeric import (
    CanonicalDecimal,
    NonNegativeCanonicalDecimal,
    PositiveCanonicalDecimal,
)
from atlas.market_data.order_book import OrderBookLevel, OrderBookSnapshot
from atlas.market_data.origin import MarketDataOrigin
from atlas.market_data.protocols import (
    HistoricalBarsMarketDataProvider,
    OrderBookMarketDataProvider,
    QuoteMarketDataProvider,
    SnapshotMarketDataProvider,
    TradesMarketDataProvider,
)
from atlas.market_data.quote import Quote
from atlas.market_data.requests import (
    HistoricalBarsRequest,
    MarketSnapshotRequest,
    OrderBookRequest,
    QuoteRequest,
    TradesRequest,
)
from atlas.market_data.responses import (
    HistoricalBarsResponse,
    MarketSnapshotResponse,
    OrderBookResponse,
    QuoteResponse,
    TradesResponse,
)
from atlas.market_data.snapshot import MarketSnapshot
from atlas.market_data.timestamps import CanonicalDatetime
from atlas.market_data.trade import Trade

__all__ = [
    # Enums
    "BarInterval",
    "MarketDataOperation",
    "MarketDataTimeliness",
    "MarketDataTimestampSource",
    "MarketSession",
    "PriceAdjustment",
    "TradeSide",
    # Errors
    "MarketDataAdjustmentUnsupportedError",
    "MarketDataError",
    "MarketDataIntervalUnsupportedError",
    "MarketDataInvalidRequestError",
    "MarketDataOperationUnsupportedError",
    # Validation types
    "CanonicalDecimal",
    "NonNegativeCanonicalDecimal",
    "PositiveCanonicalDecimal",
    "CanonicalDatetime",
    # Base Domain Models
    "MarketDataOrigin",
    "Quote",
    "Trade",
    "OHLCVBar",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "MarketSnapshot",
    # Requests
    "HistoricalBarsRequest",
    "MarketSnapshotRequest",
    "OrderBookRequest",
    "QuoteRequest",
    "TradesRequest",
    # Responses
    "HistoricalBarsResponse",
    "MarketSnapshotResponse",
    "OrderBookResponse",
    "QuoteResponse",
    "TradesResponse",
    # Capabilities and Protocols
    "MarketDataProviderCapabilities",
    "HistoricalBarsMarketDataProvider",
    "OrderBookMarketDataProvider",
    "QuoteMarketDataProvider",
    "SnapshotMarketDataProvider",
    "TradesMarketDataProvider",
]
