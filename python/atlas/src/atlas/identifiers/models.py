import uuid
from datetime import date
from typing import Optional

from sqlalchemy import (
    UUID,
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class IdentifierScheme(Base):
    __tablename__ = "identifier_schemes"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    scope_policy: Mapped[str] = mapped_column(String(64), nullable=False)
    normalization_strategy: Mapped[str] = mapped_column(String(64), nullable=False)
    case_sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    max_length: Mapped[int] = mapped_column(Integer, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")


class EntityIdentifier(Base):
    __tablename__ = "entity_identifiers"

    identifier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scheme_key: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("identifier_schemes.key", ondelete="RESTRICT"),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str] = mapped_column(Text, nullable=False)
    scope_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("entities.entity_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    namespace: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    valid_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    valid_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "length(trim(value)) > 0",
            name="ck_entity_identifiers_value_not_empty",
        ),
        CheckConstraint(
            "length(trim(normalized_value)) > 0",
            name="ck_entity_identifiers_normalized_value_not_empty",
        ),
        CheckConstraint(
            "namespace IS NULL OR length(trim(namespace)) > 0",
            name="ck_entity_identifiers_namespace_not_empty",
        ),
        CheckConstraint(
            "((is_current = TRUE) AND (valid_to IS NULL)) OR ((is_current = FALSE) AND (valid_to IS NOT NULL))",
            name="ck_entity_identifiers_current_history",
        ),
        CheckConstraint(
            "valid_from IS NULL OR valid_to IS NULL OR valid_from <= valid_to",
            name="ck_entity_identifiers_validity_dates",
        ),
        # Unique current lookup
        Index(
            "ix_entity_identifiers_current_lookup",
            "scheme_key",
            "normalized_value",
            text("COALESCE(scope_entity_id, '00000000-0000-0000-0000-000000000000'::uuid)"),
            text("COALESCE(namespace, '')"),
            postgresql_where=text("is_current = TRUE"),
            unique=True,
        ),
        # Unique current entity assignment (prevent multiple current IDs for same entity+scheme+scope)
        Index(
            "ix_entity_identifiers_current_assignment",
            "entity_id",
            "scheme_key",
            text("COALESCE(scope_entity_id, '00000000-0000-0000-0000-000000000000'::uuid)"),
            text("COALESCE(namespace, '')"),
            postgresql_where=text("is_current = TRUE"),
            unique=True,
        ),
    )
