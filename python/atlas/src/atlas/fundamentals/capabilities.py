from pydantic import BaseModel, Field

from atlas.fundamentals.enums import FundamentalDataOperation


class FundamentalProviderCapabilities(BaseModel):
    """
    Capabilities of a Fundamental Data Provider.
    """

    operations: frozenset[FundamentalDataOperation] = Field(default_factory=frozenset)

    model_config = {"frozen": True}
