"""Network Registry with Tenant Isolation and Entitlement Enforcement (Stage 133)."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from atlas.maps.infrastructure.domain import (
    InfrastructureNetwork,
    InfrastructureSector,
    LicensingClass,
)
from atlas.maps.infrastructure.errors import (
    EntitlementRevokedError,
    NetworkNotFoundError,
    SensitiveAssetAccessDeniedError,
)


class NetworkRegistry:
    """Registry managing infrastructure networks with multi-tenant isolation and licensing gates."""

    def __init__(self) -> None:
        self._networks: Dict[str, InfrastructureNetwork] = {}
        self._revoked_source_ids: Set[str] = set()

    def register_network(self, network: InfrastructureNetwork) -> None:
        """Register or update an infrastructure network."""
        self._networks[network.network_id] = network

    def revoke_source_entitlement(self, source_id: str) -> None:
        """Revoke dataset entitlement, rendering associated networks inaccessible (Fixture N)."""
        self._revoked_source_ids.add(source_id)

    def restore_source_entitlement(self, source_id: str) -> None:
        """Restore dataset entitlement."""
        self._revoked_source_ids.discard(source_id)

    def get_network(
        self,
        network_id: str,
        actor_tenant_id: Optional[str] = None,
    ) -> InfrastructureNetwork:
        """Retrieve network by ID enforcing tenant boundaries and revoked entitlements."""
        network = self._networks.get(network_id)
        if not network:
            raise NetworkNotFoundError(network_id)

        # Check for revoked source
        source_id = network.properties.get("source_id", "OFFICIAL")
        if source_id in self._revoked_source_ids:
            raise EntitlementRevokedError(source_id)

        # Check tenant isolation (Fixture L)
        if network.is_private:
            if not actor_tenant_id or network.tenant_id != actor_tenant_id:
                raise SensitiveAssetAccessDeniedError(network_id, actor_tenant_id)

        return network

    def list_networks(
        self,
        sector: Optional[InfrastructureSector] = None,
        country: Optional[str] = None,
        actor_tenant_id: Optional[str] = None,
    ) -> List[InfrastructureNetwork]:
        """List networks visible to the actor tenant, excluding revoked datasets."""
        results: List[InfrastructureNetwork] = []

        for network in self._networks.values():
            source_id = network.properties.get("source_id", "OFFICIAL")
            if source_id in self._revoked_source_ids:
                continue

            if network.is_private:
                if not actor_tenant_id or network.tenant_id != actor_tenant_id:
                    continue

            if sector and network.sector != sector:
                continue

            if country and network.country != country:
                continue

            results.append(network)

        return results

    def clear(self) -> None:
        self._networks.clear()
        self._revoked_source_ids.clear()


network_registry = NetworkRegistry()

