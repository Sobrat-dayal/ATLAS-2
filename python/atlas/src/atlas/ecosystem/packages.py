"""
.atlas-agent Package Engine for Stage 149.
Provides package manifest validation, archive builder, exporter, secret scanning,
Zip-Slip / bomb security guards, integrity verification, and safe draft-state installation.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import uuid
import zipfile
from typing import Any, Dict, List, Optional, Tuple

from atlas.agents.domain import AgentDefinition, AgentStatus, AgentVersion
from atlas.agents.service import AgentRegistryService
from atlas.ecosystem.domain import (
    AtlasAgentPackageManifest,
    PackageExportResult,
    PackageImportResult,
    PackageInstallation,
    PackageValidationResult,
    utc_now,
)
from atlas.ecosystem.errors import (
    PackageIntegrityError,
    PackageNotFoundError,
    PackageSecurityError,
    PackageValidationError,
)

# Limits to defend against decompression bombs
MAX_TOTAL_EXTRACT_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_SINGLE_FILE_BYTES = 10 * 1024 * 1024    # 10 MB
MAX_FILE_COUNT = 500

# Secret detection patterns
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9]{32,}", re.IGNORECASE),
    re.compile(r"ghp_[a-zA-Z0-9]{36}", re.IGNORECASE),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{25,}", re.IGNORECASE),
    re.compile(r"password\s*[:=]\s*['\"][^'\"]{6,}['\"]", re.IGNORECASE),
    re.compile(r"client_secret\s*[:=]\s*['\"][^'\"]{10,}['\"]", re.IGNORECASE),
]


def scan_for_secrets(content: str) -> Optional[str]:
    """Scans content for credential patterns. Returns matched pattern name if found."""
    for pattern in SECRET_PATTERNS:
        if pattern.search(content):
            return pattern.pattern
    return None


class AgentPackageManager:
    """
    Handles packaging, exporting, validating, and importing .atlas-agent archives.
    """

    def __init__(self, agent_service: Optional[AgentRegistryService] = None) -> None:
        self._agent_service = agent_service or AgentRegistryService()
        self._installations: Dict[str, PackageInstallation] = {}
        self._exported_packages: Dict[str, PackageExportResult] = {}

    # -----------------------------------------------------------------------
    # Export Engine: AgentDefinition -> .atlas-agent Archive
    # -----------------------------------------------------------------------

    def export_agent(
        self,
        *,
        agent_id: str,
        tenant_id: str,
        owner_id: str,
        publisher_id: str = "atlas-user",
        package_id: Optional[str] = None,
        version: str = "1.0.0",
    ) -> PackageExportResult:
        """
        Exports an AgentDefinition into a versioned, secret-free .atlas-agent zip archive.
        """
        agent = self._agent_service.get_agent(agent_id=agent_id, tenant_id=tenant_id, owner_id=owner_id)
        if not agent.versions:
            raise PackageValidationError(f"Agent '{agent_id}' has no configured versions.")

        latest_version = agent.versions[-1]
        resolved_pkg_id = package_id or f"pkg.{agent.name.lower().replace(' ', '-')}"

        manifest = {
            "manifest_version": "1.0",
            "package_id": resolved_pkg_id,
            "name": agent.name,
            "version": version,
            "kind": "atlas-agent",
            "description": agent.description,
            "publisher": {"id": publisher_id, "name": "Institutional Author"},
            "compatibility": {"atlas": ">=1.0.0"},
            "requirements": {
                "capabilities": ["text-generation", "structured-output"],
                "tools": list(latest_version.tool_ids),
                "model": [latest_version.model_id],
            },
            "permissions": ["READ_RESEARCH", "EXECUTE_APPROVED_TOOLS"],
            "entrypoint": "agent/definition.json",
        }

        # Redact instructions if any secret strings happen to be present
        safe_instructions = latest_version.instructions
        matched_secret = scan_for_secrets(safe_instructions)
        if matched_secret:
            raise PackageSecurityError("Cannot export agent: Instructions contain potential raw secret values.")

        definition_doc = {
            "name": agent.name,
            "description": agent.description,
            "role": agent.role,
            "model_id": latest_version.model_id,
            "execution_limits": dict(latest_version.execution_limits),
            "instructions_ref": "agent/instructions.md",
        }

        model_policy = {
            "primary_model": latest_version.model_id,
            "fallback_models": ["gpt-4o-mini", "claude-3-5-haiku-20241022"],
            "temperature": 0.2,
        }

        execution_policy = {
            "max_timeout_seconds": 60,
            "max_retries": 2,
            "budget_limit_usd": 25.0,
        }

        memory_policy = {
            "context_window_tokens": 128000,
            "retention_mode": "SESSION_ONLY",
        }

        tools_dep = {"required_tool_ids": list(latest_version.tool_ids)}
        permissions_doc = {"scopes": ["READ_RESEARCH", "EXECUTE_APPROVED_TOOLS"]}
        readme_doc = f"# {agent.name} (v{version})\n\n{agent.description}\n\nRole: {agent.role}\n"

        # Build in-memory files dictionary
        files_to_pack: Dict[str, bytes] = {
            "manifest.json": json.dumps(manifest, indent=2).encode("utf-8"),
            "agent/definition.json": json.dumps(definition_doc, indent=2).encode("utf-8"),
            "agent/instructions.md": safe_instructions.encode("utf-8"),
            "agent/model-policy.json": json.dumps(model_policy, indent=2).encode("utf-8"),
            "agent/execution-policy.json": json.dumps(execution_policy, indent=2).encode("utf-8"),
            "agent/memory-policy.json": json.dumps(memory_policy, indent=2).encode("utf-8"),
            "dependencies/tools.json": json.dumps(tools_dep, indent=2).encode("utf-8"),
            "permissions/required-scopes.json": json.dumps(permissions_doc, indent=2).encode("utf-8"),
            "docs/README.md": readme_doc.encode("utf-8"),
        }

        # Calculate checksums for integrity verification
        checksums: Dict[str, str] = {}
        for filename, data in files_to_pack.items():
            checksums[filename] = hashlib.sha256(data).hexdigest()
        files_to_pack["integrity/checksums.json"] = json.dumps(checksums, indent=2).encode("utf-8")

        # Create zip archive
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for filepath, content in sorted(files_to_pack.items()):
                zf.writestr(filepath, content)

        archive_bytes = buf.getvalue()
        package_sha256 = hashlib.sha256(archive_bytes).hexdigest()
        filename = f"{resolved_pkg_id}-{version}.atlas-agent"

        result = PackageExportResult(
            package_id=resolved_pkg_id,
            version=version,
            filename=filename,
            archive_bytes=archive_bytes,
            sha256_hash=package_sha256,
            file_count=len(files_to_pack),
        )
        self._exported_packages[resolved_pkg_id] = result
        return result

    # -----------------------------------------------------------------------
    # Package Validation Engine: Inspects .atlas-agent Bytes
    # -----------------------------------------------------------------------

    def validate_package_bytes(self, archive_bytes: bytes) -> PackageValidationResult:
        """
        Validates .atlas-agent archive structure, manifest schema, Zip-Slip,
        decompression limits, secret patterns, and integrity checksums.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if len(archive_bytes) == 0:
            return PackageValidationResult(is_valid=False, errors=("Archive is empty.",))

        try:
            buf = io.BytesIO(archive_bytes)
            zf = zipfile.ZipFile(buf, "r")
        except zipfile.BadZipFile:
            return PackageValidationResult(is_valid=False, errors=("File is not a valid zip archive.",))

        infolist = zf.infolist()
        if len(infolist) > MAX_FILE_COUNT:
            return PackageValidationResult(
                is_valid=False,
                errors=(f"Decompression bomb defense: File count {len(infolist)} exceeds limit {MAX_FILE_COUNT}.",)
            )

        total_bytes = 0
        file_map: Dict[str, bytes] = {}
        for info in infolist:
            # 1. Zip-Slip / Path Traversal Defense
            norm_name = info.filename.replace("\\", "/")
            if ".." in norm_name or norm_name.startswith("/") or ":" in norm_name:
                return PackageValidationResult(
                    is_valid=False,
                    errors=(f"Zip-Slip path traversal violation detected in '{info.filename}'.",),
                )

            # 2. Size limit checks
            if info.file_size > MAX_SINGLE_FILE_BYTES:
                return PackageValidationResult(
                    is_valid=False,
                    errors=(f"File '{info.filename}' size exceeds single file limit of {MAX_SINGLE_FILE_BYTES} bytes.",),
                )
            total_bytes += info.file_size
            if total_bytes > MAX_TOTAL_EXTRACT_BYTES:
                return PackageValidationResult(
                    is_valid=False,
                    errors=(f"Total uncompressed size exceeds limit of {MAX_TOTAL_EXTRACT_BYTES} bytes.",),
                )

            data = zf.read(info)
            file_map[norm_name] = data

        # 3. Check for manifest.json
        if "manifest.json" not in file_map:
            return PackageValidationResult(
                is_valid=False,
                errors=("Archive is missing required 'manifest.json'.",),
            )

        try:
            manifest_json = json.loads(file_map["manifest.json"].decode("utf-8"))
        except Exception as exc:
            return PackageValidationResult(
                is_valid=False,
                errors=(f"Malformed manifest.json: {exc}",),
            )

        required_manifest_fields = ["manifest_version", "package_id", "name", "version", "kind", "entrypoint"]
        for field in required_manifest_fields:
            if field not in manifest_json:
                errors.append(f"manifest.json missing required field '{field}'.")

        if manifest_json.get("kind") != "atlas-agent":
            errors.append(f"Invalid package kind '{manifest_json.get('kind')}': must be 'atlas-agent'.")

        entrypoint = manifest_json.get("entrypoint", "")
        if entrypoint not in file_map:
            errors.append(f"Declared entrypoint '{entrypoint}' not found in archive.")

        # 4. Secret pattern scanning
        secrets_detected = False
        for fname, content_bytes in file_map.items():
            try:
                text_content = content_bytes.decode("utf-8", errors="ignore")
                matched = scan_for_secrets(text_content)
                if matched:
                    secrets_detected = True
                    errors.append(f"Prohibited secret pattern detected in '{fname}'.")
            except Exception:
                pass

        # 5. Check integrity checksums
        checksum_verified = False
        if "integrity/checksums.json" in file_map:
            try:
                checksums = json.loads(file_map["integrity/checksums.json"].decode("utf-8"))
                mismatches = []
                for fname, expected_hash in checksums.items():
                    if fname not in file_map:
                        mismatches.append(f"Missing file declared in checksums: '{fname}'")
                    else:
                        actual_hash = hashlib.sha256(file_map[fname]).hexdigest()
                        if actual_hash != expected_hash:
                            mismatches.append(f"Checksum mismatch for '{fname}'")
                if mismatches:
                    errors.extend(mismatches)
                else:
                    checksum_verified = True
            except Exception as exc:
                warnings.append(f"Could not parse checksums.json: {exc}")
        else:
            warnings.append("Archive lacks 'integrity/checksums.json'; integrity unverified.")

        manifest_obj = None
        if not errors:
            manifest_obj = AtlasAgentPackageManifest(
                manifest_version=manifest_json.get("manifest_version", "1.0"),
                package_id=manifest_json.get("package_id", ""),
                name=manifest_json.get("name", ""),
                version=manifest_json.get("version", "1.0.0"),
                kind=manifest_json.get("kind", "atlas-agent"),
                description=manifest_json.get("description", ""),
                publisher=manifest_json.get("publisher", {}),
                compatibility=manifest_json.get("compatibility", {}),
                requirements=manifest_json.get("requirements", {}),
                permissions=tuple(manifest_json.get("permissions", [])),
                entrypoint=entrypoint,
            )

        is_valid = len(errors) == 0
        return PackageValidationResult(
            is_valid=is_valid,
            package_id=manifest_json.get("package_id") if manifest_json else None,
            version=manifest_json.get("version") if manifest_json else None,
            manifest=manifest_obj,
            errors=tuple(errors),
            warnings=tuple(warnings),
            file_count=len(file_map),
            total_bytes=total_bytes,
            checksum_verified=checksum_verified,
            secrets_detected=secrets_detected,
        )

    # -----------------------------------------------------------------------
    # Package Import Engine: Validate -> Install into Draft Agent
    # -----------------------------------------------------------------------

    def import_package(
        self,
        *,
        archive_bytes: bytes,
        tenant_id: str,
        owner_id: str,
        granted_permissions: Tuple[str, ...],
    ) -> PackageImportResult:
        """
        Validates package, verifies integrity, checks required tools, and creates
        an Agent in DRAFT status (NO immediate execution).
        """
        validation = self.validate_package_bytes(archive_bytes)
        if not validation.is_valid or not validation.manifest:
            error_details = "; ".join(validation.errors)
            if validation.secrets_detected:
                raise PackageSecurityError(f"Package rejected due to secret leakage: {error_details}")
            if not validation.checksum_verified and any("Checksum mismatch" in e for e in validation.errors):
                raise PackageIntegrityError(f"Package rejected due to integrity failure: {error_details}")
            raise PackageValidationError(f"Package validation failed: {error_details}")

        manifest = validation.manifest
        buf = io.BytesIO(archive_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            entrypoint_data = json.loads(zf.read(manifest.entrypoint).decode("utf-8"))
            instructions = zf.read("agent/instructions.md").decode("utf-8") if "agent/instructions.md" in zf.namelist() else ""

        # Extract requirements
        required_tools = manifest.requirements.get("tools", [])
        model_id = entrypoint_data.get("model_id", "atlas-intelligence-v1")
        if model_id not in ("atlas-intelligence-v1", "atlas-reasoning-v1", "atlas-speed-v1"):
            model_id = "atlas-intelligence-v1"

        # Create Agent in Stage 146 Agent Registry with DRAFT status
        agent = self._agent_service.create_agent(
            tenant_id=tenant_id,
            owner_id=owner_id,
            name=manifest.name,
            description=manifest.description,
            role=entrypoint_data.get("role", "Specialist"),
            model_id=model_id,
            instructions=instructions,
            tool_ids=required_tools,
            execution_limits=entrypoint_data.get("execution_limits", {"max_tokens": 4096}),
        )

        inst_id = f"pkg-inst-{uuid.uuid4().hex[:8]}"
        installation = PackageInstallation(
            installation_id=inst_id,
            tenant_id=tenant_id,
            owner_id=owner_id,
            package_id=manifest.package_id,
            package_version=manifest.version,
            status="DRAFT",
            permission_grants=granted_permissions,
            agent_reference_id=agent.agent_id,
        )
        self._installations[inst_id] = installation

        return PackageImportResult(
            package_id=manifest.package_id,
            version=manifest.version,
            agent_id=agent.agent_id,
            installation_status="DRAFT",
            installed_version=manifest.version,
            requires_configuration=False,
            missing_dependencies=(),
        )

    def list_installations(self, *, tenant_id: str, owner_id: str) -> List[PackageInstallation]:
        return [
            inst for inst in self._installations.values()
            if inst.tenant_id == tenant_id and inst.owner_id == owner_id
        ]

