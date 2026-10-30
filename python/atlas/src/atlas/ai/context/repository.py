"""Thread-safe Repository for Stage 125 AI Context Preferences & Source Manifests."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.ai.context.domain import AiContextPreferences, AiContextSourceManifest, ContextMode
from atlas.ai.context.errors import (
    AiContextManifestAccessDeniedError,
    AiContextManifestNotFoundError,
)


class AiContextRepository:
    """In-memory and persistence repository for context preferences and manifests."""

    _instance: Optional["AiContextRepository"] = None

    def __init__(self):
        self._lock = threading.RLock()
        self._preferences: Dict[str, AiContextPreferences] = {}  # user_id -> preferences
        self._manifests: Dict[str, AiContextSourceManifest] = {}  # generation_id -> manifest
        self._manifest_lookup: Dict[str, AiContextSourceManifest] = {}  # manifest_id -> manifest
        self._audit_events: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "AiContextRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_preferences(
        self, owner_user_id: str, tenant_id: Optional[str] = None
    ) -> AiContextPreferences:
        with self._lock:
            if owner_user_id not in self._preferences:
                pref_id = f"ctx_pref_{uuid.uuid4().hex[:12]}"
                now_str = datetime.now(timezone.utc).isoformat()
                self._preferences[owner_user_id] = AiContextPreferences(
                    preference_id=pref_id,
                    owner_user_id=owner_user_id,
                    tenant_id=tenant_id,
                    context_mode=ContextMode.FOCUSED,
                    allow_workspace_context=True,
                    allow_portfolio_holdings_context=False,
                    allow_research_drafts_context=False,
                    pinned_context_references=[],
                    excluded_context_references=[],
                    provider_disclosure_enabled=True,
                    created_at=now_str,
                    updated_at=now_str,
                )
            return self._preferences[owner_user_id]

    def update_preferences(
        self,
        owner_user_id: str,
        context_mode: Optional[ContextMode] = None,
        allow_workspace_context: Optional[bool] = None,
        allow_portfolio_holdings_context: Optional[bool] = None,
        allow_research_drafts_context: Optional[bool] = None,
        pinned_context_references: Optional[List[str]] = None,
        excluded_context_references: Optional[List[str]] = None,
        provider_disclosure_enabled: Optional[bool] = None,
    ) -> AiContextPreferences:
        with self._lock:
            prefs = self.get_preferences(owner_user_id)
            if context_mode is not None:
                prefs.context_mode = context_mode
            if allow_workspace_context is not None:
                prefs.allow_workspace_context = allow_workspace_context
            if allow_portfolio_holdings_context is not None:
                prefs.allow_portfolio_holdings_context = allow_portfolio_holdings_context
            if allow_research_drafts_context is not None:
                prefs.allow_research_drafts_context = allow_research_drafts_context
            if pinned_context_references is not None:
                prefs.pinned_context_references = pinned_context_references
            if excluded_context_references is not None:
                prefs.excluded_context_references = excluded_context_references
            if provider_disclosure_enabled is not None:
                prefs.provider_disclosure_enabled = provider_disclosure_enabled
            prefs.updated_at = datetime.now(timezone.utc).isoformat()

            self.record_audit_event(
                owner_user_id=owner_user_id,
                event_type="CONTEXT_PREFERENCES_UPDATED",
                payload={"mode": prefs.context_mode.value},
            )
            return prefs

    def save_manifest(
        self,
        generation_id: str,
        owner_user_id: str,
        tenant_id: Optional[str],
        source_items: List[Dict[str, Any]],
        total_tokens: int,
        context_mode: str,
    ) -> AiContextSourceManifest:
        with self._lock:
            manifest_id = f"man_{uuid.uuid4().hex[:14]}"
            manifest = AiContextSourceManifest(
                manifest_id=manifest_id,
                generation_id=generation_id,
                owner_user_id=owner_user_id,
                tenant_id=tenant_id,
                source_items=source_items,
                total_tokens=total_tokens,
                context_mode=context_mode,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._manifests[generation_id] = manifest
            self._manifest_lookup[manifest_id] = manifest

            self.record_audit_event(
                owner_user_id=owner_user_id,
                event_type="CONTEXT_MANIFEST_CREATED",
                payload={
                    "manifest_id": manifest_id,
                    "generation_id": generation_id,
                    "items": len(source_items),
                },
            )
            return manifest

    def get_manifest_by_generation_id(
        self, generation_id: str, user_id: str
    ) -> Optional[AiContextSourceManifest]:
        with self._lock:
            m = self._manifests.get(generation_id)
            if not m:
                return None
            if m.owner_user_id != user_id:
                raise AiContextManifestAccessDeniedError(m.manifest_id)
            return m

    def get_manifest_by_id(self, manifest_id: str, user_id: str) -> AiContextSourceManifest:
        with self._lock:
            m = self._manifest_lookup.get(manifest_id)
            if not m:
                raise AiContextManifestNotFoundError(manifest_id)
            if m.owner_user_id != user_id:
                raise AiContextManifestAccessDeniedError(manifest_id)
            return m

    def record_audit_event(
        self,
        owner_user_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            self._audit_events.append(
                {
                    "audit_id": f"audit_{uuid.uuid4().hex[:12]}",
                    "owner_user_id": owner_user_id,
                    "event_type": event_type,
                    "payload": payload or {},
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )
