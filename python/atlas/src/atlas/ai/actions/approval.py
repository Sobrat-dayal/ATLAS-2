"""Human approval framework and cryptographic binding (Stage 128, Parts XVI, XVII, LXXXIV)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from atlas.ai.actions.domain import ActionLifecycleState, AiFinancialAction
from atlas.ai.actions.errors import (
    AiActionApprovalExpiredError,
    AiActionApprovalMismatchError,
    AiActionReplayDetectedError,
    AiActionValidationFailedError,
)


@dataclass
class ActionApprovalRecord:
    """Immutable record of explicit user consent bound to an action proposal (Part XVI)."""

    approval_id: str
    action_id: str
    actor_user_id: str
    tenant_id: str
    target_resource_id: str
    expected_resource_revision: str
    normalized_arguments_hash: str
    preview_hash: str
    created_at: datetime
    expires_at: datetime
    consumed: bool = False
    consumed_at: Optional[datetime] = None


class AtlasActionApprovalEngine:
    """Manages exact approval binding, expiration verification, and replay prevention."""

    def __init__(self) -> None:
        self._approvals: Dict[str, ActionApprovalRecord] = {}
        self._action_to_approval: Dict[str, str] = {}

    def approve_action(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
        preview_hash: str,
        expected_resource_revision: str,
        duration_minutes: int = 15,
    ) -> ActionApprovalRecord:
        # Verify preview hash matches
        if not action.preview:
            raise AiActionValidationFailedError(
                "Cannot approve an action without a generated preview."
            )

        if action.preview.preview_hash != preview_hash:
            raise AiActionApprovalMismatchError(
                f"Supplied preview_hash '{preview_hash}' does not match computed preview hash '{action.preview.preview_hash}'."
            )

        now = datetime.now(timezone.utc)
        approval_id = f"appr_{uuid.uuid4().hex[:12]}"
        record = ActionApprovalRecord(
            approval_id=approval_id,
            action_id=action.action_id,
            actor_user_id=actor_user_id,
            tenant_id=tenant_id,
            target_resource_id=action.target_resource_id,
            expected_resource_revision=expected_resource_revision,
            normalized_arguments_hash=action.normalized_arguments_hash,
            preview_hash=preview_hash,
            created_at=now,
            expires_at=now + timedelta(minutes=duration_minutes),
        )

        self._approvals[approval_id] = record
        self._action_to_approval[action.action_id] = approval_id
        action.action_status = ActionLifecycleState.APPROVED
        return record

    def deny_action(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        reason: Optional[str] = None,
    ) -> None:
        action.action_status = ActionLifecycleState.DENIED
        # Clean up any pending approval
        if action.action_id in self._action_to_approval:
            appr_id = self._action_to_approval.pop(action.action_id)
            if appr_id in self._approvals:
                del self._approvals[appr_id]

    def verify_and_consume(
        self,
        action: AiFinancialAction,
        actor_user_id: str,
        tenant_id: str,
    ) -> ActionApprovalRecord:
        """Verifies approval authenticity and marks it consumed (preventing replay).

        Throws appropriate typed errors on mismatch, expiration, or replay.
        """
        appr_id = self._action_to_approval.get(action.action_id)
        if not appr_id or appr_id not in self._approvals:
            raise AiActionApprovalMismatchError(
                f"No valid approval found for action '{action.action_id}'."
            )

        record = self._approvals[appr_id]
        now = datetime.now(timezone.utc)

        # 1. Replay check
        if record.consumed:
            raise AiActionReplayDetectedError(record.approval_id)

        # 2. Expiration check
        if now > record.expires_at:
            raise AiActionApprovalExpiredError(record.approval_id)

        # 3. User & Tenant check
        if record.actor_user_id != actor_user_id or record.tenant_id != tenant_id:
            raise AiActionApprovalMismatchError(
                f"Approval was granted to user '{record.actor_user_id}' but execution attempted by '{actor_user_id}'."
            )

        # 4. Target Resource check (Fixture E: Approval Substitution Attack)
        if record.target_resource_id != action.target_resource_id:
            raise AiActionApprovalMismatchError(
                f"Approval attack detected! Approved resource was '{record.target_resource_id}', "
                f"but execution attempted against '{action.target_resource_id}'."
            )

        # 5. Arguments Hash check
        if record.normalized_arguments_hash != action.normalized_arguments_hash:
            raise AiActionApprovalMismatchError(
                "Proposed arguments have been modified since user approval was granted."
            )

        # 6. Mark consumed (Replay prevention)
        record.consumed = True
        record.consumed_at = now
        return record
