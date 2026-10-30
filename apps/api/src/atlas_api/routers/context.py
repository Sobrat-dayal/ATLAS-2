"""
FastAPI Router for ATLAS Stage 121: Global Workspace Linking.
Mounted under /context.
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional

from atlas.auth import AuthPrincipal
from atlas.context.enums import ContextScope
from atlas.context.errors import ContextLinkingError
from atlas.context.models import ContextSelectionEvent
from atlas.context.schemas import (
    ChannelResponse,
    ChannelStateResponse,
    CreateChannelRequest,
    CreateMembershipRequest,
    DispatchEventRequest,
    DispatchEventResponse,
    MembershipResponse,
    PanelCapabilityResponse,
    ResolveEntityRequest,
    ResolveEntityResponse,
    UpdateChannelRequest,
    UpdateContextStateRequest,
    UpdateMembershipRequest,
)
from atlas.context.service import ContextLinkingService
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context", tags=["Global Context & Linking"])

# Singleton service instance
_context_service = ContextLinkingService()


def get_context_service() -> ContextLinkingService:
    return _context_service


def _get_principal_user_id(principal: AuthPrincipal) -> str:
    user_id = getattr(principal, "user_id", None) or getattr(principal, "sub", None)
    if not user_id:
        return "usr_default_trader"
    return str(user_id)


# ---------------- Channel Management ----------------


@router.get("/channels", response_model=list[ChannelResponse])
async def list_channels(
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    workspace_id: Optional[str] = Query(None, description="Filter by workspace ID"),
    scope: Optional[ContextScope] = Query(None, description="Filter by context scope"),
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> list[ChannelResponse]:
    """List accessible context link channels for user, optionally filtered by workspace or scope."""
    user_id = _get_principal_user_id(principal)
    try:
        channels = service.list_channels(user_id=user_id, workspace_id=workspace_id, scope=scope)
        return [ChannelResponse(**c.to_dict()) for c in channels]
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/channels", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    payload: CreateChannelRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ChannelResponse:
    """Create a new context link channel."""
    user_id = _get_principal_user_id(principal)
    try:
        channel = service.create_channel(
            user_id=user_id,
            name=payload.name,
            display_color_token=payload.display_color_token,
            workspace_id=payload.workspace_id,
            scope=payload.scope,
            supported_dimensions=payload.supported_dimensions,
            initial_context=payload.initial_context,
        )
        return ChannelResponse(**channel.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ChannelResponse:
    """Retrieve details for a specific link channel."""
    user_id = _get_principal_user_id(principal)
    try:
        channel = service.get_channel(channel_id, user_id)
        return ChannelResponse(**channel.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    payload: UpdateChannelRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ChannelResponse:
    """Update link channel configuration."""
    user_id = _get_principal_user_id(principal)
    try:
        channel = service.update_channel(
            channel_id=channel_id,
            user_id=user_id,
            name=payload.name,
            display_color_token=payload.display_color_token,
            scope=payload.scope,
            enabled=payload.enabled,
            supported_dimensions=payload.supported_dimensions,
        )
        return ChannelResponse(**channel.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> None:
    """Delete a link channel."""
    user_id = _get_principal_user_id(principal)
    try:
        service.delete_channel(channel_id, user_id)
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ---------------- Subscription / Membership Management ----------------


@router.get("/channels/{channel_id}/memberships", response_model=list[MembershipResponse])
async def list_channel_memberships(
    channel_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> list[MembershipResponse]:
    """List panel subscriptions registered to a link channel."""
    user_id = _get_principal_user_id(principal)
    try:
        memberships = service.list_memberships(channel_id, user_id)
        return [MembershipResponse(**m.to_dict()) for m in memberships]
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/channels/{channel_id}/memberships",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_channel_membership(
    channel_id: str,
    payload: CreateMembershipRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> MembershipResponse:
    """Subscribe a panel instance to a link channel with specific dimensions."""
    user_id = _get_principal_user_id(principal)
    try:
        sub = service.add_membership(
            channel_id=channel_id,
            user_id=user_id,
            panel_instance_id=payload.panel_instance_id,
            mode=payload.mode,
            inbound_dimensions=payload.inbound_dimensions,
            outbound_dimensions=payload.outbound_dimensions,
            priority_policy=payload.priority_policy,
        )
        return MembershipResponse(**sub.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/memberships/{subscription_id}", response_model=MembershipResponse)
async def update_membership(
    subscription_id: str,
    payload: UpdateMembershipRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> MembershipResponse:
    """Update a panel instance's subscription dimensions or mode."""
    user_id = _get_principal_user_id(principal)
    try:
        sub = service.update_membership(
            subscription_id=subscription_id,
            user_id=user_id,
            mode=payload.mode,
            inbound_dimensions=payload.inbound_dimensions,
            outbound_dimensions=payload.outbound_dimensions,
            active=payload.active,
        )
        return MembershipResponse(**sub.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/memberships/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_membership(
    subscription_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> None:
    """Remove a panel subscription."""
    user_id = _get_principal_user_id(principal)
    try:
        service.remove_membership(subscription_id, user_id)
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ---------------- Context State & Synchronization ----------------


@router.get("/channels/{channel_id}/state", response_model=ChannelStateResponse)
async def get_channel_state(
    channel_id: str,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ChannelStateResponse:
    """Get active financial context snapshot for a link channel."""
    user_id = _get_principal_user_id(principal)
    try:
        state = service.get_channel_state(channel_id, user_id)
        return ChannelStateResponse(**state)
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/channels/{channel_id}/state", response_model=ChannelResponse)
async def update_channel_state(
    channel_id: str,
    payload: UpdateContextStateRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ChannelResponse:
    """Update financial context state with optimistic concurrency check."""
    user_id = _get_principal_user_id(principal)
    try:
        ch = service.update_channel_state(
            channel_id=channel_id,
            user_id=user_id,
            context_updates=payload.context_updates,
            expected_revision=payload.expected_revision,
        )
        return ChannelResponse(**ch.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# ---------------- Canonical Entity Resolution & Capabilities ----------------


@router.post("/resolve", response_model=ResolveEntityResponse)
async def resolve_entity(
    payload: ResolveEntityRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> ResolveEntityResponse:
    """Resolve a financial query to canonical entity with optional cross-domain transformation."""
    try:
        resolved = service.resolve_entity(
            query=payload.query,
            entity_type=payload.entity_type,
            target_transformation=payload.target_transformation,
        )
        return ResolveEntityResponse(**resolved.to_dict())
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/capabilities", response_model=list[PanelCapabilityResponse])
async def list_capabilities(
    panel_type_id: Optional[str] = Query(None, description="Filter by panel type ID"),
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> list[PanelCapabilityResponse]:
    """Retrieve capability definitions for all or specific panel types."""
    caps = service.get_capabilities(panel_type_id)
    return [PanelCapabilityResponse(**c.to_dict()) for c in caps]


@router.post("/events", response_model=DispatchEventResponse)
async def dispatch_event(
    payload: DispatchEventRequest,
    principal: Annotated[AuthPrincipal, Depends(get_current_user)],
    service: Annotated[ContextLinkingService, Depends(get_context_service)] = None,
) -> DispatchEventResponse:
    """Dispatch a context selection event through the channel with loop prevention and ordering."""
    user_id = _get_principal_user_id(principal)
    event = ContextSelectionEvent(
        origin_user_id=user_id,
        channel_id=payload.channel_id,
        dimension=payload.dimension,
        canonical_target_id=payload.canonical_target_id,
        target_type=payload.target_type,
        origin_panel_instance_id=payload.origin_panel_instance_id,
        causation_id=payload.causation_id,
        payload=payload.payload,
        context_revision=payload.context_revision,
        selection_reason=payload.selection_reason,
    )
    try:
        res = service.dispatch_event(event)
        return DispatchEventResponse(**res)
    except ContextLinkingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
