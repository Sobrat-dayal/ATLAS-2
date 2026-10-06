from typing import Any

from atlas.capabilities.context import CapabilityExecutionContext
from atlas.capabilities.definition import CapabilityDefinition
from atlas.capabilities.registry import CapabilityRegistry
from atlas.capabilities.types import CapabilityExposure, CapabilityPermissionClass
from atlas.providers.registry import ProviderRegistry
from atlas.providers.types import (
    ProviderCatalogEntry,
    ProviderCatalogResponse,
    ProviderGetInput,
    ProviderListInput,
)


def register_provider_capabilities(
    cap_registry: CapabilityRegistry, provider_registry: ProviderRegistry
) -> None:
    """
    Registers the static provider catalog operations as capabilities.
    Does NOT construct providers or access external networks.
    """

    def _to_catalog_entry(descriptor: Any) -> ProviderCatalogEntry:
        return ProviderCatalogEntry(
            key=descriptor.key,
            display_name=descriptor.display_name,
            description=descriptor.description,
            adapter_version=descriptor.adapter_version,
            domains=list(descriptor.domains),
            documentation_url=descriptor.documentation_url,
            homepage_url=descriptor.homepage_url,
        )

    async def list_providers_handler(
        inputs: ProviderListInput, context: CapabilityExecutionContext
    ) -> ProviderCatalogResponse:
        """
        Lists registered provider metadata.
        Input may optionally contain 'domain' to filter.
        """
        domain = inputs.domain

        descriptors = provider_registry.list_providers(domain=domain)
        entries = [_to_catalog_entry(d) for d in descriptors]

        return ProviderCatalogResponse(providers=entries)

    async def get_provider_handler(
        inputs: ProviderGetInput, context: CapabilityExecutionContext
    ) -> ProviderCatalogEntry:
        """
        Gets a single provider's metadata by key.
        """
        provider_key = inputs.provider_key
        registration = provider_registry.get(provider_key)
        return _to_catalog_entry(registration.descriptor)

    # Register provider.list
    cap_registry.register(
        CapabilityDefinition(
            key="provider.list",
            version=1,
            title="List Providers",
            description="List registered provider metadata",
            category="Providers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=ProviderListInput,
            output_model=ProviderCatalogResponse,
        ),
        lambda _session: list_providers_handler,
    )

    # Register provider.get
    cap_registry.register(
        CapabilityDefinition(
            key="provider.get",
            version=1,
            title="Get Provider",
            description="Get provider metadata by key",
            category="Providers",
            permission_class=CapabilityPermissionClass.READ,
            required_permissions=["atlas.access"],
            exposure=CapabilityExposure.APPLICATION,
            requires_confirmation=False,
            input_model=ProviderGetInput,
            output_model=ProviderCatalogEntry,
        ),
        lambda _session: get_provider_handler,
    )
