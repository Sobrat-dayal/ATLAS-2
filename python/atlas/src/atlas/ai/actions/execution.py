"""Execution coordinator and workflow orchestrator (Stage 128, Parts LII, LIII)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from atlas.ai.actions.approval import AtlasActionApprovalEngine
from atlas.ai.actions.concurrency import verify_resource_concurrency
from atlas.ai.actions.domain import (
    ActionLifecycleState,
    AiActionExecutionReceipt,
    AiFinancialActionPlan,
    ApprovalPolicy,
)
from atlas.ai.actions.errors import (
    AiActionApprovalRequiredError,
    AiActionError,
)
from atlas.ai.actions.idempotency import get_idempotency_manager
from atlas.ai.actions.receipts import get_receipt_manager
from atlas.ai.actions.registry import get_action_registry


class AtlasActionExecutionCoordinator:
    """Coordinates dependency-ordered execution, re-verifies authorization, and creates receipts."""

    def __init__(self, approval_engine: AtlasActionApprovalEngine) -> None:
        self.registry = get_action_registry()
        self.approval_engine = approval_engine
        self.receipt_manager = get_receipt_manager()
        self.idempotency_manager = get_idempotency_manager()

    async def execute_plan(
        self,
        plan: AiFinancialActionPlan,
        actor_user_id: str,
        tenant_id: str,
        idempotency_key: str,
    ) -> Tuple[AiFinancialActionPlan, List[AiActionExecutionReceipt], bool]:
        # 1. Idempotency Check (Fixture G)
        cached = self.idempotency_manager.get_cached_response(idempotency_key)
        if cached:
            # Reconstruct receipts from cache
            receipts = [
                self.receipt_manager.get_receipt(rcpt_id)
                for rcpt_id in cached.get("receipt_ids", [])
            ]
            valid_receipts = [r for r in receipts if r is not None]
            plan.status = ActionLifecycleState(cached.get("status", "COMPLETED"))
            return plan, valid_receipts, cached.get("is_partially_completed", False)

        plan.status = ActionLifecycleState.EXECUTING
        completed_receipts: List[AiActionExecutionReceipt] = []
        is_partial = False
        failed_error: Optional[str] = None

        # Execute actions in order (respecting dependency graph)
        for action in plan.actions:
            # Check prerequisites
            prereqs = plan.dependency_graph.get(action.action_id, [])
            for prereq_id in prereqs:
                prereq_action = next((a for a in plan.actions if a.action_id == prereq_id), None)
                if (
                    not prereq_action
                    or prereq_action.action_status != ActionLifecycleState.COMPLETED
                ):
                    # Prerequisite not met!
                    action.action_status = ActionLifecycleState.FAILED
                    is_partial = True
                    break

            if action.action_status == ActionLifecycleState.FAILED:
                continue

            started_at = datetime.now(timezone.utc)
            rev_before = action.expected_resource_revision

            try:
                # 2. Check approval requirement
                if action.approval_policy != ApprovalPolicy.AUTO_READ_ONLY:
                    if action.action_status != ActionLifecycleState.APPROVED:
                        raise AiActionApprovalRequiredError(
                            action.action_id, action.approval_policy.value
                        )
                    # Verify and consume approval (checks replay, expiration, parameter tamper, resource tamper)
                    self.approval_engine.verify_and_consume(action, actor_user_id, tenant_id)

                # 3. Optimistic Concurrency Check (Fixture F)
                await verify_resource_concurrency(action, actor_user_id, tenant_id)

                action.action_status = ActionLifecycleState.EXECUTING
                adapter = self.registry.get_adapter(action.action_type)

                # 4. Dispatch to real service
                result_data, rev_after, applied_diffs = await adapter.execute(
                    action=action,
                    actor_user_id=actor_user_id,
                    tenant_id=tenant_id,
                )

                completed_at = datetime.now(timezone.utc)
                action.action_status = ActionLifecycleState.COMPLETED

                # 5. Create immutable execution receipt
                receipt = self.receipt_manager.create_receipt(
                    action_id=action.action_id,
                    plan_id=plan.plan_id,
                    actor_user_id=actor_user_id,
                    target_resource_id=action.target_resource_id,
                    target_revision_before=rev_before,
                    target_revision_after=rev_after,
                    operation_status=ActionLifecycleState.COMPLETED,
                    started_at=started_at,
                    completed_at=completed_at,
                    result_reference=result_data,
                    diffs=applied_diffs,
                )
                completed_receipts.append(receipt)

            except Exception as exc:
                completed_at = datetime.now(timezone.utc)
                action.action_status = ActionLifecycleState.FAILED
                is_partial = True
                failed_error = str(exc)

                err_code = exc.code if isinstance(exc, AiActionError) else "EXECUTION_ERROR"
                err_msg = exc.message if isinstance(exc, AiActionError) else str(exc)

                failed_receipt = self.receipt_manager.create_receipt(
                    action_id=action.action_id,
                    plan_id=plan.plan_id,
                    actor_user_id=actor_user_id,
                    target_resource_id=action.target_resource_id,
                    target_revision_before=rev_before,
                    target_revision_after=rev_before,
                    operation_status=ActionLifecycleState.FAILED,
                    started_at=started_at,
                    completed_at=completed_at,
                    error_code=err_code,
                    error_message=err_msg,
                )
                completed_receipts.append(failed_receipt)

                # If single action failed, re-raise so caller gets typed exception
                if len(plan.actions) == 1:
                    raise

                # For multi-step plan, stop executing further dependent steps (Fixture J)
                break

        # Finalize plan state
        if all(a.action_status == ActionLifecycleState.COMPLETED for a in plan.actions):
            plan.status = ActionLifecycleState.COMPLETED
        elif any(a.action_status == ActionLifecycleState.COMPLETED for a in plan.actions):
            plan.status = ActionLifecycleState.PARTIALLY_COMPLETED
            is_partial = True
        else:
            plan.status = ActionLifecycleState.FAILED

        # Record idempotency cache
        self.idempotency_manager.record_response(
            idempotency_key,
            {
                "plan_id": plan.plan_id,
                "status": plan.status.value,
                "is_partially_completed": is_partial,
                "receipt_ids": [r.receipt_id for r in completed_receipts],
                "error": failed_error,
            },
        )

        return plan, completed_receipts, is_partial
