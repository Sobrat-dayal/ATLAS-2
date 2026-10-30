"""Context Assembly and Orchestration Service for Stage 125."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.ai.context.domain import (
    AiContextPreferences,
    AiContextSourceManifest,
    AtlasAiContextEnvelope,
    AtlasAiContextItem,
    ContextMode,
    ContextType,
)
from atlas.ai.context.privacy import ContextPrivacyEngine
from atlas.ai.context.registry import ContextAdapterRegistry
from atlas.ai.context.relevance import ContextRelevanceEngine
from atlas.ai.context.repository import AiContextRepository

logger = logging.getLogger(__name__)


class AiContextService:
    """Core domain service for Stage 125 Context Intelligence and Assembly."""

    _instance: Optional["AiContextService"] = None

    def __init__(
        self,
        repository: Optional[AiContextRepository] = None,
        adapter_registry: Optional[ContextAdapterRegistry] = None,
    ):
        self.repository = repository or AiContextRepository.get_instance()
        self.adapter_registry = adapter_registry or ContextAdapterRegistry.get_instance()

    @classmethod
    def get_instance(cls) -> "AiContextService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ---------------- Preferences ----------------

    def get_user_preferences(
        self, user_id: str, tenant_id: Optional[str] = None
    ) -> AiContextPreferences:
        return self.repository.get_preferences(user_id, tenant_id)

    def update_user_preferences(
        self,
        user_id: str,
        context_mode: Optional[ContextMode] = None,
        allow_workspace_context: Optional[bool] = None,
        allow_portfolio_holdings_context: Optional[bool] = None,
        allow_research_drafts_context: Optional[bool] = None,
        pinned_context_references: Optional[List[str]] = None,
        excluded_context_references: Optional[List[str]] = None,
        provider_disclosure_enabled: Optional[bool] = None,
    ) -> AiContextPreferences:
        return self.repository.update_preferences(
            owner_user_id=user_id,
            context_mode=context_mode,
            allow_workspace_context=allow_workspace_context,
            allow_portfolio_holdings_context=allow_portfolio_holdings_context,
            allow_research_drafts_context=allow_research_drafts_context,
            pinned_context_references=pinned_context_references,
            excluded_context_references=excluded_context_references,
            provider_disclosure_enabled=provider_disclosure_enabled,
        )

    # ---------------- Resolution & Assembly ----------------

    async def resolve_item(
        self,
        context_type: ContextType,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        """Resolves a single typed context item using its registered adapter."""
        adapter = self.adapter_registry.get_adapter_by_type(context_type)
        return await adapter.resolve(target_id, user_id, tenant_id, parameters)

    async def assemble_context(
        self,
        user_id: str,
        tenant_id: Optional[str],
        conversation_id: str,
        user_query: str,
        current_route: str = "/home",
        active_module: Optional[str] = None,
        workspace_id: Optional[str] = None,
        focused_panel_id: Optional[str] = None,
        global_link_channel_id: Optional[str] = None,
        context_mode_override: Optional[ContextMode] = None,
        requested_references: Optional[List[Dict[str, Any]]] = None,
        excluded_references: Optional[List[str]] = None,
        generation_id: Optional[str] = None,
        model_id: str = "atlas-intelligence-v1",
        provider_name: str = "atlas",
        token_budget: int = 8000,
        extra_adapter_params: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextEnvelope:
        """Assembles, authorizes, scores, ranks, and budgets verified financial context items."""
        prefs = self.get_user_preferences(user_id, tenant_id)
        effective_mode = context_mode_override or prefs.context_mode

        candidate_items: List[AtlasAiContextItem] = []
        excluded_reasons: List[Dict[str, Any]] = []
        warnings: List[str] = []

        # 1. Base Page Context (always resolved)
        page_adapter = self.adapter_registry.get_adapter_by_type(ContextType.PAGE_CONTEXT)
        page_item = await page_adapter.resolve(current_route, user_id, tenant_id)
        candidate_items.append(page_item)

        # If Mode is OFF, stop right here (privacy preserve)
        if effective_mode == ContextMode.OFF:
            allowed, excl = ContextPrivacyEngine.filter_by_privacy_policy(
                candidate_items, prefs, provider_name, user_id
            )
            return AtlasAiContextEnvelope(
                context_request_id=f"ctx_req_{uuid.uuid4().hex[:12]}",
                conversation_id=conversation_id,
                generation_id=generation_id,
                authenticated_user_scope=user_id,
                tenant_id=tenant_id,
                source_page=current_route,
                active_module=active_module or "home",
                context_mode=ContextMode.OFF,
                resolved_context_items=allowed,
                excluded_items=excl,
                assembled_at=datetime.now(timezone.utc).isoformat(),
                total_estimated_tokens=sum(it.estimated_tokens for it in allowed),
                token_budget=token_budget,
            )

        # 2. Workspace Context & Focused Panel (if in Workspace or Focused mode)
        if workspace_id and prefs.allow_workspace_context:
            ws_adapter = self.adapter_registry.get_adapter_by_type(ContextType.WORKSPACE_CONTEXT)
            ws_params = extra_adapter_params.get("workspace", {}) if extra_adapter_params else {}
            if focused_panel_id:
                ws_params["active_panel_id"] = focused_panel_id
            ws_item = await ws_adapter.resolve(workspace_id, user_id, tenant_id, ws_params)
            candidate_items.append(ws_item)

        # 3. Global Linking Context (if active channel provided)
        if global_link_channel_id:
            link_adapter = self.adapter_registry.get_adapter_by_type(ContextType.LINKED_CONTEXT)
            link_params = extra_adapter_params.get("linking", {}) if extra_adapter_params else {}
            link_item = await link_adapter.resolve(
                global_link_channel_id, user_id, tenant_id, link_params
            )
            candidate_items.append(link_item)

        # 4. Explicit requested references (e.g. from "Ask AI About This", or pinned references)
        all_reqs = list(requested_references or [])
        # Add pinned references from user preferences
        for pin_ref in prefs.pinned_context_references:
            if ":" in pin_ref:
                t_type, t_id = pin_ref.split(":", 1)
                all_reqs.append({"type": t_type, "target_id": t_id, "is_pinned": True})

        for req in all_reqs:
            t_type_str = req.get("type", "")
            t_id = req.get("target_id", "")
            is_pinned = req.get("is_pinned", False)
            p_params = req.get("parameters") or (
                extra_adapter_params.get(t_type_str.lower(), {}) if extra_adapter_params else {}
            )

            try:
                c_type = (
                    ContextType[t_type_str]
                    if hasattr(ContextType, t_type_str)
                    else ContextType(t_type_str)
                )
                adapter = self.adapter_registry.get_adapter_by_type(c_type)
                res_item = await adapter.resolve(t_id, user_id, tenant_id, p_params)
                res_item.is_pinned = is_pinned
                candidate_items.append(res_item)
            except Exception as exc:
                logger.warning(
                    "Failed to resolve requested context reference %s:%s: %s", t_type_str, t_id, exc
                )
                excluded_reasons.append(
                    {
                        "target_id": t_id,
                        "type": t_type_str,
                        "reason": "SOURCE_UNAVAILABLE",
                        "detail": str(exc),
                    }
                )

        # 5. Check Multi-Panel Ambiguity (Part XXXIX)
        is_ambiguous, ambig_msg, ambig_candidates = ContextRelevanceEngine.detect_ambiguity(
            user_query=user_query,
            candidate_items=candidate_items,
            focused_panel_id=focused_panel_id,
        )
        if is_ambiguous and ambig_msg:
            warnings.append(ambig_msg)

        # 6. Apply Privacy and Provider Disclosure Policies
        privacy_allowed, privacy_excluded = ContextPrivacyEngine.filter_by_privacy_policy(
            candidate_items, prefs, provider_name, user_id
        )
        excluded_reasons.extend(privacy_excluded)

        # 7. Score Relevance
        for item in privacy_allowed:
            item.relevance_score = ContextRelevanceEngine.score_context_item(
                item=item,
                user_query=user_query,
                current_route=current_route,
                focused_panel_id=focused_panel_id,
                referenced_entity_ids=[r.get("target_id", "") for r in all_reqs],
            )

        # 8. Deduplicate and Trim by Token Budget
        final_included, budget_excluded, total_tokens = ContextRelevanceEngine.rank_and_deduplicate(
            privacy_allowed, token_budget=token_budget
        )
        excluded_reasons.extend(budget_excluded)

        envelope = AtlasAiContextEnvelope(
            context_request_id=f"ctx_req_{uuid.uuid4().hex[:12]}",
            conversation_id=conversation_id,
            generation_id=generation_id,
            authenticated_user_scope=user_id,
            tenant_id=tenant_id,
            source_page=current_route,
            active_module=active_module or "home",
            active_workspace_id=workspace_id,
            focused_panel_id=focused_panel_id,
            global_link_channel_id=global_link_channel_id,
            context_mode=effective_mode,
            requested_dimensions=[r.get("type", "") for r in all_reqs],
            resolved_context_items=final_included,
            excluded_items=excluded_reasons,
            assembled_at=datetime.now(timezone.utc).isoformat(),
            total_estimated_tokens=total_tokens,
            token_budget=token_budget,
            quality_summary="COMPLETE"
            if not any(it.data_quality_status.value != "COMPLETE" for it in final_included)
            else "PARTIAL",
            warnings=warnings,
        )

        return envelope

    async def preview_context(
        self,
        user_id: str,
        tenant_id: Optional[str],
        current_route: str = "/home",
        active_module: Optional[str] = None,
        workspace_id: Optional[str] = None,
        focused_panel_id: Optional[str] = None,
        global_link_channel_id: Optional[str] = None,
        context_mode_override: Optional[ContextMode] = None,
        requested_references: Optional[List[Dict[str, Any]]] = None,
        extra_adapter_params: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextEnvelope:
        """Generates a dry-run context envelope preview for the Context Inspector UI."""
        return await self.assemble_context(
            user_id=user_id,
            tenant_id=tenant_id,
            conversation_id="preview",
            user_query="",
            current_route=current_route,
            active_module=active_module,
            workspace_id=workspace_id,
            focused_panel_id=focused_panel_id,
            global_link_channel_id=global_link_channel_id,
            context_mode_override=context_mode_override,
            requested_references=requested_references,
            token_budget=8000,
            extra_adapter_params=extra_adapter_params,
        )

    def persist_source_manifest(
        self,
        envelope: AtlasAiContextEnvelope,
        generation_id: str,
    ) -> AiContextSourceManifest:
        """Persists immutable source manifest linking this generation run to authorized context items."""
        manifest_items = [
            {
                "context_item_id": it.context_item_id,
                "context_type": it.context_type.value
                if hasattr(it.context_type, "value")
                else str(it.context_type),
                "target_id": it.canonical_target_id,
                "source_reference": it.source_reference,
                "as_of": it.as_of,
                "data_quality": it.data_quality_status.value
                if hasattr(it.data_quality_status, "value")
                else str(it.data_quality_status),
                "content_hash": it.content_hash,
                "tokens": it.estimated_tokens,
            }
            for it in envelope.resolved_context_items
        ]
        manifest = self.repository.save_manifest(
            generation_id=generation_id,
            owner_user_id=envelope.authenticated_user_scope,
            tenant_id=envelope.tenant_id,
            source_items=manifest_items,
            total_tokens=envelope.total_estimated_tokens,
            context_mode=envelope.context_mode.value
            if hasattr(envelope.context_mode, "value")
            else str(envelope.context_mode),
        )
        envelope.source_manifest_id = manifest.manifest_id
        return manifest

    def get_manifest_for_generation(
        self, generation_id: str, user_id: str
    ) -> Optional[AiContextSourceManifest]:
        return self.repository.get_manifest_by_generation_id(generation_id, user_id)

    def format_context_for_prompt(self, envelope: AtlasAiContextEnvelope) -> str:
        """Compresses all included context items into an isolated, prompt-injection defended text block."""
        summaries: List[str] = []
        for it in envelope.resolved_context_items:
            try:
                adapter = self.adapter_registry.get_adapter_by_type(it.context_type)
                summary = adapter.summarize_for_model(it)
                summaries.append(summary)
            except Exception:
                summaries.append(
                    f"[{it.context_type.value}: {it.canonical_target_id}] {it.content_summary}"
                )

        return ContextPrivacyEngine.build_isolated_context_block(summaries)
