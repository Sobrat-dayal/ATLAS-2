"""Tenant-scoped broker connection management."""

from __future__ import annotations

import uuid

from atlas.trading.brokers.domain import (
    BrokerConnection,
    BrokerEnvironment,
    ProviderStatus,
    utc_now,
)
from atlas.trading.brokers.errors import ConnectionNotFoundError, CrossTenantConnectionError
from atlas.trading.brokers.registry.providers import BrokerProviderRegistry
from atlas.trading.brokers.security import SecretVault, validate_sandbox_url


class BrokerConnectionRegistry:
    """Keeps connection metadata and encrypted credentials out of responses."""

    def __init__(self, providers: BrokerProviderRegistry, vault: SecretVault) -> None:
        self._providers = providers
        self._vault = vault
        self._connections: dict[str, BrokerConnection] = {}
        self._credentials: dict[str, bytes] = {}

    def create(
        self,
        tenant_id: str,
        provider_id: str,
        secret: str,
        *,
        account_id: str | None = None,
    ) -> BrokerConnection:
        provider = self._providers.get(provider_id)
        validate_sandbox_url(
            f"https://{provider.execution_host}",
            provider.allowed_hosts,
        )
        connection = BrokerConnection(
            connection_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            provider_id=provider_id,
            environment=BrokerEnvironment.SANDBOX,
            account_id=account_id,
            created_at=utc_now(),
        )
        self._connections[connection.connection_id] = connection
        self._credentials[connection.connection_id] = self._vault.encrypt(secret)
        return connection

    def get(self, connection_id: str, tenant_id: str) -> BrokerConnection:
        connection = self._connections.get(connection_id)
        if connection is None:
            raise ConnectionNotFoundError(f"Connection '{connection_id}' was not found.")
        if connection.tenant_id != tenant_id:
            raise CrossTenantConnectionError("Connection belongs to another tenant.")
        return connection

    def credential(self, connection_id: str, tenant_id: str) -> str:
        self.get(connection_id, tenant_id)
        try:
            ciphertext = self._credentials[connection_id]
        except KeyError as exc:
            raise ConnectionNotFoundError("Connection credentials are unavailable.") from exc
        return self._vault.decrypt(ciphertext)

    def mark_verified(
        self,
        connection_id: str,
        tenant_id: str,
        status: ProviderStatus,
    ) -> BrokerConnection:
        connection = self.get(connection_id, tenant_id)
        updated = BrokerConnection(
            **{
                **connection.__dict__,
                "status": status,
                "last_verified_at": utc_now(),
            }
        )
        self._connections[connection_id] = updated
        return updated

    def revoke(self, connection_id: str, tenant_id: str) -> None:
        self.get(connection_id, tenant_id)
        self._connections.pop(connection_id, None)
        self._credentials.pop(connection_id, None)
