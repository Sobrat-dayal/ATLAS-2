"""Domain service for ATLAS Approval Inbox and Decision Architecture (Stage 54)."""

import base64
import datetime
import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .constants import (
    ALLOWED_ACTION_KINDS,
    MAX_APPROVAL_LIFETIME,
    TRUSTED_PRODUCERS,
)
from .enums import ApprovalDecisionType, ApprovalStatus, ApprovalStatusFilter
from .errors import (
    ApprovalAlreadyDecidedError,
    ApprovalConflictError,
    ApprovalExpiredError,
    ApprovalIdempotencyConflictError,
    ApprovalNotFoundError,
    InvalidActionKindError,
    InvalidApprovalPayloadError,
    UntrustedProducerError,
)
from .models import (
    ApprovalCountsResponse,
    ApprovalDecision,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalDetailResponse,
    ApprovalItemResponse,
    ApprovalListResponse,
    ApprovalRequest,
    CreateApprovalInternalRequest,
)
from .repository import ApprovalRepository

logger = logging.getLogger(__name__)


def encode_approval_cursor(requested_at: datetime.datetime, approval_id: uuid.UUID) -> str:
    """Encode keyset cursor as Base64 string."""
    raw = f"{requested_at.isoformat()}|{str(approval_id)}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")


def decode_approval_cursor(cursor_str: str) -> tuple[datetime.datetime, uuid.UUID]:
    """Decode keyset cursor string into (requested_at, approval_id)."""
    try:
        raw = base64.urlsafe_b64decode(cursor_str.encode("utf-8")).decode("utf-8")
        parts = raw.split("|")
        if len(parts) != 2:
            raise ValueError("Malformed cursor structure")
        requested_at = datetime.datetime.fromisoformat(parts[0])
        approval_id = uuid.UUID(parts[1])
        return requested_at, approval_id
    except Exception as exc:
        raise InvalidApprovalPayloadError(f"Invalid pagination cursor: {exc}") from exc


