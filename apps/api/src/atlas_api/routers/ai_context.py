"""FastAPI Router for ATLAS Stage 125: AI Context Awareness Engine.
Mounted under /ai/context.
"""

from __future__ import annotations

import logging
from typing import Annotated, List

from atlas.ai.context.capability_registry import AiContextCapabilityRegistry
from atlas.ai.context.domain import (
    AtlasAiContextEnvelope,
    AtlasAiContextItem,
    ContextMode,
    ContextType,
)
from atlas.ai.context.errors import AiContextError
from atlas.ai.context.schemas import (
    AiContextCapabilityResponse,
    AiContextPreferencesResponse,
    AiContextPreviewRequest,
    AiContextPreviewResponse,
    AiContextResolveRequest,
    AiContextResolveResponse,
    AiContextSourceManifestResponse,
    ContextExcludedItemSchema,
    ContextItemSchema,
    UpdateAiContextPreferencesRequest,
)
from atlas.ai.context.service import AiContextService
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/context", tags=["AI Context Awareness"])

_context_service = AiContextService.get_instance()


def get_context_service() -> AiContextService:
    return _context_service


def _map_context_item(item: AtlasAiContextItem) -> ContextItemSchema:
    return ContextItemSchema(
        context_item_id=item.context_item_id,
        context_type=item.context_type.value
        if hasattr(item.context_type, "value")
        else str(item.context_type),
        canonical_target_id=item.canonical_target_id,
        source_reference=item.source_reference,
        as_of=item.as_of,
        content_summary=item.content_summary,
        data_quality_status=item.data_quality_status.value
        if hasattr(item.data_quality_status, "value")
        else str(item.data_quality_status),
        provider_disclosure_status=item.provider_disclosure_status.value
        if hasattr(item.provider_disclosure_status, "value")
        else str(item.provider_disclosure_status),
        estimated_tokens=item.estimated_tokens,
        content_hash=item.content_hash,
        is_pinned=item.is_pinned,
        relevance_score=item.relevance_score,
        structured_payload=item.structured_payload,
        provenance=item.provenance,
    )


def _map_envelope(env: AtlasAiContextEnvelope) -> AiContextPreviewResponse:
    return AiContextPreviewResponse(
        context_request_id=env.context_request_id,
        context_mode=env.context_mode.value
        if hasattr(env.context_mode, "value")
        else str(env.context_mode),
        source_page=env.source_page,
        active_module=env.active_module,
        active_workspace_id=env.active_workspace_id,
        focused_panel_id=env.focused_panel_id,
        global_link_channel_id=env.global_link_channel_id,
        resolved_context_items=[_map_context_item(it) for it in env.resolved_context_items],
        excluded_items=[
            ContextExcludedItemSchema(
                target_id=e.get("target_id", ""),
                type=e.get("type", ""),
                reason=e.get("reason", "EXCLUDED"),
                detail=e.get("detail"),
            )
            for e in env.excluded_items
        ],
        total_estimated_tokens=env.total_estimated_tokens,
        token_budget=env.token_budget,
        quality_summary=env.quality_summary,
        warnings=env.warnings,
        assembled_at=env.assembled_at,
    )


@router.get("/capabilities", response_model=List[AiContextCapabilityResponse])
def get_capabilities() -> List[AiContextCapabilityResponse]:
    """Lists all registered financial context capabilities across the 20 ATLAS modules."""
    caps = AiContextCapabilityRegistry.list_capabilities()
    return [
        AiContextCapabilityResponse(
            capability_id=c.adapter_id,
            module_route=c.module_id,
            context_type=c.context_type.value
            if hasattr(c.context_type, "value")
            else str(c.context_type),
            display_name=f"{c.module_id.replace('_', ' ').title()} Context",
            description=f"Authorized context provider for {c.context_type.value}",
            sensitivity_tier=c.sensitivity_class,
            provider_disclosure_policy=c.provider_disclosure_policy.value
            if hasattr(c.provider_disclosure_policy, "value")
            else str(c.provider_disclosure_policy),
            requires_explicit_consent=c.requires_explicit_share,
        )
        for c in caps
    ]


@router.get("/preferences", response_model=AiContextPreferencesResponse)
def get_preferences(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiContextService, Depends(get_context_service)],
) -> AiContextPreferencesResponse:
    """Retrieves user AI context preferences."""
    prefs = service.get_user_preferences(
        user_id=current_user.sub,
        tenant_id=getattr(current_user, "tenant_id", None),
    )
    return AiContextPreferencesResponse(
        preference_id=prefs.preference_id,
        owner_user_id=prefs.owner_user_id,
        tenant_id=prefs.tenant_id,
        context_mode=prefs.context_mode.value
        if hasattr(prefs.context_mode, "value")
        else str(prefs.context_mode),
        allow_workspace_context=prefs.allow_workspace_context,
        allow_portfolio_holdings_context=prefs.allow_portfolio_holdings_context,
        allow_research_drafts_context=prefs.allow_research_drafts_context,
        pinned_context_references=prefs.pinned_context_references,
        excluded_context_references=prefs.excluded_context_references,
        provider_disclosure_enabled=prefs.provider_disclosure_enabled,
        created_at=str(prefs.created_at),
        updated_at=str(prefs.updated_at),
    )


