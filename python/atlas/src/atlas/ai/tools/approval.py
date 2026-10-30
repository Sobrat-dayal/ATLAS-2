"""Approval Engine for Stage 126: ATLAS AI Tool Gateway.

Manages human-in-the-loop confirmation, argument hash binding, replay prevention,
and time-to-live expiration for sensitive tool calls.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from atlas.ai.tools.domain import (
    AiToolApprovalRequest,
    ApprovalClass,
    ApprovalStatus,
    hash_arguments,
)
from atlas.ai.tools.errors import (
    AiToolApprovalDeniedError,
    AiToolApprovalExpiredError,
    AiToolApprovalMismatchError,
    AiToolApprovalRequiredError,
)

logger = logging.getLogger(__name__)

# Default approval time-to-live: 5 minutes
DEFAULT_APPROVAL_TTL_SECONDS = 300


class AiToolApprovalEngine:
    """Manages the lifecycle, binding, and verification of tool approval requests."""

    _instance: Optional["AiToolApprovalEngine"] = None

    def __init__(self) -> None:
        self._requests: Dict[str, AiToolApprovalRequest] = {}

    @classmethod
    def get_instance(cls) -> "AiToolApprovalEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def create_approval_request(
        self,
        tool_call_id: str,
        user_id: str,
        tool_id: str,
        approval_class: ApprovalClass,
        arguments: Dict[str, Any],
        tenant_id: Optional[str] = None,
        ttl_seconds: int = DEFAULT_APPROVAL_TTL_SECONDS,
    ) -> AiToolApprovalRequest:
        """Issues a new cryptographic approval request binding the exact arguments."""
        req_id = f"aprv_{uuid.uuid4().hex[:16]}"
        arg_hash = hash_arguments(arguments)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

        req = AiToolApprovalRequest(
            id=req_id,
            tool_call_id=tool_call_id,
            user_id=user_id,
            tool_id=tool_id,
            approval_class=approval_class,
            normalized_arguments_hash=arg_hash,
            arguments_summary=arguments,
            expires_at=expires_at,
            tenant_id=tenant_id,
            status=ApprovalStatus.PENDING,
        )
        self._requests[req_id] = req
        logger.info("Created approval request: %s for tool %s", req_id, tool_id)
        return req

    def get_approval_request(self, approval_request_id: str) -> Optional[AiToolApprovalRequest]:
        """Retrieves an approval request by ID."""
        return self._requests.get(approval_request_id)

    def approve(
        self,
        approval_request_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> AiToolApprovalRequest:
        """Approves a pending request."""
        req = self._requests.get(approval_request_id)
        if not req:
            raise AiToolApprovalDeniedError(approval_request_id, "Approval request not found.")
        if req.user_id != user_id:
            raise AiToolApprovalDeniedError(
                approval_request_id, "User not authorized to approve this request."
            )

        # Check expiration
        if datetime.now(timezone.utc) > req.expires_at:
            req.status = ApprovalStatus.EXPIRED
            raise AiToolApprovalExpiredError(approval_request_id)

        req.status = ApprovalStatus.APPROVED
        req.decision_reason = reason or "Approved by user"
        return req

    def deny(
        self,
        approval_request_id: str,
        user_id: str,
        reason: Optional[str] = None,
    ) -> AiToolApprovalRequest:
        """Denies a pending request."""
        req = self._requests.get(approval_request_id)
        if not req:
            raise AiToolApprovalDeniedError(approval_request_id, "Approval request not found.")
        if req.user_id != user_id:
            raise AiToolApprovalDeniedError(
                approval_request_id, "User not authorized to deny this request."
            )

        req.status = ApprovalStatus.DENIED
        req.decision_reason = reason or "Denied by user"
        return req

    def consume_and_verify(
        self,
        approval_request_id: str,
        user_id: str,
        tool_id: str,
        arguments: Dict[str, Any],
    ) -> None:
        """Verifies and consumes an approved token, ensuring argument integrity and replay protection."""
        req = self._requests.get(approval_request_id)
        if not req:
            raise AiToolApprovalDeniedError(approval_request_id, "Approval request not found.")

        # 1. Ownership check
        if req.user_id != user_id:
            raise AiToolApprovalDeniedError(approval_request_id, "Approval ownership mismatch.")

        # 2. Tool match check
        if req.tool_id != tool_id:
            raise AiToolApprovalDeniedError(
                approval_request_id, f"Approval was issued for '{req.tool_id}', not '{tool_id}'."
            )

        # 3. Status check
        if req.status == ApprovalStatus.PENDING:
            raise AiToolApprovalRequiredError(tool_id, approval_request_id)
        if req.status == ApprovalStatus.DENIED:
            raise AiToolApprovalDeniedError(approval_request_id, req.decision_reason)
        if req.status == ApprovalStatus.EXPIRED:
            raise AiToolApprovalExpiredError(approval_request_id)

        # 4. Expiration check
        if datetime.now(timezone.utc) > req.expires_at:
            req.status = ApprovalStatus.EXPIRED
            raise AiToolApprovalExpiredError(approval_request_id)

        # 5. Replay prevention (one-time consumption)
        if req.consumed_at is not None:
            raise AiToolApprovalDeniedError(
                approval_request_id, "Approval token has already been consumed."
            )

        # 6. Argument integrity check (reject argument swaps - Fixture I)
        current_hash = hash_arguments(arguments)
        if current_hash != req.normalized_arguments_hash:
            raise AiToolApprovalMismatchError(approval_request_id)

        # Consume token
        req.consumed_at = datetime.now(timezone.utc)
        logger.info("Successfully consumed approval token: %s", approval_request_id)
