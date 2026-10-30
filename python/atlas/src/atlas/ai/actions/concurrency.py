"""Optimistic concurrency and resource revision verification (Stage 128, Part XVIII, LXXXV)."""

from __future__ import annotations

from typing import Tuple

from atlas.ai.actions.domain import AiFinancialAction
from atlas.ai.actions.errors import AiActionResourceConflictError
from atlas.ai.actions.registry import get_action_registry


async def verify_resource_concurrency(
    action: AiFinancialAction,
    actor_user_id: str,
    tenant_id: str,
) -> Tuple[bool, str]:
    """Verifies that the live target resource revision has not changed since action planning.

    Raises:
        AiActionResourceConflictError: if current revision differs from expected_resource_revision.
    """
    adapter = get_action_registry().get_adapter(action.action_type)
    _, live_revision = await adapter.get_current_state(
        resource_id=action.target_resource_id,
        actor_user_id=actor_user_id,
        tenant_id=tenant_id,
    )

    if action.expected_resource_revision and live_revision != action.expected_resource_revision:
        raise AiActionResourceConflictError(
            resource_id=action.target_resource_id,
            expected_revision=action.expected_resource_revision,
            actual_revision=live_revision,
        )

    return True, live_revision