class ApprovalService:
    """Encapsulates business rules, producer trust, and human decision recording."""

    def __init__(
        self,
        session: AsyncSession,
        repository: ApprovalRepository,
    ) -> None:
        self.session = session
        self.repository = repository

    async def create_request(
        self,
        request: CreateApprovalInternalRequest,
    ) -> ApprovalRequest:
        """
        Create a new approval request.
        Internal service-only method: strictly validates trusted producer and action allowlists.
        """
        # 1. Validate trusted producer
        if request.producer_key not in TRUSTED_PRODUCERS:
            raise UntrustedProducerError(request.producer_key)

        # 2. Validate action kind
        if request.action_kind not in ALLOWED_ACTION_KINDS:
            raise InvalidActionKindError(request.action_kind)

        now = datetime.datetime.now(datetime.timezone.utc)

        # 3. Validate expiration window
        if request.expires_at <= now:
            raise InvalidApprovalPayloadError("expires_at must be in the future")
        if request.expires_at > (now + MAX_APPROVAL_LIFETIME):
            raise InvalidApprovalPayloadError(
                f"expires_at cannot exceed maximum lifetime of {MAX_APPROVAL_LIFETIME.days} days"
            )

        # 4. Check producer idempotency
        existing = await self.repository.get_by_producer_idempotency(
            producer_key=request.producer_key,
            idempotency_key=request.idempotency_key,
            approver_user_id=request.approver_user_id,
        )
        if existing:
            if (
                existing.proposal_reference != request.proposal_reference
                or existing.proposal_digest != request.proposal_digest
                or existing.action_kind != request.action_kind
            ):
                raise ApprovalIdempotencyConflictError(
                    "Conflicting approval request payload for provided idempotency key"
                )
            return existing

        app_req = ApprovalRequest(
            approval_id=uuid.uuid4(),
            approver_user_id=request.approver_user_id,
            producer_key=request.producer_key,
            action_kind=request.action_kind,
            proposal_reference=request.proposal_reference,
            proposal_digest=request.proposal_digest,
            title=request.title,
            summary=request.summary,
            status=ApprovalStatus.PENDING.value,
            requested_at=now,
            expires_at=request.expires_at,
            decided_at=None,
            decided_by_user_id=None,
            version=1,
            idempotency_key=request.idempotency_key,
        )

        await self.repository.create_request(app_req)
        await self.session.commit()
        return app_req

    async def record_decision(
        self,
        approver_user_id: uuid.UUID,
        approval_id: uuid.UUID,
        request: ApprovalDecisionRequest,
    ) -> ApprovalDecisionResponse:
        """
        Record an immutable human decision (APPROVE or REJECT) on a pending request.
        Non-negotiable rule: Recorded decision does NOT execute the action.
        """
        # 1. Fetch request with row lock
        app_req = await self.repository.get_by_id(
            approval_id=approval_id,
            approver_user_id=approver_user_id,
            for_update=True,
        )
        if not app_req:
            raise ApprovalNotFoundError(str(approval_id))

        # 2. Check decision idempotency
        existing_dec = await self.repository.get_decision_by_idempotency(
            approver_user_id=approver_user_id,
            decision_idempotency_key=request.decision_idempotency_key,
        )
        if existing_dec:
            if (
                existing_dec.approval_id != approval_id
                or existing_dec.decision != request.decision.value
            ):
                raise ApprovalIdempotencyConflictError(
                    "Conflicting decision parameters for decision_idempotency_key"
                )
            return ApprovalDecisionResponse(
                decision_id=existing_dec.decision_id,
                approval_id=existing_dec.approval_id,
                approver_user_id=existing_dec.approver_user_id,
                decision=ApprovalDecisionType(existing_dec.decision),
                decided_at=existing_dec.decided_at,
                status=ApprovalStatus(app_req.status),
                version=app_req.version,
            )

        now = datetime.datetime.now(datetime.timezone.utc)

        # 3. Check if already decided or cancelled
        if app_req.status != ApprovalStatus.PENDING.value:
            raise ApprovalAlreadyDecidedError(app_req.status)

        # 4. Check expiration using trusted server time
        if now >= app_req.expires_at:
            raise ApprovalExpiredError(
                f"Approval request expired at {app_req.expires_at.isoformat()} "
                "and can no longer be decided"
            )

        # 5. Check optimistic version if supplied
        if request.expected_version is not None and app_req.version != request.expected_version:
            raise ApprovalConflictError(
                f"Approval request version mismatch. Expected {request.expected_version}, "
                f"found {app_req.version}."
            )

        # 6. Atomic mutation: update status and insert decision audit record
        new_status = (
            ApprovalStatus.APPROVED.value
            if request.decision == ApprovalDecisionType.APPROVE
            else ApprovalStatus.REJECTED.value
        )
        app_req.status = new_status
        app_req.decided_at = now
        app_req.decided_by_user_id = approver_user_id
        app_req.version += 1

        decision_record = ApprovalDecision(
            decision_id=uuid.uuid4(),
            approval_id=app_req.approval_id,
            approver_user_id=approver_user_id,
            decision=request.decision.value,
            decided_at=now,
            decision_idempotency_key=request.decision_idempotency_key,
            reason=request.reason,
        )
        await self.repository.create_decision(decision_record)
        await self.session.commit()

        # NOTE: Stage 54 strictly stops at recording the human decision.
        # No shell execution, no trading execution, no workflow execution, no agent execution.
        return ApprovalDecisionResponse(
            decision_id=decision_record.decision_id,
            approval_id=app_req.approval_id,
            approver_user_id=approver_user_id,
            decision=request.decision,
            decided_at=decision_record.decided_at,
            status=ApprovalStatus(new_status),
            version=app_req.version,
        )

    async def cancel_request(
        self,
        producer_key: str,
        approval_id: uuid.UUID,
    ) -> ApprovalRequest:
        """
        Internal cancellation of a pending request by its trusted producer.
        """
        if producer_key not in TRUSTED_PRODUCERS:
            raise UntrustedProducerError(producer_key)

        stmt_res = await self.session.execute(
            ApprovalRequest.__table__.select().where(ApprovalRequest.approval_id == approval_id)
        )
        raw_row = stmt_res.first()
        if not raw_row:
            raise ApprovalNotFoundError(str(approval_id))

        app_req = await self.repository.get_by_id(
            approval_id=approval_id,
            approver_user_id=raw_row.approver_user_id,
            for_update=True,
        )
        if not app_req:
            raise ApprovalNotFoundError(str(approval_id))

        if app_req.status != ApprovalStatus.PENDING.value:
            return app_req

        now = datetime.datetime.now(datetime.timezone.utc)
        app_req.status = ApprovalStatus.CANCELLED.value
        app_req.decided_at = now
        app_req.version += 1
        await self.session.commit()
        return app_req

    async def get_approval_detail(
        self,
        approver_user_id: uuid.UUID,
        approval_id: uuid.UUID,
    ) -> ApprovalDetailResponse:
        """Fetch complete detail view for an approval request."""
        app_req = await self.repository.get_by_id(
            approval_id=approval_id,
            approver_user_id=approver_user_id,
        )
        if not app_req:
            raise ApprovalNotFoundError(str(approval_id))

        now = datetime.datetime.now(datetime.timezone.utc)
        is_expired = app_req.status == ApprovalStatus.PENDING.value and now >= app_req.expires_at

        effective_status = app_req.status
        if is_expired:
            effective_status = "EXPIRED"

        decision_reason = app_req.decision.reason if app_req.decision else None

        return ApprovalDetailResponse(
            approval_id=app_req.approval_id,
            approver_user_id=app_req.approver_user_id,
            producer_key=app_req.producer_key,
            action_kind=app_req.action_kind,
            proposal_reference=app_req.proposal_reference,
            proposal_digest=app_req.proposal_digest,
            title=app_req.title,
            summary=app_req.summary,
            status=ApprovalStatus(app_req.status),
            effective_status=effective_status,
            requested_at=app_req.requested_at,
            expires_at=app_req.expires_at,
            decided_at=app_req.decided_at,
            decided_by_user_id=app_req.decided_by_user_id,
            version=app_req.version,
            is_expired=is_expired,
            reason=decision_reason,
        )

    async def list_approvals(
        self,
        approver_user_id: uuid.UUID,
        status_filter: ApprovalStatusFilter = ApprovalStatusFilter.PENDING,
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> ApprovalListResponse:
        """
        List approval requests for user using keyset pagination.
        """
        bounded_limit = max(1, min(limit, 50))
        now = datetime.datetime.now(datetime.timezone.utc)

        cursor_requested_at = None
        cursor_id = None
        if cursor:
            cursor_requested_at, cursor_id = decode_approval_cursor(cursor)

        requests = await self.repository.list_approvals(
            approver_user_id=approver_user_id,
            status_filter=status_filter,
            limit=bounded_limit + 1,
            now=now,
            cursor_requested_at=cursor_requested_at,
            cursor_id=cursor_id,
        )

        has_more = len(requests) > bounded_limit
        page_requests = list(requests[:bounded_limit])

        items: list[ApprovalItemResponse] = []
        for r in page_requests:
            is_expired = r.status == ApprovalStatus.PENDING.value and now >= r.expires_at
            effective_status = "EXPIRED" if is_expired else r.status
            items.append(
                ApprovalItemResponse(
                    approval_id=r.approval_id,
                    approver_user_id=r.approver_user_id,
                    producer_key=r.producer_key,
                    action_kind=r.action_kind,
                    proposal_reference=r.proposal_reference,
                    title=r.title,
                    summary=r.summary,
                    status=ApprovalStatus(r.status),
                    effective_status=effective_status,
                    requested_at=r.requested_at,
                    expires_at=r.expires_at,
                    decided_at=r.decided_at,
                    decided_by_user_id=r.decided_by_user_id,
                    version=r.version,
                    is_expired=is_expired,
                )
            )

        next_cursor = None
        if has_more and page_requests:
            last = page_requests[-1]
            next_cursor = encode_approval_cursor(last.requested_at, last.approval_id)

        pending_count = await self.repository.get_pending_count(approver_user_id, now)

        return ApprovalListResponse(
            schema_version="1.0",
            items=items,
            pending_count=pending_count,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_counts(self, approver_user_id: uuid.UUID) -> ApprovalCountsResponse:
        """Return real pending count."""
        now = datetime.datetime.now(datetime.timezone.utc)
        count = await self.repository.get_pending_count(approver_user_id, now)
        return ApprovalCountsResponse(pending_count=count)
