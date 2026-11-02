"""Capability-gated sandbox execution gateway."""

from __future__ import annotations

from atlas.trading.brokers.adapters.base import BrokerSandboxAdapter
from atlas.trading.brokers.domain import (
    BrokerCapability,
    BrokerEnvironment,
    NormalizedOrder,
    NormalizedOrderRequest,
    ProviderStatus,
)
from atlas.trading.brokers.errors import (
    LiveBrokerBlockedError,
    SandboxFirewallError,
    UnsupportedCapabilityError,
)


class BrokerExecutionGateway:
    """Routes only to registered sandbox adapters after capability checks."""

    def __init__(self, adapter: BrokerSandboxAdapter) -> None:
        self._adapter = adapter

    def _assert_safe_connection(self) -> None:
        connection = self._adapter.connection
        if connection.environment is not BrokerEnvironment.SANDBOX:
            raise LiveBrokerBlockedError(
                "Stage 145 only permits orders for sandbox connections."
            )
        if connection.status not in {
            ProviderStatus.VERIFIED_WITH_MOCK,
            ProviderStatus.VERIFIED_WITH_PROVIDER_SANDBOX,
            ProviderStatus.CONNECTED,
        }:
            raise SandboxFirewallError(
                "Sandbox connection must be verified before an order operation."
            )

    def _require(self, capability: BrokerCapability) -> None:
        if not self._adapter.get_capabilities().supports(capability):
            raise UnsupportedCapabilityError(
                f"Provider '{self._adapter.provider_id}' does not support {capability.value}."
            )

    def preview(self, request: NormalizedOrderRequest) -> dict[str, object]:
        self._assert_safe_connection()
        self._require(BrokerCapability.ORDER_PREVIEW)
        return self._adapter.preview_order(request)

    def submit(self, request: NormalizedOrderRequest) -> NormalizedOrder:
        self._assert_safe_connection()
        self._require(BrokerCapability.ORDER_SUBMIT)
        return self._adapter.submit_order(request)

    def modify(self, external_order_id: str, request: NormalizedOrderRequest) -> NormalizedOrder:
        self._assert_safe_connection()
        self._require(BrokerCapability.ORDER_MODIFY)
        return self._adapter.modify_order(external_order_id, request)

    def cancel(self, external_order_id: str) -> NormalizedOrder:
        self._assert_safe_connection()
        self._require(BrokerCapability.ORDER_CANCEL)
        return self._adapter.cancel_order(external_order_id)

    def get_order(self, external_order_id: str) -> NormalizedOrder:
        self._require(BrokerCapability.ORDER_READ)
        return self._adapter.get_order(external_order_id)
