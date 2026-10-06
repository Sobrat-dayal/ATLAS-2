import datetime
import uuid
from typing import Optional

from sqlalchemy import UUID, Boolean, Date, DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class RelationshipType(Base):
    __tablename__ = "relationship_types"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    inverse_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    canonical_key: Mapped[str] = mapped_column(String(128), nullable=False)
    is_symmetric: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_policy_key: Mapped[str] = mapped_column(String(128), nullable=False)
    target_policy_key: Mapped[str] = mapped_column(String(128), nullable=False)
    allows_self: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class EntityRelationship(Base):
    __tablename__ = "entity_relationships"

    relationship_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    relationship_type_key: Mapped[str] = mapped_column(
        ForeignKey("relationship_types.key", ondelete="RESTRICT"), nullable=False
    )
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="CASCADE"), nullable=False, index=True
    )

    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    valid_from: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    valid_to: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "uq_entity_relationships_current",
            "relationship_type_key",
            "source_entity_id",
            "target_entity_id",
            unique=True,
            postgresql_where=text("is_current = true"),
        ),
    )
