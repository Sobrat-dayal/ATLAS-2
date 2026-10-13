"""Repository for approval requests and human decisions (Stage 54)."""

import datetime
import uuid
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .enums import ApprovalStatus, ApprovalStatusFilter
from .models import ApprovalDecision, ApprovalRequest


class ApprovalRepository:
    """Encapsulates database operations for approval requests and decisions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        approval_id: uuid.UUID,
        approver_user_id: uuid.UUID,
        for_update: bool = False,
    ) -> Optional[ApprovalRequest]:
        """Fetch request by ID with approver ownership enforcement."""
        stmt = (
            select(ApprovalRequest)
            .options(selectinload(ApprovalRequest.decision))
            .where(
                ApprovalRequest.approval_id == approval_id,
                ApprovalRequest.approver_user_id == approver_user_id,
            )
        )
        if for_update:
            stmt = stmt.with_for_update()
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_producer_idempotency(
        self,
        producer_key: str,
        idempotency_key: str,
        approver_user_id: uuid.UUID,
    ) -> Optional[ApprovalRequest]:
        """Fetch existing request by producer idempotency key."""
        stmt = select(ApprovalRequest).where(
            ApprovalRequest.producer_key == producer_key,
            ApprovalRequest.idempotency_key == idempotency_key,
            ApprovalRequest.approver_user_id == approver_user_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_decision_by_idempotency(
        self,
        approver_user_id: uuid.UUID,
        decision_idempotency_key: uuid.UUID,
    ) -> Optional[ApprovalDecision]:
        """Fetch existing decision by client idempotency key."""
        stmt = select(ApprovalDecision).where(
            ApprovalDecision.approver_user_id == approver_user_id,
            ApprovalDecision.decision_idempotency_key == decision_idempotency_key,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_decision_by_approval_id(
        self,
        approval_id: uuid.UUID,
    ) -> Optional[ApprovalDecision]:
        """Fetch decision for a given approval request."""
        stmt = select(ApprovalDecision).where(ApprovalDecision.approval_id == approval_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_request(self, request: ApprovalRequest) -> ApprovalRequest:
        """Insert a new approval request."""
        self.session.add(request)
        await self.session.flush()
        return request

    async def create_decision(self, decision: ApprovalDecision) -> ApprovalDecision:
        """Insert an immutable approval decision audit record."""
        self.session.add(decision)
        await self.session.flush()
        return decision

    async def list_approvals(
        self,
        approver_user_id: uuid.UUID,
        status_filter: ApprovalStatusFilter,
        limit: int,
        now: datetime.datetime,
        cursor_requested_at: Optional[datetime.datetime] = None,
        cursor_id: Optional[uuid.UUID] = None,
    ) -> list[ApprovalRequest]:
        """
        List approval requests using keyset pagination.
        Handles derived EXPIRED filter: status == PENDING and expires_at <= now.
        For PENDING filter: status == PENDING and expires_at > now.
        """
        stmt = (
            select(ApprovalRequest)
            .options(selectinload(ApprovalRequest.decision))
            .where(ApprovalRequest.approver_user_id == approver_user_id)
        )

        if status_filter == ApprovalStatusFilter.PENDING:
            stmt = stmt.where(
                ApprovalRequest.status == ApprovalStatus.PENDING.value,
                ApprovalRequest.expires_at > now,
            )
        elif status_filter == ApprovalStatusFilter.EXPIRED:
            stmt = stmt.where(
                ApprovalRequest.status == ApprovalStatus.PENDING.value,
                ApprovalRequest.expires_at <= now,
            )
        elif status_filter in (
            ApprovalStatusFilter.APPROVED,
            ApprovalStatusFilter.REJECTED,
            ApprovalStatusFilter.CANCELLED,
        ):
            stmt = stmt.where(ApprovalRequest.status == status_filter.value)

        # Keyset pagination: (requested_at, approval_id) < (cursor_requested_at, cursor_id)
        if cursor_requested_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    ApprovalRequest.requested_at < cursor_requested_at,
                    and_(
                        ApprovalRequest.requested_at == cursor_requested_at,
                        ApprovalRequest.approval_id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(
            ApprovalRequest.requested_at.desc(),
            ApprovalRequest.approval_id.desc(),
        ).limit(limit)

        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get_pending_count(
        self,
        approver_user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> int:
        """Return authoritative count of active pending approvals (excluding expired)."""
        stmt = (
            select(func.count())
            .select_from(ApprovalRequest)
            .where(
                ApprovalRequest.approver_user_id == approver_user_id,
                ApprovalRequest.status == ApprovalStatus.PENDING.value,
                ApprovalRequest.expires_at > now,
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one() or 0
