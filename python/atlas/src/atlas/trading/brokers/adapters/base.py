"""Small, capability-aware broker adapter contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from atlas.trading.brokers.domain import (
    BrokerCapabilities,
    BrokerConnection,
    BrokerEnvironment,
    NormalizedAccount,
    NormalizedOrder,
    NormalizedOrderRequest,
)
from atlas.trading.brokers.errors import LiveBrokerBlockedError, UnsupportedCapabilityError


class BrokerSandboxAdapter(ABC):
    """Interface implemented by sandbox-only provider adapters."""

    def __init__(self, connection: BrokerConnection) -> None:
        if connection.environment is not BrokerEnvironment.SANDBOX:
            raise LiveBrokerBlockedError(
                "Stage 145 adapters cannot be constructed for production connections."
            )
        self.connection = connection

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Return the registered provider identifier."""

    @abstractmethod
    def get_capabilities(self) -> BrokerCapabilities:
        """Return capabilities verified for this adapter."""

    @abstractmethod
    def validate_connection(self) -> BrokerConnection:
        """Validate credentials and return an updated connection state."""

    def list_accounts(self) -> list[NormalizedAccount]:
        raise UnsupportedCapabilityError("Account discovery is not supported.")

    def preview_order(self, request: NormalizedOrderRequest) -> dict[str, Any]:
        raise UnsupportedCapabilityError("Order preview is not supported.")

    def submit_order(self, request: NormalizedOrderRequest) -> NormalizedOrder:
        raise UnsupportedCapabilityError("Order submission is not supported.")

    def modify_order(
        self, external_order_id: str, request: NormalizedOrderRequest
    ) -> NormalizedOrder:
        raise UnsupportedCapabilityError("Order modification is not supported.")

    def cancel_order(self, external_order_id: str) -> NormalizedOrder:
        raise UnsupportedCapabilityError("Order cancellation is not supported.")

    def get_order(self, external_order_id: str) -> NormalizedOrder:
        raise UnsupportedCapabilityError("Order lookup is not supported.")
