"""FastAPI Router for ATLAS Stage 128: AI Financial Action Engine.
Mounted under /api/v1/ai/actions.
"""

from __future__ import annotations

import logging
from typing import Annotated

from atlas.ai.actions.errors import (
    AiActionError,
)
from atlas.ai.actions.registry import get_action_registry
from atlas.ai.actions.schemas import (
    ActionApprovalRequest,
    ActionApprovalResponse,
    ActionCapabilitiesResponse,
    ActionDenialRequest,
    ActionDenialResponse,
    ActionHistoryResponse,
    ActionPlanResponse,
    CreateActionPlanRequest,
    ExecuteActionPlanRequest,
    ExecuteActionPlanResponse,
    ExecutionReceiptDTO,
    UndoActionRequest,
    UndoActionResponse,
)
from atlas.ai.actions.service import get_action_service
from atlas.auth import AuthPrincipal
from fastapi import APIRouter, Depends, HTTPException, status

from atlas_api.auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/actions", tags=["AI Financial Actions"])


def _extract_user_context(current_user: AuthPrincipal) -> tuple[str, str]:
    user_id = str(getattr(current_user, "sub", getattr(current_user, "id", "test_user")))
    tenant_id = str(getattr(current_user, "tenant_id", "default_tenant"))
    return user_id, tenant_id


def _map_action_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, AiActionError):
        return HTTPException(
            status_code=exc.status_code,
            detail={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )
    logger.exception("Unexpected error in AI Action Engine: %s", exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={"code": "AI_ACTION_INTERNAL_ERROR", "message": str(exc)},
    )


@router.get("/capabilities", response_model=ActionCapabilitiesResponse)
async def get_capabilities(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionCapabilitiesResponse:
    """Discover all supported AI financial action capabilities across Charts, Screeners, Portfolios, and Risk."""
    registry = get_action_registry()
    caps = registry.get_capabilities()
    return ActionCapabilitiesResponse(capabilities=caps, total_count=len(caps))


@router.post("/plan", response_model=ActionPlanResponse)
async def create_action_plan(
    request: CreateActionPlanRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionPlanResponse:
    """Interpret natural-language intent, resolve context, and construct a previewed action plan."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    try:
        plan = await service.create_plan(
            intent=request.intent,
            actor_user_id=user_id,
            tenant_id=tenant_id,
            conversation_id=request.conversation_id,
            context_hints=request.context_hints,
        )
        return ActionPlanResponse(**plan.to_dict())
    except Exception as exc:
        raise _map_action_exception(exc)


@router.get("/plans/{plan_id}", response_model=ActionPlanResponse)
async def get_action_plan(
    plan_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionPlanResponse:
    """Retrieve details and previews for an action plan."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    try:
        plan = service.get_plan(plan_id, user_id, tenant_id)
        return ActionPlanResponse(**plan.to_dict())
    except Exception as exc:
        raise _map_action_exception(exc)


@router.post("/plans/{plan_id}/approve", response_model=ActionApprovalResponse)
async def approve_action(
    plan_id: str,
    request: ActionApprovalRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionApprovalResponse:
    """Grant explicit user confirmation for a planned action bound to its preview hash."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    try:
        # Verify plan ownership first
        service.get_plan(plan_id, user_id, tenant_id)
        res = service.approve_action(
            action_id=request.action_id,
            preview_hash=request.preview_hash,
            expected_resource_revision=request.expected_resource_revision,
            actor_user_id=user_id,
            tenant_id=tenant_id,
        )
        return ActionApprovalResponse(**res)
    except Exception as exc:
        raise _map_action_exception(exc)


@router.post("/plans/{plan_id}/deny", response_model=ActionDenialResponse)
async def deny_action(
    plan_id: str,
    request: ActionDenialRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionDenialResponse:
    """Deny a planned financial action."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    try:
        service.get_plan(plan_id, user_id, tenant_id)
        res = service.deny_action(
            action_id=request.action_id,
            actor_user_id=user_id,
            tenant_id=tenant_id,
            reason=request.reason,
        )
        return ActionDenialResponse(**res)
    except Exception as exc:
        raise _map_action_exception(exc)


@router.post("/plans/{plan_id}/execute", response_model=ExecuteActionPlanResponse)
async def execute_action_plan(
    plan_id: str,
    request: ExecuteActionPlanRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ExecuteActionPlanResponse:
    """Execute an approved action plan across real financial modules."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    try:
        plan, receipts, is_partial = await service.execute_plan(
            plan_id=plan_id,
            idempotency_key=request.idempotency_key,
            actor_user_id=user_id,
            tenant_id=tenant_id,
        )
        return ExecuteActionPlanResponse(
            plan_id=plan.plan_id,
            status=plan.status.value,
            executed_actions=len(receipts),
            receipts=[ExecutionReceiptDTO(**r.to_dict()) for r in receipts],
            is_partially_completed=is_partial,
        )
    except Exception as exc:
        raise _map_action_exception(exc)


@router.get("/receipts/{receipt_id}", response_model=ExecutionReceiptDTO)
async def get_execution_receipt(
    receipt_id: str,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ExecutionReceiptDTO:
    """Retrieve an immutable execution receipt."""
    user_id, _ = _extract_user_context(current_user)
    service = get_action_service()
    receipt = service.receipt_manager.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "AI_ACTION_RECEIPT_NOT_FOUND",
                "message": f"Receipt '{receipt_id}' not found.",
            },
        )
    if receipt.actor_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AI_ACTION_ACCESS_DENIED", "message": "Access denied to receipt."},
        )
    return ExecutionReceiptDTO(**receipt.to_dict())


@router.post("/actions/{action_id}/undo", response_model=UndoActionResponse)
async def undo_action(
    action_id: str,
    request: UndoActionRequest,
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> UndoActionResponse:
    """Revert a reversible action using its execution receipt."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    if not request.receipt_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "AI_ACTION_RECEIPT_REQUIRED",
                "message": "Missing receipt_id for undo.",
            },
        )
    try:
        restored_rev = await service.undo_action(
            action_id=action_id,
            receipt_id=request.receipt_id,
            actor_user_id=user_id,
            tenant_id=tenant_id,
        )
        return UndoActionResponse(
            action_id=action_id,
            status="RESTORED",
            restored_revision=restored_rev,
            receipt_id=request.receipt_id,
            undone_at="now",
        )
    except Exception as exc:
        raise _map_action_exception(exc)


@router.get("/history", response_model=ActionHistoryResponse)
async def get_action_history(
    current_user: Annotated[AuthPrincipal, Depends(get_current_user)],
) -> ActionHistoryResponse:
    """List authenticated user's authorized action execution history."""
    user_id, tenant_id = _extract_user_context(current_user)
    service = get_action_service()
    hist = service.get_history(user_id, tenant_id)
    return ActionHistoryResponse(history=hist, total_count=len(hist))
