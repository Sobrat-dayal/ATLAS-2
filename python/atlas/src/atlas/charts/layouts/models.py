"""SQLAlchemy Declarative Model for Saved Chart Layouts (Stage 74).

PostgreSQL-backed storage for persistent multi-chart workspace configurations:
- Owner-scoped isolation (owner_user_id)
- Monotonic revision for optimistic concurrency control (ETag / If-Match)
- Document schema versioning (document_schema_version)
- Validated JSONB configuration aggregate (layout_document)
- Unique normalized names per owner
- At most one default layout per owner
"""

import datetime
import uuid
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class ChartLayoutModel(Base):
    """
    Authoritative persistent chart workspace configuration document stored in PostgreSQL.
    """

    __tablename__ = "chart_layouts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    normalized_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    document_schema_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    revision: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=1,
    )

    layout_document: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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

    __table_args__ = (
        UniqueConstraint(
            "owner_user_id",
            "normalized_name",
            name="uq_chart_layouts_owner_normalized_name",
        ),
        Index(
            "uq_chart_layouts_owner_default",
            "owner_user_id",
            unique=True,
            postgresql_where=text("is_default = TRUE"),
        ),
        Index(
            "ix_chart_layouts_owner_updated",
            "owner_user_id",
            text("updated_at DESC"),
        ),
    )
