"""Provider and adapter registry with explicit tenant isolation."""

from __future__ import annotations

from typing import Callable

from atlas.trading.brokers.adapters.base import BrokerSandboxAdapter
from atlas.trading.brokers.adapters.mock import MockBrokerAdapter
from atlas.trading.brokers.domain import BrokerConnection, BrokerEnvironment, BrokerProvider
from atlas.trading.brokers.errors import BrokerNotFoundError, LiveBrokerBlockedError
from atlas.trading.brokers.providers import DEFAULT_PROVIDERS

AdapterFactory = Callable[[BrokerConnection], BrokerSandboxAdapter]


class BrokerProviderRegistry:
    """Stores sandbox provider definitions and adapter factories."""

    def __init__(self, providers: tuple[BrokerProvider, ...] = DEFAULT_PROVIDERS) -> None:
        self._providers = {provider.provider_id: provider for provider in providers}
        self._factories: dict[str, AdapterFactory] = {
            provider.provider_id: lambda connection, provider=provider: MockBrokerAdapter(
                connection, provider.capabilities
            )
            for provider in providers
        }

    def register(self, provider: BrokerProvider, factory: AdapterFactory | None = None) -> None:
        self._providers[provider.provider_id] = provider
        if factory is not None:
            self._factories[provider.provider_id] = factory

    def get(self, provider_id: str) -> BrokerProvider:
        try:
            return self._providers[provider_id]
        except KeyError as exc:
            raise BrokerNotFoundError(f"Provider '{provider_id}' is not registered.") from exc

    def list(self) -> list[BrokerProvider]:
        return list(self._providers.values())

    def create_adapter(self, connection: BrokerConnection) -> BrokerSandboxAdapter:
        if connection.environment is not BrokerEnvironment.SANDBOX:
            raise LiveBrokerBlockedError(
                "Stage 145 only permits sandbox adapter connections."
            )
        self.get(connection.provider_id)
        try:
            factory = self._factories[connection.provider_id]
        except KeyError as exc:
            raise BrokerNotFoundError(
                f"No adapter is registered for '{connection.provider_id}'."
            ) from exc
        return factory(connection)
