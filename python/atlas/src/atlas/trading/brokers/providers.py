"""Registered sandbox provider definitions.

Capabilities are intentionally conservative until verified against a provider
sandbox; a definition is not evidence that a provider is connected.
"""

from __future__ import annotations

from atlas.trading.brokers.domain import (
    BrokerCapabilities,
    BrokerCapability,
    BrokerEnvironment,
    BrokerProvider,
)


def _capabilities(provider_id: str, *, order_modify: bool = False) -> BrokerCapabilities:
    capabilities = {
        BrokerCapability.ORDER_PREVIEW,
        BrokerCapability.ORDER_SUBMIT,
        BrokerCapability.ORDER_CANCEL,
        BrokerCapability.ORDER_READ,
    }
    if order_modify:
        capabilities.add(BrokerCapability.ORDER_MODIFY)
    return BrokerCapabilities(
        provider_id=provider_id,
        environment=BrokerEnvironment.SANDBOX,
        capabilities=frozenset(capabilities),
        asset_classes=frozenset({"EQUITY", "OPTION"}),
        order_types=frozenset({"MARKET", "LIMIT", "STOP", "STOP_LIMIT"}),
        time_in_force=frozenset({"DAY", "GTC", "IOC", "FOK"}),
    )


ALPACA_PAPER = BrokerProvider(
    provider_id="ALPACA_PAPER",
    display_name="Alpaca Paper",
    environment=BrokerEnvironment.SANDBOX,
    execution_host="paper-api.alpaca.markets",
    allowed_hosts=frozenset({"paper-api.alpaca.markets"}),
    capabilities=_capabilities("ALPACA_PAPER", order_modify=True),
)

UPSTOX_SANDBOX = BrokerProvider(
    provider_id="UPSTOX_SANDBOX",
    display_name="Upstox Sandbox",
    environment=BrokerEnvironment.SANDBOX,
    execution_host="api-sandbox.upstox.com",
    allowed_hosts=frozenset({"api-sandbox.upstox.com"}),
    capabilities=_capabilities("UPSTOX_SANDBOX", order_modify=True),
)

TRADIER_SANDBOX = BrokerProvider(
    provider_id="TRADIER_SANDBOX",
    display_name="Tradier Sandbox",
    environment=BrokerEnvironment.SANDBOX,
    execution_host="sandbox.tradier.com",
    allowed_hosts=frozenset({"sandbox.tradier.com"}),
    capabilities=_capabilities("TRADIER_SANDBOX", order_modify=False),
)

DEFAULT_PROVIDERS = (ALPACA_PAPER, UPSTOX_SANDBOX, TRADIER_SANDBOX)
