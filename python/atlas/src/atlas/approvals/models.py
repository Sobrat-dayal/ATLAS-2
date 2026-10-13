"""SQLAlchemy models and Pydantic schemas for ATLAS Approval Requests (Stage 54)."""

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from atlas.database import Base

from .enums import ApprovalDecisionType, ApprovalStatus


class ApprovalRequest(Base):
    """Authoritative durable approval request stored in PostgreSQL."""

    __tablename__ = "approval_requests"

    approval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    approver_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    producer_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    action_kind: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    proposal_reference: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    proposal_digest: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=ApprovalStatus.PENDING.value,
        nullable=False,
    )
    requested_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    decided_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    decided_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    decision: Mapped[Optional["ApprovalDecision"]] = relationship(
        "ApprovalDecision",
        back_populates="request",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')",
            name="ck_approval_request_status",
        ),
        Index(
            "uq_approval_requests_producer_idempotency",
            "producer_key",
            "idempotency_key",
            "approver_user_id",
            unique=True,
        ),
        Index(
            "ix_approval_requests_approver_status_expires",
            "approver_user_id",
            "status",
            "expires_at",
        ),
        Index(
            "ix_approval_requests_approver_requested",
            "approver_user_id",
            func.text("requested_at DESC"),
            func.text("approval_id DESC"),
        ),
    )


class ApprovalDecision(Base):
    """Immutable audit record of a human decision on an approval request."""

    __tablename__ = "approval_decisions"

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    approval_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("approval_requests.approval_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    approver_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    decided_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    decision_idempotency_key: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    request: Mapped["ApprovalRequest"] = relationship(
        "ApprovalRequest",
        back_populates="decision",
    )

    __table_args__ = (
        CheckConstraint(
            "decision IN ('APPROVE', 'REJECT')",
            name="ck_approval_decision_type",
        ),
        Index(
            "uq_approval_decisions_approver_idempotency",
            "approver_user_id",
            "decision_idempotency_key",
            unique=True,
        ),
    )


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------


class CreateApprovalInternalRequest(BaseModel):
    """Payload used by trusted internal producers to originate an approval request."""

    producer_key: str = Field(..., max_length=64)
    approver_user_id: uuid.UUID
    action_kind: str = Field(..., max_length=64)
    proposal_reference: str = Field(..., max_length=256)
    proposal_digest: str = Field(..., min_length=64, max_length=64)
    title: str = Field(..., min_length=1, max_length=160)
    summary: str = Field(..., min_length=1, max_length=2000)
    expires_at: datetime.datetime
    idempotency_key: str = Field(..., min_length=1, max_length=64)

    model_config = ConfigDict(extra="forbid")

    @field_validator("proposal_digest")
    @classmethod
    def validate_digest_hex(cls, v: str) -> str:
        if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
            raise ValueError("proposal_digest must be a 64-character hexadecimal SHA-256 string")
        return v.lower()


class ApprovalDecisionRequest(BaseModel):
    """Decision submitted by the authorized human approver."""

    decision: ApprovalDecisionType
    decision_idempotency_key: uuid.UUID
    reason: Optional[str] = Field(None, max_length=500)
    expected_version: Optional[int] = Field(None, ge=1)

    model_config = ConfigDict(extra="forbid")


class ApprovalItemResponse(BaseModel):
    """Compact summary of an approval request for lists."""

    approval_id: uuid.UUID
    approver_user_id: uuid.UUID
    producer_key: str
    action_kind: str
    proposal_reference: str
    title: str
    summary: str
    status: ApprovalStatus
    effective_status: str
    requested_at: datetime.datetime
    expires_at: datetime.datetime
    decided_at: Optional[datetime.datetime] = None
    decided_by_user_id: Optional[uuid.UUID] = None
    version: int
    is_expired: bool

    model_config = ConfigDict(from_attributes=True)


class ApprovalDetailResponse(ApprovalItemResponse):
    """Full detail view for evaluating an approval request before decision."""

    proposal_digest: str
    reason: Optional[str] = None


class ApprovalDecisionResponse(BaseModel):
    """Authoritative response confirming recorded human decision."""

    decision_id: uuid.UUID
    approval_id: uuid.UUID
    approver_user_id: uuid.UUID
    decision: ApprovalDecisionType
    decided_at: datetime.datetime
    status: ApprovalStatus
    version: int


class ApprovalListResponse(BaseModel):
    """Paginated list of approval requests with authoritative pending count."""

    schema_version: str = "1.0"
    items: list[ApprovalItemResponse]
    pending_count: int
    next_cursor: Optional[str] = None
    has_more: bool = False


class ApprovalCountsResponse(BaseModel):
    """Authoritative count of pending approval requests."""

    pending_count: int
