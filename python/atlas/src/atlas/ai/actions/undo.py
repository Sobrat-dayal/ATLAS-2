"""Undo and compensation service for reversible financial actions (Stage 128, Part XXII)."""

from __future__ import annotations

from atlas.ai.actions.domain import ActionLifecycleState, AiFinancialAction, ReversibilityPolicy
from atlas.ai.actions.errors import (
    AiActionTargetNotFoundError,
    AiActionUndoUnavailableError,
)
from atlas.ai.actions.receipts import get_receipt_manager
from atlas.ai.actions.registry import get_action_registry


class AtlasActionUndoService:
    """Safely reverts reversible actions using prior resource revisions."""

    def __init__(self) -> None:
        self.registry = get_action_registry()
        self.receipt_manager = get_receipt_manager()

    async def undo_action(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
        receipt_id: str,
    ) -> str:
        # Check reversibility policy
        if action.reversibility_policy == ReversibilityPolicy.NON_REVERSIBLE:
            raise AiActionUndoUnavailableError(
                action.action_id,
                f"Action '{action.action_type.value}' is non-reversible by policy.",
            )

        receipt = self.receipt_manager.get_receipt(receipt_id)
        if not receipt:
            raise AiActionTargetNotFoundError("execution_receipt", receipt_id)

        adapter = self.registry.get_adapter(action.action_type)
        restored_revision = await adapter.undo(
            action=action,
            receipt=receipt,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
        )

        action.action_status = ActionLifecycleState.COMPLETED
        return restored_revision

