"""SQLAlchemy models and Pydantic schemas for ATLAS Personal Tasks (Stage 54)."""

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
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base

from .enums import TaskStatus


class UserTask(Base):
    """Authoritative user-owned personal task stored in PostgreSQL."""

    __tablename__ = "user_tasks"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=TaskStatus.OPEN.value,
        nullable=False,
    )
    due_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    module_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('OPEN', 'COMPLETED', 'CANCELLED')",
            name="ck_user_tasks_status",
        ),
        CheckConstraint(
            "length(trim(title)) > 0",
            name="ck_user_tasks_title_not_empty",
        ),
        Index(
            "ix_user_tasks_owner_status_due",
            "owner_user_id",
            "status",
            "due_at",
        ),
        Index(
            "ix_user_tasks_owner_created_id",
            "owner_user_id",
            func.text("created_at DESC"),
            func.text("task_id DESC"),
        ),
        Index(
            "uq_user_tasks_owner_idempotency",
            "owner_user_id",
            "idempotency_key",
            unique=True,
            postgresql_where=(idempotency_key.isnot(None)),
        ),
    )


# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------


class CreateTaskRequest(BaseModel):
    """Payload to create a new personal task."""

    title: str = Field(..., min_length=1, max_length=160, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Optional explanation")
    due_at: Optional[datetime.datetime] = Field(None, description="Optional deadline in UTC")
    module_id: Optional[str] = Field(
        None, max_length=64, description="Optional canonical module ID"
    )
    entity_id: Optional[uuid.UUID] = Field(None, description="Optional canonical Entity UUID")
    idempotency_key: Optional[str] = Field(
        None, max_length=64, description="Client idempotency token"
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped

    @field_validator("description")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        return stripped if stripped else None


class UpdateTaskRequest(BaseModel):
    """Payload to update an existing personal task."""

    title: Optional[str] = Field(None, min_length=1, max_length=160, description="Updated title")
    description: Optional[str] = Field(None, max_length=2000, description="Updated description")
    due_at: Optional[datetime.datetime] = Field(None, description="Updated due date")
    clear_due_at: bool = Field(False, description="Explicitly remove due date")
    module_id: Optional[str] = Field(None, max_length=64, description="Updated module ID")
    clear_module_id: bool = Field(False, description="Explicitly remove module context")
    entity_id: Optional[uuid.UUID] = Field(None, description="Updated canonical Entity UUID")
    clear_entity_id: bool = Field(False, description="Explicitly remove Entity context")
    expected_version: Optional[int] = Field(
        None, ge=1, description="Expected task version for optimistic locking"
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        if not stripped:
            raise ValueError("Task title cannot be empty or whitespace only")
        return stripped


class TaskResponse(BaseModel):
    """Public representation of a personal task."""

    task_id: uuid.UUID
    owner_user_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_at: Optional[datetime.datetime] = None
    module_id: Optional[str] = None
    module_label: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    entity_display_name: Optional[str] = None
    entity_type: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    cancelled_at: Optional[datetime.datetime] = None
    version: int
    is_overdue: bool
    is_due_soon: bool

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Paginated list of personal tasks with authoritative summary counts."""

    schema_version: str = "1.0"
    items: list[TaskResponse]
    open_count: int
    overdue_count: int
    next_cursor: Optional[str] = None
    has_more: bool = False


class TaskCountsResponse(BaseModel):
    """Authoritative task counts for the authenticated user."""

    open_count: int
    overdue_count: int
