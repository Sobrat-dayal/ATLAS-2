import re
from pydantic import BaseModel, ConfigDict, Field, field_validator
from atlas.providers.types import ProviderDomain


class ProviderDescriptor(BaseModel):
    """Immutable metadata describing a Provider adapter."""
    model_config = ConfigDict(frozen=True)

    key: str = Field(..., description="Stable unique identifier for the provider (lowercase snake_case)")
    display_name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="Brief description of the provider adapter")
    adapter_version: int = Field(..., ge=1, description="Version of the ATLAS adapter contract")
    domains: frozenset[ProviderDomain] = Field(..., description="Domains supported by this provider")
    documentation_url: str | None = Field(default=None, description="URL for documentation")
    homepage_url: str | None = Field(default=None, description="URL for provider homepage")

    @field_validator("key")
    @classmethod
    def validate_key(cls, value: str) -> str:
        if not re.match(r"^[a-z][a-z0-9_]{0,63}$", value):
            raise ValueError("Provider key must be lowercase snake_case (e.g., 'openbb', 'alpha_vantage')")
        return value

    @field_validator("domains")
    @classmethod
    def validate_domains(cls, value: frozenset[ProviderDomain]) -> frozenset[ProviderDomain]:
        if not value:
            raise ValueError("Provider must support at least one domain")
        return value

    @field_validator("documentation_url", "homepage_url")
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is not None and not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return value
