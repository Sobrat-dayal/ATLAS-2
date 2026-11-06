"""
Developer Platform and Scoped External API Service for Stage 149.
Manages developer applications, client credentials, scoped token authorization,
rate limiting, usage metering, and external ATLAS API dispatch.
"""

from __future__ import annotations

import hashlib
import secrets
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from atlas.ecosystem.domain import (
    ApiCredential,
    DeveloperApp,
    DeveloperAppStatus,
    DeveloperUsageRecord,
    utc_now,
)
from atlas.ecosystem.errors import (
    DeveloperAppNotFoundError,
    DeveloperCredentialRevokedError,
    DeveloperRateLimitExceededError,
    PermissionDeniedEcosystemError,
)

DEFAULT_RATE_LIMIT_RPM = 120  # 120 requests per minute per application


class DeveloperPlatformService:
    """
    Manages registered external developer applications, API keys, rate limits, and usage accounting.
    """

    def __init__(self) -> None:
        self._apps: Dict[str, DeveloperApp] = {}
        self._credentials: Dict[str, ApiCredential] = {}
        self._usage_records: Dict[str, DeveloperUsageRecord] = {}
        self._rate_limit_windows: Dict[str, List[float]] = {}
        self._seed_default_apps()

    def _seed_default_apps(self) -> None:
        """Seeds demo developer app for testing."""
        demo_app = DeveloperApp(
            app_id="app-institutional-client",
            developer_id="dev-demo",
            tenant_id="tenant-demo",
            name="Institutional Analytics Client",
            description="External Python/FastAPI client reading research metadata and agent status.",
            redirect_uris=("https://localhost:8443/callback",),
            allowed_scopes=("atlas.agents:read", "atlas.workflows:read", "atlas.tools:read", "atlas.research:read"),
            status=DeveloperAppStatus.ACTIVE,
        )
        self._apps[demo_app.app_id] = demo_app

    # -----------------------------------------------------------------------
    # Application Management
    # -----------------------------------------------------------------------

    def register_app(
        self,
        *,
        developer_id: str,
        tenant_id: str,
        name: str,
        description: str,
        redirect_uris: Tuple[str, ...] = (),
        allowed_scopes: Tuple[str, ...] = ("atlas.agents:read", "atlas.tools:read"),
    ) -> DeveloperApp:
        app_id = f"app-{uuid.uuid4().hex[:10]}"
        app = DeveloperApp(
            app_id=app_id,
            developer_id=developer_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            redirect_uris=redirect_uris,
            allowed_scopes=allowed_scopes,
            status=DeveloperAppStatus.ACTIVE,
        )
        self._apps[app_id] = app
        return app

    def get_app(self, app_id: str) -> DeveloperApp:
        app = self._apps.get(app_id)
        if not app:
            raise DeveloperAppNotFoundError(f"Developer App '{app_id}' was not found.")
        return app

    def list_apps(self, *, tenant_id: str) -> List[DeveloperApp]:
        return [a for a in self._apps.values() if a.tenant_id == tenant_id]

    def revoke_app(self, app_id: str) -> DeveloperApp:
        app = self.get_app(app_id)
        revoked = DeveloperApp(
            app_id=app.app_id,
            developer_id=app.developer_id,
            tenant_id=app.tenant_id,
            name=app.name,
            description=app.description,
            redirect_uris=app.redirect_uris,
            allowed_scopes=app.allowed_scopes,
            status=DeveloperAppStatus.REVOKED,
            created_at=app.created_at,
            updated_at=utc_now(),
        )
        self._apps[app_id] = revoked

        # Revoke all credentials associated with this app
        for cred_id, cred in list(self._credentials.items()):
            if cred.app_id == app_id:
                self._credentials[cred_id] = ApiCredential(
                    credential_id=cred.credential_id,
                    app_id=cred.app_id,
                    tenant_id=cred.tenant_id,
                    client_id=cred.client_id,
                    client_secret_hash=cred.client_secret_hash,
                    scopes=cred.scopes,
                    expires_at=cred.expires_at,
                    revoked_at=utc_now(),
                    created_at=cred.created_at,
                )
        return revoked

    # -----------------------------------------------------------------------
    # Scoped Credentials
    # -----------------------------------------------------------------------

    def issue_credential(
        self,
        *,
        app_id: str,
        tenant_id: str,
        scopes: Tuple[str, ...],
    ) -> Tuple[ApiCredential, str]:
        """
        Issues an API credential. Returns tuple (ApiCredential, raw_client_secret).
        The raw secret is only displayed once and stored exclusively as a SHA-256 hash.
        """
        app = self.get_app(app_id)
        if app.status != DeveloperAppStatus.ACTIVE:
            raise DeveloperAppNotFoundError(f"Cannot issue credentials for {app.status} application.")

        # Ensure requested scopes are within allowed_scopes
        for s in scopes:
            if s not in app.allowed_scopes:
                raise PermissionDeniedEcosystemError(
                    f"Requested scope '{s}' is not allowed by application registration."
                )

        client_id = f"atlas_live_{secrets.token_hex(8)}"
        raw_secret = f"sec_{secrets.token_hex(24)}"
        secret_hash = hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()

        cred_id = f"cred-{uuid.uuid4().hex[:8]}"
        cred = ApiCredential(
            credential_id=cred_id,
            app_id=app_id,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret_hash=secret_hash,
            scopes=scopes,
        )
        self._credentials[client_id] = cred
        return cred, raw_secret

    def verify_credential(self, client_id: str, raw_secret: str, required_scope: str) -> ApiCredential:
        """
        Verifies client credentials, revocation status, rate limits, and required scopes.
        """
        cred = self._credentials.get(client_id)
        if not cred or cred.revoked_at is not None:
            raise DeveloperCredentialRevokedError("Invalid or revoked developer credentials.")

        # Check App Status
        app = self._apps.get(cred.app_id)
        if not app or app.status == DeveloperAppStatus.REVOKED:
            raise DeveloperCredentialRevokedError("Application has been revoked by institutional policy.")

        # Verify hash
        expected_hash = hashlib.sha256(raw_secret.encode("utf-8")).hexdigest()
        if not secrets.compare_digest(cred.client_secret_hash, expected_hash):
            raise DeveloperCredentialRevokedError("Invalid credentials signature.")

        # Scope verification
        if required_scope not in cred.scopes:
            raise PermissionDeniedEcosystemError(
                f"Credential lacks required permission scope '{required_scope}'."
            )

        # Rate limit enforcement
        self._check_rate_limit(cred.app_id)

        return cred

    def revoke_credential(self, client_id: str) -> None:
        cred = self._credentials.get(client_id)
        if cred:
            self._credentials[client_id] = ApiCredential(
                credential_id=cred.credential_id,
                app_id=cred.app_id,
                tenant_id=cred.tenant_id,
                client_id=cred.client_id,
                client_secret_hash=cred.client_secret_hash,
                scopes=cred.scopes,
                expires_at=cred.expires_at,
                revoked_at=utc_now(),
                created_at=cred.created_at,
            )

    # -----------------------------------------------------------------------
    # Rate Limiting & Metering
    # -----------------------------------------------------------------------

    def _check_rate_limit(self, app_id: str) -> None:
        now = time.time()
        window = self._rate_limit_windows.setdefault(app_id, [])
        # Evict timestamps older than 60s
        self._rate_limit_windows[app_id] = [t for t in window if now - t < 60.0]
        if len(self._rate_limit_windows[app_id]) >= DEFAULT_RATE_LIMIT_RPM:
            raise DeveloperRateLimitExceededError(
                f"Rate limit exceeded: Max {DEFAULT_RATE_LIMIT_RPM} requests per minute."
            )
        self._rate_limit_windows[app_id].append(now)

    def record_usage(
        self,
        *,
        app_id: str,
        tenant_id: str,
        endpoint: str,
        tokens_consumed: int = 0,
        is_error: bool = False,
    ) -> None:
        key = f"{app_id}:{endpoint}"
        existing = self._usage_records.get(key)
        if existing:
            self._usage_records[key] = DeveloperUsageRecord(
                app_id=app_id,
                tenant_id=tenant_id,
                endpoint=endpoint,
                requests_count=existing.requests_count + 1,
                errors_count=existing.errors_count + (1 if is_error else 0),
                tokens_consumed=existing.tokens_consumed + tokens_consumed,
                last_invoked_at=utc_now(),
            )
        else:
            self._usage_records[key] = DeveloperUsageRecord(
                app_id=app_id,
                tenant_id=tenant_id,
                endpoint=endpoint,
                requests_count=1,
                errors_count=1 if is_error else 0,
                tokens_consumed=tokens_consumed,
                last_invoked_at=utc_now(),
            )

    def get_usage(self, *, tenant_id: str) -> List[DeveloperUsageRecord]:
        return [u for u in self._usage_records.values() if u.tenant_id == tenant_id]

