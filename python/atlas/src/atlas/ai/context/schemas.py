"""Pydantic request and response schemas for Stage 125 ATLAS AI Context Awareness."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AiContextPreferencesResponse(BaseModel):
    preference_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    context_mode: str
    allow_workspace_context: bool
    allow_portfolio_holdings_context: bool
    allow_research_drafts_context: bool
    pinned_context_references: List[str]
    excluded_context_references: List[str]
    provider_disclosure_enabled: bool
    created_at: str
    updated_at: str


class UpdateAiContextPreferencesRequest(BaseModel):
    context_mode: Optional[str] = Field(None, description="OFF, FOCUSED, WORKSPACE, or CUSTOM")
    allow_workspace_context: Optional[bool] = None
    allow_portfolio_holdings_context: Optional[bool] = None
    allow_research_drafts_context: Optional[bool] = None
    pinned_context_references: Optional[List[str]] = None
    excluded_context_references: Optional[List[str]] = None
    provider_disclosure_enabled: Optional[bool] = None


class ContextItemSchema(BaseModel):
    context_item_id: str
    context_type: str
    canonical_target_id: str
    source_reference: str
    as_of: Optional[str] = None
    content_summary: str
    data_quality_status: str
    provider_disclosure_status: str
    estimated_tokens: int
    content_hash: str
    is_pinned: bool = False
    relevance_score: float = 0.0
    structured_payload: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)


class ContextExcludedItemSchema(BaseModel):
    target_id: str
    type: str
    reason: str
    detail: Optional[str] = None


class AiContextPreviewRequest(BaseModel):
    current_route: str = Field("/home", description="Active frontend route path")
    active_module: Optional[str] = Field(None, description="Canonical ATLAS module key")
    workspace_id: Optional[str] = Field(None, description="Stage 120 Workspace ID")
    focused_panel_id: Optional[str] = Field(None, description="Focused panel ID")
    global_link_channel_id: Optional[str] = Field(None, description="Stage 121 Link channel ID")
    context_mode_override: Optional[str] = Field(None, description="Optional override for preview")
    requested_references: Optional[List[Dict[str, Any]]] = Field(
        None, description="List of explicit {type, target_id} references"
    )
    extra_adapter_params: Optional[Dict[str, Any]] = Field(
        None, description="Extra context parameters"
    )


class AiContextPreviewResponse(BaseModel):
    context_request_id: str
    context_mode: str
    source_page: str
    active_module: str
    active_workspace_id: Optional[str] = None
    focused_panel_id: Optional[str] = None
    global_link_channel_id: Optional[str] = None
    resolved_context_items: List[ContextItemSchema]
    excluded_items: List[ContextExcludedItemSchema]
    total_estimated_tokens: int
    token_budget: int
    quality_summary: str
    warnings: List[str] = Field(default_factory=list)
    assembled_at: str


class AiContextResolveRequest(BaseModel):
    context_type: str = Field(..., description="ContextType enum value (e.g. INSTRUMENT_CONTEXT)")
    target_id: str = Field(..., description="Target identifier (e.g. AAPL, c_aapl, p_100)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AiContextResolveResponse(BaseModel):
    item: ContextItemSchema


class AiContextCapabilityResponse(BaseModel):
    capability_id: str
    module_route: str
    context_type: str
    display_name: str
    description: str
    sensitivity_tier: str
    provider_disclosure_policy: str
    requires_explicit_consent: bool


class AiContextSourceManifestResponse(BaseModel):
    manifest_id: str
    generation_id: str
    owner_user_id: str
    tenant_id: Optional[str] = None
    context_mode: str
    source_items: List[Dict[str, Any]]
    total_estimated_tokens: int
    assembled_at: str
    created_at: str
