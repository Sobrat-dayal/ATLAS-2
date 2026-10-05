import enum
from pydantic import BaseModel, ConfigDict, Field


class ProviderDomain(str, enum.Enum):
    """Domains of functionality a Provider may support."""
    MARKET_DATA = "market_data"
    FUNDAMENTALS = "fundamentals"
    ECONOMICS = "economics"
    NEWS = "news"
    RESEARCH = "research"
    GEOSPATIAL = "geospatial"
    BROKER = "broker"
    ALTERNATIVE_DATA = "alternative_data"


class ProviderCatalogEntry(BaseModel):
    """A serialized metadata entry for a Provider."""
    model_config = ConfigDict(frozen=True)

    key: str = Field(..., description="Stable unique identifier for the provider")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Brief description of the provider")
    adapter_version: int = Field(..., description="Version of the ATLAS adapter contract")
    domains: list[ProviderDomain] = Field(
        ...,
        description="List of domains supported by this provider"
    )
    documentation_url: str | None = Field(default=None, description="URL for documentation")
    homepage_url: str | None = Field(default=None, description="URL for provider homepage")


class ProviderCatalogResponse(BaseModel):
    """Response wrapper for a list of providers."""
    providers: list[ProviderCatalogEntry]


class ProviderListInput(BaseModel):
    domain: ProviderDomain | None = None


class ProviderGetInput(BaseModel):
    provider_key: str
