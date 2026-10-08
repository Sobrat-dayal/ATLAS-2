from typing import Protocol, runtime_checkable

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


@runtime_checkable
class QuoteMarketDataProvider(Protocol):
    """
    Protocol for providers that support the QUOTE operation.
    """

    async def get_quotes(self, request: QuoteRequest) -> QuoteResponse: ...


@runtime_checkable
class HistoricalBarsMarketDataProvider(Protocol):
    """
    Protocol for providers that support the HISTORICAL_BARS operation.
    """

    async def get_historical_bars(
        self, request: HistoricalBarsRequest
    ) -> HistoricalBarsResponse: ...


@runtime_checkable
class TradesMarketDataProvider(Protocol):
    """
    Protocol for providers that support the TRADES operation.
    """

    async def get_trades(self, request: TradesRequest) -> TradesResponse: ...


@runtime_checkable
class OrderBookMarketDataProvider(Protocol):
    """
    Protocol for providers that support the ORDER_BOOK operation.
    """

    async def get_order_book(self, request: OrderBookRequest) -> OrderBookResponse: ...


@runtime_checkable
class SnapshotMarketDataProvider(Protocol):
    """
    Protocol for providers that support the SNAPSHOT operation.
    """

    async def get_market_snapshots(
        self, request: MarketSnapshotRequest
    ) -> MarketSnapshotResponse: ...


from typing import AsyncIterator
from atlas.market_data.requests import LiveQuoteSubscriptionRequest
from atlas.market_data.quote import Quote


@runtime_checkable
class LiveQuoteStreamProvider(Protocol):
    """
    Protocol for providers that support the LIVE_QUOTE_STREAM operation.
    """

    async def stream_live_quotes(
        self, request: LiveQuoteSubscriptionRequest
    ) -> AsyncIterator[Quote]: ...
