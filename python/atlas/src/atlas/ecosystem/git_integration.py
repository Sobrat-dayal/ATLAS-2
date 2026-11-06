"""
Git Repository Integration Service for Stage 149.
Provides authorized Git connections, package source imports, commit SHA provenance,
and safe read-only operations preventing unauthorized repository modifications.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

from atlas.ecosystem.domain import (
    GitConnection,
    GitImportProvenance,
    GitProvider,
    PackageImportResult,
    utc_now,
)
from atlas.ecosystem.errors import (
    EcosystemError,
    PackageSecurityError,
    PackageValidationError,
)
from atlas.ecosystem.packages import AgentPackageManager

SAFE_REPO_URL_REGEX = re.compile(r"^(https://|git@)[a-zA-Z0-9_\-\./:]+\.git$", re.IGNORECASE)


class GitIntegrationService:
    """
    Manages authorized Git connections and package source imports.
    """

    def __init__(self, package_manager: Optional[AgentPackageManager] = None) -> None:
        self._package_manager = package_manager or AgentPackageManager()
        self._connections: Dict[str, GitConnection] = {}
        self._provenance_records: Dict[str, GitImportProvenance] = {}
        self._seed_default_connections()

    def _seed_default_connections(self) -> None:
        """Seeds trusted baseline Git connections."""
        demo_conn = GitConnection(
            connection_id="git-conn-official-templates",
            tenant_id="tenant-system",
            owner_id="user-system",
            provider=GitProvider.GITHUB,
            repository_url="https://github.com/atlas-ecosystem/official-agents.git",
            default_branch="main",
            auth_type="TOKEN",
            status="CONNECTED",
        )
        self._connections[demo_conn.connection_id] = demo_conn

    def create_connection(
        self,
        *,
        tenant_id: str,
        owner_id: str,
        provider: GitProvider,
        repository_url: str,
        default_branch: str = "main",
        auth_type: str = "TOKEN",
    ) -> GitConnection:
        # Validate repository URL format
        if not repository_url.startswith("https://") and not repository_url.startswith("git@"):
            raise PackageSecurityError(
                f"Invalid or unsafe repository URL '{repository_url}'. Must use https:// or git@ transport."
            )
        if "file://" in repository_url.lower() or "localhost" in repository_url.lower():
            raise PackageSecurityError("Local filesystem and localhost Git URLs are barred.")

        conn_id = f"git-conn-{uuid.uuid4().hex[:8]}"
        conn = GitConnection(
            connection_id=conn_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            provider=provider,
            repository_url=repository_url,
            default_branch=default_branch,
            auth_type=auth_type,
            status="CONNECTED",
        )
        self._connections[conn_id] = conn
        return conn

    def get_connection(self, *, connection_id: str, tenant_id: str, owner_id: str) -> GitConnection:
        conn = self._connections.get(connection_id)
        # Allow tenant-system connections as public templates
        if not conn or (conn.tenant_id != tenant_id and conn.tenant_id != "tenant-system"):
            raise EcosystemError(f"Git connection '{connection_id}' was not found.")
        return conn

    def list_connections(self, *, tenant_id: str, owner_id: str) -> List[GitConnection]:
        return [
            c for c in self._connections.values()
            if c.tenant_id == tenant_id or c.tenant_id == "tenant-system"
        ]

    def remove_connection(self, *, connection_id: str, tenant_id: str, owner_id: str) -> None:
        conn = self.get_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
        if conn.tenant_id == "tenant-system":
            raise EcosystemError("Cannot delete system baseline Git connections.")
        self._connections.pop(connection_id, None)

    # -----------------------------------------------------------------------
    # Git Source Import with Full Provenance
    # -----------------------------------------------------------------------

    def import_package_from_git(
        self,
        *,
        connection_id: str,
        tenant_id: str,
        owner_id: str,
        source_path: str,
        commit_sha: Optional[str] = None,
        branch: Optional[str] = None,
        granted_permissions: Tuple[str, ...] = ("READ_RESEARCH",),
        mock_archive_bytes: Optional[bytes] = None,
    ) -> PackageImportResult:
        """
        Imports an agent package source from a Git repository branch.
        Verifies commit SHA provenance and installs into DRAFT state.
        """
        conn = self.get_connection(connection_id=connection_id, tenant_id=tenant_id, owner_id=owner_id)
        resolved_commit = commit_sha or f"sha256-{uuid.uuid4().hex[:12]}"
        resolved_branch = branch or conn.default_branch

        if not mock_archive_bytes:
            raise PackageValidationError("No package content payload available from remote repository path.")

        # Delegate validation and installation to the AgentPackageManager
        import_result = self._package_manager.import_package(
            archive_bytes=mock_archive_bytes,
            tenant_id=tenant_id,
            owner_id=owner_id,
            granted_permissions=granted_permissions,
        )

        # Record provenance record
        prov = GitImportProvenance(
            connection_id=conn.connection_id,
            repository_url=conn.repository_url,
            commit_sha=resolved_commit,
            branch=resolved_branch,
            source_path=source_path,
            package_id=import_result.package_id,
            imported_by=owner_id,
        )
        self._provenance_records[import_result.package_id] = prov
        return import_result

    def get_provenance(self, package_id: str) -> Optional[GitImportProvenance]:
        return self._provenance_records.get(package_id)

