"""Action preview engine generating before/after diffs and preview hashes (Stage 128, Part XIV, XV)."""

from __future__ import annotations

from typing import List

from atlas.ai.actions.domain import (
    ActionLifecycleState,
    AiFinancialAction,
    AiFinancialActionPlan,
    AiFinancialActionPreview,
)
from atlas.ai.actions.registry import get_action_registry


class AtlasActionPreviewEngine:
    """Computes accurate previews and cryptographic validation hashes for proposed actions."""

    def __init__(self) -> None:
        self.registry = get_action_registry()

    async def generate_action_preview(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
    ) -> AiFinancialActionPreview:
        adapter = self.registry.get_adapter(action.action_type)

        # 1. Strictly validate parameters
        validated_args = adapter.validate_parameters(action.proposed_arguments)
        action.proposed_arguments = validated_args

        # 2. Retrieve live current state & revision
        current_state, current_rev = await adapter.get_current_state(
            resource_id=action.target_resource_id,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
        )
        action.expected_resource_revision = current_rev

        # 3. Generate preview diffs & hash
        preview = await adapter.generate_preview(
            action_id=action.action_id,
            resource_id=action.target_resource_id,
            current_state=current_state,
            current_revision=current_rev,
            proposed_args=validated_args,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
        )

        action.preview = preview
        action.action_status = ActionLifecycleState.PREVIEW_READY
        return preview

    async def generate_plan_previews(
        self,
        plan: AiFinancialActionPlan,
        actor_user_id: str,
        tenant_id: str,
    ) -> List[AiFinancialActionPreview]:
        previews: List[AiFinancialActionPreview] = []
        for action in plan.actions:
            prev = await self.generate_action_preview(
                action=action,
                actor_user_id=actor_user_id,
                tenant_id=tenant_id,
            )
            previews.append(prev)
        plan.status = ActionLifecycleState.PREVIEW_READY
        return previews
