from typing import Awaitable, Callable

from pydantic import BaseModel, ConfigDict

from atlas.providers.base import BaseProvider
from atlas.providers.descriptor import ProviderDescriptor

# Factory definition for constructing a provider adapter.
ProviderFactory = Callable[..., BaseProvider | Awaitable[BaseProvider]]


class ProviderRegistration(BaseModel):
    """
    An immutable registration connecting a ProviderDescriptor to the factory
    capable of instantiating the adapter.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    descriptor: ProviderDescriptor
    factory: ProviderFactory
