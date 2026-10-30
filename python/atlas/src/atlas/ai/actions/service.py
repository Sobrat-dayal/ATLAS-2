"""Service coordinator for ATLAS AI Financial Actions (Stage 128, Part LIII)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from atlas.ai.actions.approval import AtlasActionApprovalEngine
from atlas.ai.actions.domain import (
    AiActionExecutionReceipt,
    AiFinancialAction,
    AiFinancialActionPlan,
)
from atlas.ai.actions.errors import (
    AiActionAccessDeniedError,
    AiActionTargetNotFoundError,
)
from atlas.ai.actions.execution import AtlasActionExecutionCoordinator
from atlas.ai.actions.planning import AtlasActionPlanner
from atlas.ai.actions.preview import AtlasActionPreviewEngine
from atlas.ai.actions.receipts import get_receipt_manager
from atlas.ai.actions.registry import get_action_registry
from atlas.ai.actions.undo import AtlasActionUndoService


class AtlasAiActionService:
    """Master service providing high-level APIs for AI financial action lifecycle."""

    def __init__(self) -> None:
        self.registry = get_action_registry()
        self.planner = AtlasActionPlanner()
        self.preview_engine = AtlasActionPreviewEngine()
        self.approval_engine = AtlasActionApprovalEngine()
        self.execution_coordinator = AtlasActionExecutionCoordinator(self.approval_engine)
        self.undo_service = AtlasActionUndoService()
        self.receipt_manager = get_receipt_manager()

        self._plans: Dict[str, AiFinancialActionPlan] = {}
        self._actions: Dict[str, AiFinancialAction] = {}

    async def create_plan(
        self,
        intent: str,
        actor_user_id: str,
        tenant_id: str = "default_tenant",
        conversation_id: Optional[str] = None,
        context_hints: Optional[Dict[str, Any]] = None,
    ) -> AiFinancialActionPlan:
        # 1. Parse intent into structured plan
        plan = self.planner.parse_and_plan(
            intent=intent,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            context_hints=context_hints,
        )

        # 2. Compute previews for all planned actions
        await self.preview_engine.generate_plan_previews(
            plan=plan,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
        )

        # 3. Store plan and actions
        self._plans[plan.plan_id] = plan
        for action in plan.actions:
            self._actions[action.action_id] = action

        return plan

    def get_plan(self, plan_id: str, actor_user_id: str, tenant_id: str) -> AiFinancialActionPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise AiActionTargetNotFoundError("action_plan", plan_id)

        # Tenant & user isolation check (Part LVI, LXXIV)
        if plan.owner_user_id != actor_user_id or plan.tenant_id != tenant_id:
            raise AiActionAccessDeniedError("action_plan", plan_id)

        return plan

    def approve_action(
        self,
        action_id: str,
        preview_hash: str,
        expected_resource_revision: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Dict[str, Any]:
        action = self._actions.get(action_id)
        if not action:
            raise AiActionTargetNotFoundError("financial_action", action_id)

        if action.actor_user_id != actor_user_id or action.tenant_scope != tenant_id:
            raise AiActionAccessDeniedError("financial_action", action_id)

        record = self.approval_engine.approve_action(
            action=action,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            preview_hash=preview_hash,
            expected_resource_revision=expected_resource_revision,
        )

        return {
            "approval_id": record.approval_id,
            "action_id": record.action_id,
            "status": "APPROVED",
            "approved_at": record.created_at.isoformat(),
            "expires_at": record.expires_at.isoformat(),
        }

    def deny_action(
        self,
        action_id: str,
        actor_user_id: str,
        tenant_id: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        action = self._actions.get(action_id)
        if not action:
            raise AiActionTargetNotFoundError("financial_action", action_id)

        if action.actor_user_id != actor_user_id or action.tenant_scope != tenant_id:
            raise AiActionAccessDeniedError("financial_action", action_id)

        self.approval_engine.deny_action(action, actor_user_id, reason)
        return {
            "action_id": action.action_id,
            "status": "DENIED",
            "reason": reason,
        }

    async def execute_plan(
        self,
        plan_id: str,
        idempotency_key: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> Tuple[AiFinancialActionPlan, List[AiActionExecutionReceipt], bool]:
        plan = self.get_plan(plan_id, actor_user_id, tenant_id)
        return await self.execution_coordinator.execute_plan(
            plan=plan,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            idempotency_key=idempotency_key,
        )

    async def undo_action(
        self,
        action_id: str,
        receipt_id: str,
        actor_user_id: str,
        tenant_id: str,
    ) -> str:
        action = self._actions.get(action_id)
        if not action:
            raise AiActionTargetNotFoundError("financial_action", action_id)

        if action.actor_user_id != actor_user_id or action.tenant_scope != tenant_id:
            raise AiActionAccessDeniedError("financial_action", action_id)

        return await self.undo_service.undo_action(
            action=action,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            receipt_id=receipt_id,
        )

    def get_history(self, actor_user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        receipts = self.receipt_manager.list_receipts_for_user(actor_user_id)
        history: List[Dict[str, Any]] = []
        for r in receipts:
            act = self._actions.get(r.action_id)
            history.append(
                {
                    "action_id": r.action_id,
                    "plan_id": r.plan_id,
                    "action_type": act.action_type.value if act else "unknown",
                    "target_module": act.target_module if act else "unknown",
                    "target_resource_id": r.target_resource_id,
                    "status": r.operation_status.value,
                    "created_at": r.started_at.isoformat(),
                    "completed_at": r.completed_at.isoformat(),
                    "receipt_id": r.receipt_id,
                    "is_reversible": act.reversibility_policy.value != "NON_REVERSIBLE"
                    if act
                    else False,
                }
            )
        return history


_ACTION_SERVICE = AtlasAiActionService()


def get_action_service() -> AtlasAiActionService:
    return _ACTION_SERVICE
