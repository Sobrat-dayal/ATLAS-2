from typing import Callable
from atlas.providers.registry import ProviderRegistry
from atlas.providers.health.models import ProviderHealthDefinition
from atlas.providers.health.probe import ProviderHealthProbe
from atlas.providers.errors import ProviderNotRegisteredError

class ProviderHealthRegistry:
    """
    Code-defined registry for Provider health probes.
    Separate from ProviderRegistry. Stores definitions and probe factories.
    """
    def __init__(self, provider_registry: ProviderRegistry) -> None:
        self._provider_registry = provider_registry
        self._definitions: dict[str, ProviderHealthDefinition] = {}
        self._probes: dict[str, Callable[[], ProviderHealthProbe]] = {}
        self._frozen: bool = False

    def register(
        self,
        definition: ProviderHealthDefinition,
        probe_factory: Callable[[], ProviderHealthProbe],
    ) -> None:
        if self._frozen:
            raise RuntimeError("Cannot register health definition: ProviderHealthRegistry is frozen")

        key = definition.provider_key
        
        # Verify provider exists in main registry
        try:
            self._provider_registry.get(key)
        except ProviderNotRegisteredError:
            raise ValueError(f"Cannot register health definition for unregistered provider: {key}")

        if key in self._definitions:
            raise ValueError(f"Provider health definition for key '{key}' is already registered")

        self._definitions[key] = definition
        self._probes[key] = probe_factory

    def freeze(self) -> None:
        self._frozen = True

    def get_definition(self, provider_key: str) -> ProviderHealthDefinition:
        if provider_key not in self._definitions:
            raise ValueError(f"No health definition registered for provider: {provider_key}")
        return self._definitions[provider_key]

    def get_probe_factory(self, provider_key: str) -> Callable[[], ProviderHealthProbe]:
        if provider_key not in self._probes:
            raise ValueError(f"No health probe registered for provider: {provider_key}")
        return self._probes[provider_key]

    def list_definitions(self) -> list[ProviderHealthDefinition]:
        sorted_keys = sorted(self._definitions.keys())
        return [self._definitions[k] for k in sorted_keys]

    def has_definition(self, provider_key: str) -> bool:
        return provider_key in self._definitions
