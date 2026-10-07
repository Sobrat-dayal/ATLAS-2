from atlas.market_data import MarketDataProviderCapabilities
from atlas.providers.base import BaseProvider
from atlas.providers.descriptor import ProviderDescriptor
from atlas.providers.openbb.runtime import OpenBBRuntime
from atlas.providers.types import ProviderDomain

OPENBB_DESCRIPTOR = ProviderDescriptor(
    key="openbb",
    display_name="OpenBB",
    description="an ATLAS integration bridge to the OpenBB data-provider ecosystem",
    adapter_version=1,
    domains=frozenset(
        [
            ProviderDomain.MARKET_DATA,
            ProviderDomain.FUNDAMENTALS,
            ProviderDomain.ECONOMICS,
            ProviderDomain.NEWS,
            ProviderDomain.RESEARCH,
        ]
    ),
    homepage_url="https://openbb.co",
    documentation_url="https://docs.openbb.co",
)


class OpenBBProviderAdapter(BaseProvider):
    """
    ATLAS Provider adapter for OpenBB framework.
    """

    def __init__(self, runtime: OpenBBRuntime):
        self._runtime = runtime

    @property
    def descriptor(self) -> ProviderDescriptor:
        return OPENBB_DESCRIPTOR

    @property
    def market_data_capabilities(self) -> MarketDataProviderCapabilities:
        return MarketDataProviderCapabilities(operations=frozenset())

    @property
    def fundamental_capabilities(self) -> "FundamentalProviderCapabilities":
        from atlas.fundamentals import FundamentalProviderCapabilities
        return FundamentalProviderCapabilities(operations=frozenset())

    @property
    def economic_capabilities(self) -> "EconomicProviderCapabilities":
        from atlas.economics import EconomicProviderCapabilities
        return EconomicProviderCapabilities(operations=frozenset())

    @property
    def news_capabilities(self) -> "NewsProviderCapabilities":
        from atlas.news import NewsProviderCapabilities
        return NewsProviderCapabilities(operations=frozenset())

    @property
    def research_capabilities(self) -> "ResearchProviderCapabilities":
        from atlas.research import ResearchProviderCapabilities
        return ResearchProviderCapabilities(operations=frozenset())

    @property
    def runtime(self) -> OpenBBRuntime:
        return self._runtime

    async def close(self) -> None:
        """Clean up OpenBB resources if necessary. Stateless for now."""
        pass
