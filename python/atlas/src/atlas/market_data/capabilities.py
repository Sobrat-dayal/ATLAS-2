from pydantic import BaseModel, ConfigDict, Field

from atlas.market_data.enums import MarketDataOperation


class MarketDataProviderCapabilities(BaseModel):
    """
    Capabilities of a Market Data Provider.
    Declares the canonical operations supported by the provider.
    """

    model_config = ConfigDict(frozen=True)

    operations: frozenset[MarketDataOperation] = Field(
        default_factory=frozenset,
        description="The set of canonical MarketDataOperations supported by the provider.",
    )
