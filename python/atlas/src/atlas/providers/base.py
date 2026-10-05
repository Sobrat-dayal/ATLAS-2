from typing import Protocol, runtime_checkable
from atlas.providers.descriptor import ProviderDescriptor


@runtime_checkable
class BaseProvider(Protocol):
    """Base contract that all ATLAS Providers must fulfill."""
    
    @property
    def descriptor(self) -> ProviderDescriptor:
        """Returns the descriptor defining the identity and capabilities of this provider."""
        ...
        
    async def close(self) -> None:
        """
        Cleans up any resources held by the provider (e.g., HTTP sessions, connections).
        Default behavior may be a no-op if the provider is stateless.
        """
        ...
