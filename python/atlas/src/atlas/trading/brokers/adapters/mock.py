"""Credential-free adapter used for contract and integration tests only."""

from __future__ import annotations

import uuid

from atlas.trading.brokers.adapters.base import BrokerSandboxAdapter
from atlas.trading.brokers.domain import (
    BrokerCapabilities,
    BrokerCapability,
    BrokerConnection,
    BrokerEnvironment,
    NormalizedOrder,
    NormalizedOrderRequest,
    ProviderStatus,
    utc_now,
)


class MockBrokerAdapter(BrokerSandboxAdapter):
    """A deterministic sandbox adapter; never represents provider verification."""

    def __init__(
        self,
        connection: BrokerConnection,
        capabilities: BrokerCapabilities,
    ) -> None:
        super().__init__(connection)
        self._capabilities = capabilities
        self._orders: dict[str, NormalizedOrder] = {}

    @property
    def provider_id(self) -> str:
        return self._capabilities.provider_id

    def get_capabilities(self) -> BrokerCapabilities:
        return self._capabilities

    def validate_connection(self) -> BrokerConnection:
        if self.connection.environment is not BrokerEnvironment.SANDBOX:
            raise ValueError("Mock adapter cannot validate production connections.")
        return BrokerConnection(
            **{
                **self.connection.__dict__,
                "status": ProviderStatus.VERIFIED_WITH_MOCK,
                "last_verified_at": utc_now(),
            }
        )

    def submit_order(self, request: NormalizedOrderRequest) -> NormalizedOrder:
        if not self._capabilities.supports(BrokerCapability.ORDER_SUBMIT):
            return super().submit_order(request)
        external_id = str(uuid.uuid4())
        order = NormalizedOrder(
            provider_id=self.provider_id,
            external_order_id=external_id,
            client_order_id=request.client_order_id,
            status="ACCEPTED",
            submitted_at=utc_now(),
            raw_status="MOCK_ACCEPTED",
        )
        self._orders[external_id] = order
        return order

    def get_order(self, external_order_id: str) -> NormalizedOrder:
        if not self._capabilities.supports(BrokerCapability.ORDER_READ):
            return super().get_order(external_order_id)
        from atlas.trading.brokers.errors import ConnectionNotFoundError

        try:
            return self._orders[external_order_id]
        except KeyError as exc:
            raise ConnectionNotFoundError(
                f"Order '{external_order_id}' was not found in the mock adapter."
            ) from exc
