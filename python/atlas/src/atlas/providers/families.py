from typing import Protocol

from atlas.market_data import MarketDataProviderCapabilities
from atlas.providers.base import BaseProvider


class MarketDataProvider(BaseProvider, Protocol):
    """
    Abstractions for external market data sources (e.g., quotes, bars, trades, FX).
    Specific canonical methods will be introduced in Stage 33.
    """

    @property
    def market_data_capabilities(self) -> MarketDataProviderCapabilities: ...


class FundamentalProvider(BaseProvider, Protocol):
    """
    Abstractions for external fundamentals sources (e.g., financial statements, valuation, ownership).
    Specific canonical methods will be introduced in Stage 34.
    """

    pass


class EconomicProvider(BaseProvider, Protocol):
    """
    Abstractions for external economic sources (e.g., series, observations, macro releases).
    Specific canonical methods will be introduced in Stage 35.
    """

    pass


class NewsProvider(BaseProvider, Protocol):
    """
    Abstractions for external news sources (e.g., headlines, articles, feeds).
    Specific canonical methods will be introduced in Stage 36.
    """

    pass


class ResearchProvider(BaseProvider, Protocol):
    """
    Abstractions for external research sources (e.g., papers, metadata, citations).
    Specific canonical methods will be introduced in Stage 36.
    """

    pass


class GeospatialProvider(BaseProvider, Protocol):
    """
    Abstractions for external geospatial sources (e.g., maps, weather, aviation).
    """

    pass


class BrokerProvider(BaseProvider, Protocol):
    """
    Abstractions for external broker integrations (e.g., accounts, orders, execution).
    """

    pass


class AlternativeDataProvider(BaseProvider, Protocol):
    """
    Abstractions for external alternative data sources.
    """

    pass