@router.put("/preferences", response_model=AiContextPreferencesResponse)
def update_preferences(
    payload: UpdateAiContextPreferencesRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiContextService, Depends(get_context_service)],
) -> AiContextPreferencesResponse:
    """Updates user AI context preferences."""
    mode_enum = None
    if payload.context_mode:
        try:
            mode_enum = ContextMode[payload.context_mode.upper()]
        except KeyError:
            mode_enum = ContextMode(payload.context_mode)

    prefs = service.update_user_preferences(
        user_id=current_user.sub,
        context_mode=mode_enum,
        allow_workspace_context=payload.allow_workspace_context,
        allow_portfolio_holdings_context=payload.allow_portfolio_holdings_context,
        allow_research_drafts_context=payload.allow_research_drafts_context,
        pinned_context_references=payload.pinned_context_references,
        excluded_context_references=payload.excluded_context_references,
        provider_disclosure_enabled=payload.provider_disclosure_enabled,
    )
    return AiContextPreferencesResponse(
        preference_id=prefs.preference_id,
        owner_user_id=prefs.owner_user_id,
        tenant_id=prefs.tenant_id,
        context_mode=prefs.context_mode.value
        if hasattr(prefs.context_mode, "value")
        else str(prefs.context_mode),
        allow_workspace_context=prefs.allow_workspace_context,
        allow_portfolio_holdings_context=prefs.allow_portfolio_holdings_context,
        allow_research_drafts_context=prefs.allow_research_drafts_context,
        pinned_context_references=prefs.pinned_context_references,
        excluded_context_references=prefs.excluded_context_references,
        provider_disclosure_enabled=prefs.provider_disclosure_enabled,
        created_at=str(prefs.created_at),
        updated_at=str(prefs.updated_at),
    )


@router.post("/preview", response_model=AiContextPreviewResponse)
async def preview_context(
    payload: AiContextPreviewRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiContextService, Depends(get_context_service)],
) -> AiContextPreviewResponse:
    """Generates a dry-run context envelope preview for the Context Inspector UI."""
    mode_override = None
    if payload.context_mode_override:
        try:
            mode_override = ContextMode[payload.context_mode_override.upper()]
        except KeyError:
            mode_override = ContextMode(payload.context_mode_override)

    try:
        envelope = await service.preview_context(
            user_id=current_user.sub,
            tenant_id=getattr(current_user, "tenant_id", None),
            current_route=payload.current_route,
            active_module=payload.active_module,
            workspace_id=payload.workspace_id,
            focused_panel_id=payload.focused_panel_id,
            global_link_channel_id=payload.global_link_channel_id,
            context_mode_override=mode_override,
            requested_references=payload.requested_references,
            extra_adapter_params=payload.extra_adapter_params,
        )
        return _map_envelope(envelope)
    except AiContextError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.post("/resolve", response_model=AiContextResolveResponse)
async def resolve_item(
    payload: AiContextResolveRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiContextService, Depends(get_context_service)],
) -> AiContextResolveResponse:
    """Explicitly resolves a single typed financial context item."""
    try:
        ctype = (
            ContextType[payload.context_type.upper()]
            if hasattr(ContextType, payload.context_type.upper())
            else ContextType(payload.context_type)
        )
        item = await service.resolve_item(
            context_type=ctype,
            target_id=payload.target_id,
            user_id=current_user.sub,
            tenant_id=getattr(current_user, "tenant_id", None),
            parameters=payload.parameters,
        )
        return AiContextResolveResponse(item=_map_context_item(item))
    except AiContextError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail={"code": err.code, "message": err.message, "details": err.details},
        )


@router.get("/manifests/{generation_id}", response_model=AiContextSourceManifestResponse)
def get_manifest(
    generation_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[AiContextService, Depends(get_context_service)],
) -> AiContextSourceManifestResponse:
    """Retrieves the immutable source manifest for a completed generation run."""
    manifest = service.get_manifest_for_generation(generation_id, current_user.sub)
    if not manifest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "AI_CONTEXT_MANIFEST_NOT_FOUND",
                "message": f"Source manifest not found for generation '{generation_id}'",
            },
        )
    return AiContextSourceManifestResponse(
        manifest_id=manifest.manifest_id,
        generation_id=manifest.generation_id,
        owner_user_id=manifest.owner_user_id,
        tenant_id=manifest.tenant_id,
        context_mode=manifest.context_mode,
        source_items=manifest.source_items,
        total_estimated_tokens=manifest.total_tokens,
        assembled_at=str(getattr(manifest, "assembled_at", manifest.created_at)),
        created_at=str(manifest.created_at),
    )
