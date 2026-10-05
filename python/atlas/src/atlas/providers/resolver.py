import inspect
from atlas.providers.registry import ProviderRegistry
from atlas.providers.base import BaseProvider
from atlas.providers.types import ProviderDomain
from atlas.providers.errors import (
    ProviderDomainUnsupportedError,
    ProviderFactoryInvalidError,
    ProviderAdapterInvalidError,
    sanitize_provider_error
)


class ProviderResolver:
    """
    Explicitly resolves a provider key to a constructed provider adapter instance.
    """

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    async def resolve(self, provider_key: str, required_domain: ProviderDomain | None = None) -> BaseProvider:
        """
        Resolves a provider key, validating the required domain if provided.
        Constructs the provider lazily via its registered factory.
        """
        registration = self._registry.get(provider_key)

        if required_domain is not None:
            if required_domain not in registration.descriptor.domains:
                raise ProviderDomainUnsupportedError(
                    f"Provider '{provider_key}' does not support domain '{required_domain.value}'"
                )

        try:
            # Construct the adapter
            result = registration.factory()
            if inspect.isawaitable(result):
                adapter = await result
            else:
                adapter = result
        except Exception as e:
            # Wrap factory failures
            raise sanitize_provider_error(
                ProviderFactoryInvalidError(f"Failed to construct provider '{provider_key}': {str(e)}")
            ) from e

        # Validate that the constructed adapter matches the registered descriptor
        adapter_descriptor = adapter.descriptor
        if adapter_descriptor.key != provider_key:
            raise ProviderAdapterInvalidError(
                f"Factory returned provider with key '{adapter_descriptor.key}' instead of '{provider_key}'"
            )
        if adapter_descriptor.adapter_version != registration.descriptor.adapter_version:
            raise ProviderAdapterInvalidError(
                f"Factory returned adapter version {adapter_descriptor.adapter_version} instead of {registration.descriptor.adapter_version}"
            )

        return adapter
