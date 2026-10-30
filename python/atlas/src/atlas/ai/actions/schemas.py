"""Pydantic schemas and DTOs for ATLAS AI Financial Action Engine (Stage 128, Part LXXV)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionCapabilityDTO(BaseModel):
    """Capability information for a supported financial action."""

    action_type: str = Field(..., description="Canonical action type identifier")
    action_version: str = Field("1.0.0", description="Action schema version")
    target_module: str = Field(
        ..., description="Target module (charts, screeners, portfolios, risk)"
    )
    classification: str = Field(
        ..., description="Action classification (READ_ONLY, SESSION_UI_CHANGE, etc.)"
    )
    approval_policy: str = Field(..., description="Approval requirement policy")
    reversibility_policy: str = Field(..., description="Reversibility policy")
    description: str = Field(..., description="Human-readable description of the action")
    parameters_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON schema of arguments"
    )


class ActionCapabilitiesResponse(BaseModel):
    """Response containing all available AI financial action capabilities."""

    capabilities: List[ActionCapabilityDTO]
    total_count: int


class CreateActionPlanRequest(BaseModel):
    """Request to parse intent, resolve context, and build an action plan."""

    intent: str = Field(..., description="Natural-language action request from user")
    conversation_id: Optional[str] = Field(None, description="Current conversation ID")
    context_hints: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional explicit context overrides (e.g. active_chart_id, portfolio_id)",
    )


class ActionDiffDTO(BaseModel):
    """DTO for a single field diff in an action preview."""

    field_path: str
    before_value: Any
    after_value: Any
    change_type: str = "MODIFY"
    validation_status: str = "VALID"
    financial_impact_if_computable: Optional[str] = None


class ActionPreviewDTO(BaseModel):
    """DTO for an action preview."""

    preview_id: str
    action_id: str
    target_resource_type: str
    target_resource_id: str
    current_state: Dict[str, Any]
    proposed_state: Dict[str, Any]
    diffs: List[ActionDiffDTO]
    financial_assumptions: List[str]
    estimated_cost: str
    approval_policy: str
    reversibility_policy: str
    preview_hash: str
    created_at: str
    expires_at: str


class ActionDTO(BaseModel):
    """DTO for an individual planned action."""

    action_id: str
    action_type: str
    action_version: str
    target_module: str
    target_resource_type: str
    target_resource_id: str
    actor_user_id: str
    tenant_scope: str
    proposed_arguments: Dict[str, Any]
    normalized_arguments_hash: str
    expected_resource_revision: str
    classification: str
    approval_policy: str
    reversibility_policy: str
    action_status: str
    preview: Optional[ActionPreviewDTO] = None
    created_at: str
    expires_at: Optional[str] = None


class ActionPlanResponse(BaseModel):
    """Response containing a validated action plan."""

    plan_id: str
    owner_user_id: str
    tenant_id: str
    user_intent: str
    actions: List[ActionDTO]
    dependency_graph: Dict[str, List[str]]
    conversation_id: Optional[str] = None
    status: str
    created_at: str
    expires_at: Optional[str] = None


class ActionApprovalRequest(BaseModel):
    """Request from user to approve a planned action."""

    action_id: str
    preview_hash: str = Field(..., description="Hash of the preview the user agreed to")
    expected_resource_revision: str = Field(
        ..., description="Expected revision at time of approval"
    )


class ActionApprovalResponse(BaseModel):
    """Response indicating action approval status."""

    approval_id: str
    action_id: str
    status: str
    approved_at: str
    expires_at: str


class ActionDenialRequest(BaseModel):
    """Request from user to deny a planned action."""

    action_id: str
    reason: Optional[str] = None


class ActionDenialResponse(BaseModel):
    """Response indicating action denial."""

    action_id: str
    status: str = "DENIED"
    denied_at: str
    reason: Optional[str] = None


class ExecuteActionPlanRequest(BaseModel):
    """Request to execute an approved action plan."""

    plan_id: str
    idempotency_key: str = Field(
        ..., description="Unique client key preventing duplicate execution"
    )


class ExecutionReceiptDTO(BaseModel):
    """DTO for an immutable execution receipt."""

    receipt_id: str
    action_id: str
    plan_id: str
    tool_call_id: Optional[str] = None
    actor_user_id: str
    target_resource_id: str
    target_revision_before: str
    target_revision_after: str
    operation_status: str
    started_at: str
    completed_at: str
    result_reference: Dict[str, Any] = Field(default_factory=dict)
    diffs: List[ActionDiffDTO] = Field(default_factory=list)
    source_manifest_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    undo_reference: Optional[str] = None


class ExecuteActionPlanResponse(BaseModel):
    """Response returned upon execution completion or submission."""

    plan_id: str
    status: str
    executed_actions: int
    receipts: List[ExecutionReceiptDTO]
    is_partially_completed: bool = False
    error: Optional[str] = None


class ExecutionStatusResponse(BaseModel):
    """Current status of an action execution."""

    execution_id: str
    plan_id: str
    status: str
    progress_percentage: float = 0.0
    current_step: Optional[str] = None
    receipts: List[ExecutionReceiptDTO] = Field(default_factory=list)


class CancelExecutionResponse(BaseModel):
    """Response for a cancelled execution."""

    execution_id: str
    status: str = "CANCELLED"
    cancelled_at: str
    reason: str


class UndoActionRequest(BaseModel):
    """Request to undo a reversible action."""

    action_id: str
    receipt_id: Optional[str] = None


class UndoActionResponse(BaseModel):
    """Response for an action undo operation."""

    action_id: str
    status: str = "RESTORED"
    restored_revision: str
    receipt_id: str
    undone_at: str


class ActionHistoryItemDTO(BaseModel):
    """Summary item in user action history."""

    action_id: str
    plan_id: str
    action_type: str
    target_module: str
    target_resource_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    receipt_id: Optional[str] = None
    is_reversible: bool = False


class ActionHistoryResponse(BaseModel):
    """Response containing user's authorized action history."""

    history: List[ActionHistoryItemDTO]
    total_count: int
