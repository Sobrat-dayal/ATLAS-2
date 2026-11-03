import pytest
from atlas.trading.brokers import (
    BrokerConnectionRegistry,
    BrokerExecutionGateway,
    BrokerProviderRegistry,
    NormalizedOrderRequest,
    SecretVault,
)
from atlas.trading.brokers.errors import (
    CrossTenantConnectionError,
    SandboxFirewallError,
)
from atlas.trading.brokers.security import validate_sandbox_url
from cryptography.fernet import Fernet


def build_connection_registry() -> tuple[BrokerProviderRegistry, BrokerConnectionRegistry]:
    providers = BrokerProviderRegistry()
    connections = BrokerConnectionRegistry(
        providers,
        SecretVault(Fernet.generate_key()),
    )
    return providers, connections


def test_default_providers_create_explicit_mock_adapters() -> None:
    providers, connections = build_connection_registry()
    connection = connections.create("tenant-a", "ALPACA_PAPER", "sandbox-secret")

    adapter = providers.create_adapter(connection)
    verified = adapter.validate_connection()

    assert verified.status.value == "VERIFIED_WITH_MOCK"
    assert adapter.provider_id == "ALPACA_PAPER"


def test_gateway_requires_persisted_verification_before_submission() -> None:
    providers, connections = build_connection_registry()
    connection = connections.create("tenant-a", "ALPACA_PAPER", "sandbox-secret")
    unverified_adapter = providers.create_adapter(connection)
    request = NormalizedOrderRequest(
        symbol="AAPL",
        side="BUY",
        order_type="MARKET",
        quantity=1,
        client_order_id="stage145-unknown-outcome-check",
    )

    with pytest.raises(SandboxFirewallError):
        BrokerExecutionGateway(unverified_adapter).submit(request)


def test_verified_mock_submission_returns_provider_order_id() -> None:
    providers, connections = build_connection_registry()
    connection = connections.create("tenant-a", "ALPACA_PAPER", "sandbox-secret")
    probe = providers.create_adapter(connection)
    verified = connections.mark_verified(
        connection.connection_id,
        "tenant-a",
        probe.validate_connection().status,
    )
    adapter = providers.create_adapter(verified)

    order = BrokerExecutionGateway(adapter).submit(
        NormalizedOrderRequest(
            symbol="AAPL",
            side="BUY",
            order_type="MARKET",
            quantity=1,
            client_order_id="stage145-submit-check",
        )
    )

    assert order.status == "ACCEPTED"
    assert order.external_order_id


def test_connection_and_secret_are_tenant_scoped() -> None:
    _, connections = build_connection_registry()
    connection = connections.create("tenant-a", "TRADIER_SANDBOX", "sandbox-secret")

    with pytest.raises(CrossTenantConnectionError):
        connections.credential(connection.connection_id, "tenant-b")


def test_production_host_is_rejected_by_sandbox_allowlist() -> None:
    with pytest.raises(SandboxFirewallError):
        validate_sandbox_url(
            "https://api.alpaca.markets",
            frozenset({"paper-api.alpaca.markets"}),
        )
