"""Stage 145 broker abstraction and sandbox boundary."""

from atlas.trading.brokers.connections import BrokerConnectionRegistry
from atlas.trading.brokers.domain import (
    BrokerCapabilities,
    BrokerCapability,
    BrokerConnection,
    BrokerEnvironment,
    BrokerProvider,
    NormalizedAccount,
    NormalizedOrder,
    NormalizedOrderRequest,
    ProviderStatus,
)
from atlas.trading.brokers.gateway import BrokerExecutionGateway
from atlas.trading.brokers.registry.providers import BrokerProviderRegistry
from atlas.trading.brokers.security import SecretVault, validate_sandbox_url

__all__ = [
    "BrokerCapabilities",
    "BrokerCapability",
    "BrokerConnection",
    "BrokerConnectionRegistry",
    "BrokerEnvironment",
    "BrokerExecutionGateway",
    "BrokerProvider",
    "BrokerProviderRegistry",
    "NormalizedAccount",
    "NormalizedOrder",
    "NormalizedOrderRequest",
    "ProviderStatus",
    "SecretVault",
    "validate_sandbox_url",
]
