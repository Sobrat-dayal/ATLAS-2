from atlas.providers.descriptor import ProviderDescriptor
from atlas.providers.errors import ProviderNotRegisteredError
from atlas.providers.registration import ProviderRegistration
from atlas.providers.types import ProviderDomain


class ProviderRegistry:
    """
    Code-defined registry for Provider adapters.
    Maintains a list of available provider factories and their descriptors.
    """

    def __init__(self) -> None:
        self._providers: dict[str, ProviderRegistration] = {}
        self._frozen: bool = False

    def register(self, registration: ProviderRegistration) -> None:
        """Explicitly registers a provider. Must be called before freeze()."""
        if self._frozen:
            raise RuntimeError("Cannot register provider: ProviderRegistry is frozen")

        key = registration.descriptor.key
        if key in self._providers:
            raise ValueError(f"Provider with key '{key}' is already registered")

        self._providers[key] = registration

    def freeze(self) -> None:
        """Freezes the registry, preventing further registrations."""
        self._frozen = True

    def get(self, provider_key: str) -> ProviderRegistration:
        """Looks up a provider registration by its exact key."""
        if provider_key not in self._providers:
            raise ProviderNotRegisteredError(f"Provider '{provider_key}' is not registered.")
        return self._providers[provider_key]

    def list_providers(self, domain: ProviderDomain | None = None) -> list[ProviderDescriptor]:
        """
        Lists all registered provider descriptors, deterministically ordered by key.
        If domain is provided, filters for providers declaring that domain.
        """
        # Ensure deterministic ordering
        sorted_keys = sorted(self._providers.keys())
        descriptors = [self._providers[k].descriptor for k in sorted_keys]

        if domain is not None:
            descriptors = [d for d in descriptors if domain in d.domains]

        return descriptors
