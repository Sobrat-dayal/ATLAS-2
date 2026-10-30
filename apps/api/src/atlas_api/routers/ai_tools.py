"""FastAPI Router for ATLAS Stage 126: Secure AI Tool Gateway.
Mounted under /ai/tools.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated, Dict, Optional

from atlas.ai.tools.approval import AiToolApprovalEngine
from atlas.ai.tools.dispatcher import AiToolDispatcher
from atlas.ai.tools.domain import (
    AiToolUserPreferences,
    AtlasAiToolDefinition,
)
from atlas.ai.tools.errors import (
    AiToolApprovalDeniedError,
    AiToolApprovalExpiredError,
    AiToolApprovalMismatchError,
    AiToolApprovalRequiredError,
    AiToolError,
    AiToolNotAuthorizedError,
    AiToolNotFoundError,
    AiToolResourceAccessDeniedError,
    AiToolSequenceLimitExceededError,
    AiToolTimeoutError,
)
from atlas.ai.tools.registry import AtlasAiToolRegistry
from atlas.ai.tools.schemas import (
    AiToolApprovalActionRequest,
    AiToolApprovalResponse,
    AiToolCallListResponse,
    AiToolCallResponse,
    AiToolDescriptorResponse,
    AiToolExecuteRequest,
    AiToolExecuteResponse,
    AiToolListResponse,
    AiToolPreferencesResponse,
    AiToolPreferencesUpdateRequest,
)
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/tools", tags=["AI Tool Gateway"])

# In-memory user preferences store for fast lookups
_USER_PREFERENCES: Dict[str, AiToolUserPreferences] = {}


def _get_user_preferences(user_id: str) -> AiToolUserPreferences:
    if user_id not in _USER_PREFERENCES:
        _USER_PREFERENCES[user_id] = AiToolUserPreferences(
            user_id=user_id,
            enabled_tools=[],
            disabled_tools=[],
            auto_approve_read_only=True,
            require_approval_for_sensitive=True,
        )
    return _USER_PREFERENCES[user_id]


def _map_tool_descriptor(tool: AtlasAiToolDefinition) -> AiToolDescriptorResponse:
    return AiToolDescriptorResponse(
        tool_id=tool.tool_id,
        version=tool.version,
        category=tool.category.value,
        name=tool.name,
        description=tool.description,
        capability_scope=tool.capability_scope.value,
        approval_class=tool.approval_class.value,
        provider_disclosure_policy=tool.provider_disclosure_policy.value,
        parameters_schema=tool.parameters_schema,
        returns_schema=tool.returns_schema,
        lifecycle_status=tool.lifecycle_status.value,
        timeout_seconds=tool.timeout_seconds,
        rate_limit_per_minute=tool.rate_limit_per_minute,
    )


@router.get("", response_model=AiToolListResponse)
async def list_tools(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    category: Optional[str] = Query(None, description="Filter by tool category"),
    include_disabled: bool = Query(False, description="Include disabled tools"),
) -> AiToolListResponse:
    """Lists registered AI tools with operational metadata and schemas."""
    registry = AtlasAiToolRegistry.get_instance()
    tools = registry.list_tools(include_disabled=include_disabled)

    if category:
        tools = [t for t in tools if t.category.value.upper() == category.upper()]

    descriptors = [_map_tool_descriptor(t) for t in tools]
    return AiToolListResponse(tools=descriptors, total=len(descriptors))


@router.get("/calls", response_model=AiToolCallListResponse)
async def list_tool_calls(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
    limit: int = Query(50, ge=1, le=100),
) -> AiToolCallListResponse:
    """Lists recent tool execution calls for the authenticated user."""
    dispatcher = AiToolDispatcher.get_instance()
    calls = dispatcher.list_tool_calls(user_id=current_user.user_id, limit=limit)

    mapped_calls = [
        AiToolCallResponse(
            id=c.id,
            tool_id=c.tool_id,
            tool_version=c.tool_version,
            status=c.status.value,
            arguments=c.arguments,
            normalized_arguments_hash=c.normalized_arguments_hash,
            result=c.result.data if c.result and c.result.success else None,
            error_code=c.error_code,
            error_message=c.error_message,
            execution_time_ms=c.execution_time_ms,
            approval_class=c.approval_class.value,
            approval_request_id=c.approval_request_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in calls
    ]
    return AiToolCallListResponse(calls=mapped_calls, total=len(mapped_calls))


@router.get("/calls/{call_id}", response_model=AiToolCallResponse)
async def get_tool_call(
    call_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolCallResponse:
    """Retrieves full details and result payload of an executed tool call."""
    dispatcher = AiToolDispatcher.get_instance()
    call = dispatcher.get_tool_call(call_id)
    if not call or call.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool call '{call_id}' not found.",
        )

    return AiToolCallResponse(
        id=call.id,
        tool_id=call.tool_id,
        tool_version=call.tool_version,
        status=call.status.value,
        arguments=call.arguments,
        normalized_arguments_hash=call.normalized_arguments_hash,
        result=call.result.data if call.result and call.result.success else None,
        error_code=call.error_code,
        error_message=call.error_message,
        execution_time_ms=call.execution_time_ms,
        approval_class=call.approval_class.value,
        approval_request_id=call.approval_request_id,
        created_at=call.created_at,
        updated_at=call.updated_at,
    )


@router.post("/execute", response_model=AiToolExecuteResponse)
async def execute_tool(
    request: AiToolExecuteRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolExecuteResponse:
    """Explicitly executes an authorized tool call via the zero-trust dispatcher."""
    dispatcher = AiToolDispatcher.get_instance()
    prefs = _get_user_preferences(current_user.user_id)

    try:
        result = await dispatcher.dispatch(
            tool_id=request.tool_id,
            arguments=request.arguments,
            user_id=current_user.user_id,
            generation_run_id=request.generation_run_id,
            conversation_id=request.conversation_id,
            tenant_id=getattr(current_user, "tenant_id", None),
            disabled_tools=prefs.disabled_tools,
            approval_request_id=request.approval_request_id,
        )

        manifest_dict = None
        if result.source_manifest:
            manifest_dict = {
                "tool_id": result.source_manifest.tool_id,
                "data_source": result.source_manifest.data_source,
                "as_of": result.source_manifest.as_of,
                "attribution": result.source_manifest.attribution,
                "record_count": result.source_manifest.record_count,
            }

        return AiToolExecuteResponse(
            tool_call_id=result.tool_call_id,
            tool_id=result.tool_id,
            success=result.success,
            data=result.data,
            source_manifest=manifest_dict,
            execution_time_ms=result.execution_time_ms,
            as_of=result.as_of,
            error_code=result.error_code,
            error_message=result.error_message,
            truncated=result.truncated,
            content_hash=result.content_hash,
        )

    except AiToolNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except (AiToolNotAuthorizedError, AiToolResourceAccessDeniedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except AiToolApprovalRequiredError as e:
        raise HTTPException(status_code=status.HTTP_428_PRECONDITION_REQUIRED, detail=e.message)
    except (
        AiToolApprovalDeniedError,
        AiToolApprovalExpiredError,
        AiToolApprovalMismatchError,
    ) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except AiToolTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=e.message)
    except AiToolSequenceLimitExceededError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=e.message)
    except AiToolError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/preferences", response_model=AiToolPreferencesResponse)
async def get_preferences(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolPreferencesResponse:
    """Retrieves tool governance preferences for the authenticated user."""
    prefs = _get_user_preferences(current_user.user_id)
    return AiToolPreferencesResponse(
        user_id=prefs.user_id,
        enabled_tools=prefs.enabled_tools,
        disabled_tools=prefs.disabled_tools,
        auto_approve_read_only=prefs.auto_approve_read_only,
        require_approval_for_sensitive=prefs.require_approval_for_sensitive,
        updated_at=prefs.updated_at,
    )


@router.put("/preferences", response_model=AiToolPreferencesResponse)
async def update_preferences(
    body: AiToolPreferencesUpdateRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolPreferencesResponse:
    """Updates tool governance preferences for the authenticated user."""
    prefs = _get_user_preferences(current_user.user_id)

    if body.enabled_tools is not None:
        prefs.enabled_tools = body.enabled_tools
    if body.disabled_tools is not None:
        prefs.disabled_tools = body.disabled_tools
    if body.auto_approve_read_only is not None:
        prefs.auto_approve_read_only = body.auto_approve_read_only
    if body.require_approval_for_sensitive is not None:
        prefs.require_approval_for_sensitive = body.require_approval_for_sensitive
    prefs.updated_at = datetime.now(timezone.utc)

    return AiToolPreferencesResponse(
        user_id=prefs.user_id,
        enabled_tools=prefs.enabled_tools,
        disabled_tools=prefs.disabled_tools,
        auto_approve_read_only=prefs.auto_approve_read_only,
        require_approval_for_sensitive=prefs.require_approval_for_sensitive,
        updated_at=prefs.updated_at,
    )


@router.get("/approvals/{approval_id}", response_model=AiToolApprovalResponse)
async def get_approval(
    approval_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolApprovalResponse:
    """Retrieves details of a pending or decided human approval request."""
    engine = AiToolApprovalEngine.get_instance()
    req = engine.get_approval_request(approval_id)
    if not req or req.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request '{approval_id}' not found.",
        )

    return AiToolApprovalResponse(
        id=req.id,
        tool_call_id=req.tool_call_id,
        user_id=req.user_id,
        tool_id=req.tool_id,
        approval_class=req.approval_class.value,
        normalized_arguments_hash=req.normalized_arguments_hash,
        arguments_summary=req.arguments_summary,
        status=req.status.value,
        expires_at=req.expires_at,
        consumed_at=req.consumed_at,
        decision_reason=req.decision_reason,
        created_at=req.created_at,
    )


@router.post("/approvals/{approval_id}/approve", response_model=AiToolApprovalResponse)
async def approve_tool_call(
    approval_id: str,
    body: AiToolApprovalActionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolApprovalResponse:
    """Approves a pending tool call authorization request."""
    engine = AiToolApprovalEngine.get_instance()
    try:
        req = engine.approve(approval_id, current_user.user_id, body.decision_reason)
        return AiToolApprovalResponse(
            id=req.id,
            tool_call_id=req.tool_call_id,
            user_id=req.user_id,
            tool_id=req.tool_id,
            approval_class=req.approval_class.value,
            normalized_arguments_hash=req.normalized_arguments_hash,
            arguments_summary=req.arguments_summary,
            status=req.status.value,
            expires_at=req.expires_at,
            consumed_at=req.consumed_at,
            decision_reason=req.decision_reason,
            created_at=req.created_at,
        )
    except AiToolError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.post("/approvals/{approval_id}/deny", response_model=AiToolApprovalResponse)
async def deny_tool_call(
    approval_id: str,
    body: AiToolApprovalActionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolApprovalResponse:
    """Denies a pending tool call authorization request."""
    engine = AiToolApprovalEngine.get_instance()
    try:
        req = engine.deny(approval_id, current_user.user_id, body.decision_reason)
        return AiToolApprovalResponse(
            id=req.id,
            tool_call_id=req.tool_call_id,
            user_id=req.user_id,
            tool_id=req.tool_id,
            approval_class=req.approval_class.value,
            normalized_arguments_hash=req.normalized_arguments_hash,
            arguments_summary=req.arguments_summary,
            status=req.status.value,
            expires_at=req.expires_at,
            consumed_at=req.consumed_at,
            decision_reason=req.decision_reason,
            created_at=req.created_at,
        )
    except AiToolError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/{tool_id}", response_model=AiToolDescriptorResponse)
async def get_tool_metadata(
    tool_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> AiToolDescriptorResponse:
    """Retrieves full specification and parameters schema for a registered tool."""
    registry = AtlasAiToolRegistry.get_instance()
    try:
        tool = registry.get_tool(tool_id)
        return _map_tool_descriptor(tool)
    except AiToolNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{tool_id}' not found in registry.",
        )
