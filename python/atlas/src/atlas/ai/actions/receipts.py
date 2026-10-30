"""Immutable execution receipts for verified financial operations (Stage 128, Part XXI)."""

from __future__ import annotations

import copy
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from atlas.ai.actions.domain import ActionLifecycleState, AiActionDiff, AiActionExecutionReceipt


class AtlasReceiptManager:
    """Manages immutable receipts generated after real service executions."""

    def __init__(self) -> None:
        self._receipts: Dict[str, AiActionExecutionReceipt] = {}

    def create_receipt(
        self,
        action_id: str,
        plan_id: str,
        actor_user_id: str,
        target_resource_id: str,
        target_revision_before: str,
        target_revision_after: str,
        operation_status: ActionLifecycleState,
        started_at: datetime,
        completed_at: datetime,
        result_reference: Optional[Dict[str, Any]] = None,
        diffs: Optional[List[AiActionDiff]] = None,
        tool_call_id: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        undo_reference: Optional[str] = None,
    ) -> AiActionExecutionReceipt:
        receipt_id = f"rcpt_{uuid.uuid4().hex[:12]}"
        receipt = AiActionExecutionReceipt(
            receipt_id=receipt_id,
            action_id=action_id,
            plan_id=plan_id,
            tool_call_id=tool_call_id,
            actor_user_id=actor_user_id,
            target_resource_id=target_resource_id,
            target_revision_before=target_revision_before,
            target_revision_after=target_revision_after,
            operation_status=operation_status,
            started_at=started_at,
            completed_at=completed_at,
            result_reference=result_reference or {},
            diffs=diffs or [],
            error_code=error_code,
            error_message=error_message,
            undo_reference=undo_reference,
        )
        self._receipts[receipt_id] = copy.deepcopy(receipt)
        return receipt

    def get_receipt(self, receipt_id: str) -> Optional[AiActionExecutionReceipt]:
        r = self._receipts.get(receipt_id)
        return copy.deepcopy(r) if r else None

    def list_receipts_for_user(self, user_id: str) -> List[AiActionExecutionReceipt]:
        return [copy.deepcopy(r) for r in self._receipts.values() if r.actor_user_id == user_id]

    def list_receipts_for_plan(self, plan_id: str) -> List[AiActionExecutionReceipt]:
        return [copy.deepcopy(r) for r in self._receipts.values() if r.plan_id == plan_id]


_RECEIPT_MANAGER = AtlasReceiptManager()


def get_receipt_manager() -> AtlasReceiptManager:
    return _RECEIPT_MANAGER
