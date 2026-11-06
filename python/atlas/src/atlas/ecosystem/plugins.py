"""
Plugin Architecture and Installation Lifecycle Management Service for Stage 149.
Maintains plugin manifests, dependency checking, permission grant review,
enable/disable states, updates, and safe uninstalls.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from atlas.ecosystem.domain import (
    PluginInstallation,
    PluginManifest,
    PluginStatus,
    utc_now,
)
from atlas.ecosystem.errors import (
    PermissionDeniedEcosystemError,
    PluginNotFoundError,
    PluginRevokedError,
    PluginValidationError,
)


class PluginRegistryService:
    """
    Manages institutional plugin manifests and tenant installation lifecycles.
    """

    def __init__(self) -> None:
        self._plugins: Dict[str, PluginManifest] = {}
        self._installations: Dict[str, PluginInstallation] = {}
        self._seed_default_plugins()

    def _seed_default_plugins(self) -> None:
        """Seeds trusted baseline institutional plugins."""
        defaults = [
            PluginManifest(
                plugin_id="sec-filings-plugin",
                name="SEC EDGAR Intelligence Plugin",
                version="1.2.0",
                publisher="atlas-official",
                description="Enterprise SEC filings search, 10-K risk factor extraction, and XBRL facts integration.",
                manifest_version="1.0",
                compatible_atlas_versions=">=1.0.0",
                capabilities=("agent_tool", "workflow_node", "rag_connector"),
                permissions=("tools:sec_read", "storage:research_read"),
                dependencies=(),
                license="MIT",
            ),
            PluginManifest(
                plugin_id="macro-analytics-plugin",
                name="Global Macro Analytics Plugin",
                version="2.0.1",
                publisher="atlas-official",
                description="Central bank yield curves, inflation projections, and global FX rates connector.",
                manifest_version="1.0",
                compatible_atlas_versions=">=1.0.0",
                capabilities=("agent_tool", "dashboard_widget"),
                permissions=("tools:macro_read",),
                dependencies=(),
                license="Apache-2.0",
            ),
            PluginManifest(
                plugin_id="quant-backtester-connector",
                name="Quant Strategy Backtesting Exporter",
                version="1.0.0",
                publisher="quant-lab",
                description="Integrates NautilusTrader backtest results into agent decision workflows.",
                manifest_version="1.0",
                compatible_atlas_versions=">=1.0.0",
                capabilities=("workflow_node",),
                permissions=("tools:backtest_read",),
                dependencies=(),
                license="BSD-3-Clause",
            ),
        ]
        for p in defaults:
            self._plugins[p.plugin_id] = p

    # -----------------------------------------------------------------------
    # Plugin Manifest Management
    # -----------------------------------------------------------------------

    def register_plugin(
        self,
        *,
        plugin_id: str,
        name: str,
        version: str,
        publisher: str,
        description: str,
        manifest_version: str = "1.0",
        compatible_atlas_versions: str = ">=1.0.0",
        capabilities: Tuple[str, ...] = ("agent_tool",),
        permissions: Tuple[str, ...] = (),
        dependencies: Tuple[str, ...] = (),
        entrypoints: Optional[Dict[str, str]] = None,
        integrity_hash: str = "",
        license: str = "MIT",
    ) -> PluginManifest:
        if not plugin_id or not name:
            raise PluginValidationError("Plugin ID and name cannot be empty.")

        manifest = PluginManifest(
            plugin_id=plugin_id,
            name=name,
            version=version,
            publisher=publisher,
            description=description,
            manifest_version=manifest_version,
            compatible_atlas_versions=compatible_atlas_versions,
            capabilities=capabilities,
            permissions=permissions,
            dependencies=dependencies,
            entrypoints=entrypoints or {},
            integrity_hash=integrity_hash,
            license=license,
        )
        self._plugins[plugin_id] = manifest
        return manifest

    def get_plugin(self, plugin_id: str) -> PluginManifest:
        manifest = self._plugins.get(plugin_id)
        if not manifest:
            raise PluginNotFoundError(f"Plugin '{plugin_id}' was not found.")
        return manifest

    def list_plugins(self) -> List[PluginManifest]:
        return list(self._plugins.values())

    # -----------------------------------------------------------------------
    # Installation Lifecycle Management
    # -----------------------------------------------------------------------

    def install_plugin(
        self,
        *,
        plugin_id: str,
        tenant_id: str,
        owner_id: str,
        granted_permissions: Tuple[str, ...],
        configuration: Optional[Dict[str, Any]] = None,
    ) -> PluginInstallation:
        manifest = self.get_plugin(plugin_id)

        # Check dependencies
        for dep in manifest.dependencies:
            if dep not in self._plugins:
                raise PluginValidationError(f"Missing required plugin dependency: '{dep}'.")

        # Evaluate permissions
        for perm in manifest.permissions:
            if perm not in granted_permissions:
                raise PermissionDeniedEcosystemError(
                    f"Required permission '{perm}' was not granted by administrator."
                )

        inst_id = f"inst-{uuid.uuid4().hex[:8]}"
        installation = PluginInstallation(
            installation_id=inst_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            plugin_id=plugin_id,
            version=manifest.version,
            status=PluginStatus.ENABLED,
            granted_permissions=granted_permissions,
            configuration=configuration or {},
        )
        self._installations[inst_id] = installation
        return installation

    def enable_plugin(self, *, installation_id: str, tenant_id: str, owner_id: str) -> PluginInstallation:
        inst = self.get_installation(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        if inst.status == PluginStatus.REVOKED:
            raise PluginRevokedError("Cannot enable a revoked plugin installation.")
        updated = PluginInstallation(
            installation_id=inst.installation_id,
            tenant_id=inst.tenant_id,
            owner_id=inst.owner_id,
            plugin_id=inst.plugin_id,
            version=inst.version,
            status=PluginStatus.ENABLED,
            granted_permissions=inst.granted_permissions,
            configuration=inst.configuration,
            installed_at=inst.installed_at,
            updated_at=utc_now(),
        )
        self._installations[installation_id] = updated
        return updated

    def disable_plugin(self, *, installation_id: str, tenant_id: str, owner_id: str) -> PluginInstallation:
        inst = self.get_installation(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        updated = PluginInstallation(
            installation_id=inst.installation_id,
            tenant_id=inst.tenant_id,
            owner_id=inst.owner_id,
            plugin_id=inst.plugin_id,
            version=inst.version,
            status=PluginStatus.DISABLED,
            granted_permissions=inst.granted_permissions,
            configuration=inst.configuration,
            installed_at=inst.installed_at,
            updated_at=utc_now(),
        )
        self._installations[installation_id] = updated
        return updated

    def update_plugin(
        self,
        *,
        installation_id: str,
        target_version: str,
        tenant_id: str,
        owner_id: str,
    ) -> PluginInstallation:
        inst = self.get_installation(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        manifest = self.get_plugin(inst.plugin_id)

        # Check if new version requests extra permissions
        new_permissions_required = [p for p in manifest.permissions if p not in inst.granted_permissions]
        new_status = PluginStatus.AWAITING_PERMISSION if new_permissions_required else PluginStatus.ENABLED

        updated = PluginInstallation(
            installation_id=inst.installation_id,
            tenant_id=inst.tenant_id,
            owner_id=inst.owner_id,
            plugin_id=inst.plugin_id,
            version=target_version,
            status=new_status,
            granted_permissions=inst.granted_permissions,
            configuration=inst.configuration,
            installed_at=inst.installed_at,
            updated_at=utc_now(),
        )
        self._installations[installation_id] = updated
        return updated

    def uninstall_plugin(self, *, installation_id: str, tenant_id: str, owner_id: str) -> None:
        inst = self.get_installation(installation_id=installation_id, tenant_id=tenant_id, owner_id=owner_id)
        self._installations.pop(installation_id, None)

    def revoke_plugin(self, plugin_id: str) -> None:
        """Revokes a plugin globally across all tenant installations."""
        for inst_id, inst in list(self._installations.items()):
            if inst.plugin_id == plugin_id:
                self._installations[inst_id] = PluginInstallation(
                    installation_id=inst.installation_id,
                    tenant_id=inst.tenant_id,
                    owner_id=inst.owner_id,
                    plugin_id=inst.plugin_id,
                    version=inst.version,
                    status=PluginStatus.REVOKED,
                    granted_permissions=(),
                    configuration=inst.configuration,
                    installed_at=inst.installed_at,
                    updated_at=utc_now(),
                )

    def get_installation(self, *, installation_id: str, tenant_id: str, owner_id: str) -> PluginInstallation:
        inst = self._installations.get(installation_id)
        if not inst or inst.tenant_id != tenant_id or inst.owner_id != owner_id:
            raise PluginNotFoundError(f"Plugin installation '{installation_id}' was not found.")
        return inst

    def list_installations(self, *, tenant_id: str, owner_id: str) -> List[PluginInstallation]:
        return [
            i for i in self._installations.values()
            if i.tenant_id == tenant_id and i.owner_id == owner_id
        ]

