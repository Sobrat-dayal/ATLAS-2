"""
Pydantic Request and Response Schemas for ATLAS Stage 121: Global Workspace Linking.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .enums import ContextDimension, ContextScope, SubscriptionMode, TransformationType


class CreateChannelRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    display_color_token: str = Field(default="#3b82f6", max_length=32)
    workspace_id: Optional[str] = None
    scope: ContextScope = ContextScope.WORKSPACE
    supported_dimensions: Optional[list[ContextDimension]] = None
    initial_context: Optional[dict[str, Any]] = None


class UpdateChannelRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    display_color_token: Optional[str] = Field(None, max_length=32)
    scope: Optional[ContextScope] = None
    enabled: Optional[bool] = None
    supported_dimensions: Optional[list[ContextDimension]] = None


class ChannelResponse(BaseModel):
    channel_id: str
    owner_user_id: str
    workspace_id: Optional[str] = None
    scope: str
    name: str
    display_color_token: str
    enabled: bool
    supported_dimensions: list[str]
    context_snapshot: dict[str, Any]
    revision: int
    created_at: str
    updated_at: str


class CreateMembershipRequest(BaseModel):
    panel_instance_id: str
    mode: SubscriptionMode = SubscriptionMode.BIDIRECTIONAL
    inbound_dimensions: Optional[list[ContextDimension]] = None
    outbound_dimensions: Optional[list[ContextDimension]] = None
    priority_policy: str = "NORMAL"


class UpdateMembershipRequest(BaseModel):
    mode: Optional[SubscriptionMode] = None
    inbound_dimensions: Optional[list[ContextDimension]] = None
    outbound_dimensions: Optional[list[ContextDimension]] = None
    active: Optional[bool] = None


class MembershipResponse(BaseModel):
    subscription_id: str
    channel_id: str
    panel_instance_id: str
    mode: str
    inbound_dimensions: list[str]
    outbound_dimensions: list[str]
    active: bool
    priority_policy: str
    created_at: str


class UpdateContextStateRequest(BaseModel):
    context_updates: dict[str, Any]
    expected_revision: Optional[int] = None


class ChannelStateResponse(BaseModel):
    channel_id: str
    revision: int
    context: dict[str, Any]
    updated_at: str


class ResolveEntityRequest(BaseModel):
    query: str
    entity_type: str = "INSTRUMENT"
    target_transformation: Optional[TransformationType] = None


class ResolveEntityResponse(BaseModel):
    entity_id: str
    entity_type: str
    canonical_name: str
    display_name: str
    symbol: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DispatchEventRequest(BaseModel):
    channel_id: str
    dimension: ContextDimension = ContextDimension.INSTRUMENT
    canonical_target_id: str
    target_type: str = "INSTRUMENT"
    origin_panel_instance_id: Optional[str] = None
    causation_id: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)
    context_revision: int = 1
    selection_reason: str = "USER_CLICK"


class DispatchEventResponse(BaseModel):
    status: str
    event_id: str
    channel_id: str
    revision: int
    delivered_count: int
    delivered_panel_ids: list[str]


class PanelCapabilityResponse(BaseModel):
    panel_type_id: str
    publishable_dimensions: list[str]
    subscribable_dimensions: list[str]
    accepted_entity_types: list[str]
    required_transformations: dict[str, str]
    supported_timeframes: list[str]
    supports_as_of: bool
    supports_currency: bool

