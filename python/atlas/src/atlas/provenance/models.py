import datetime
import uuid
from typing import Optional

from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    Numeric,
    func,
    text,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database import Base


class ProvenanceSource(Base):
    __tablename__ = "provenance_sources"

    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_key: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    source_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

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
        CheckConstraint("length(name) > 0", name="chk_provenance_source_name_empty"),
        CheckConstraint(
            "source_key IS NULL OR source_key ~ '^[a-z0-9][a-z0-9._-]{0,127}$'",
            name="chk_provenance_source_key_format"
        ),
    )


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    provenance_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provenance_sources.source_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    record_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    source_reference: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    source_uri: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    source_locator: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    published_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    observed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    license_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    license_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    attribution_text: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    content_hash_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "content_hash_sha256 IS NULL OR content_hash_sha256 ~ '^[0-9a-f]{64}$'",
            name="chk_provenance_record_hash_format"
        ),
    )


class EntityProvenanceLink(Base):
    __tablename__ = "entity_provenance_links"

    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.entity_id", ondelete="CASCADE"), primary_key=True
    )
    provenance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provenance_records.provenance_id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    evidence_role: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="chk_entity_prov_confidence"
        ),
    )


class IdentifierProvenanceLink(Base):
    __tablename__ = "identifier_provenance_links"

    identifier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entity_identifiers.identifier_id", ondelete="CASCADE"), primary_key=True
    )
    provenance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provenance_records.provenance_id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    evidence_role: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="chk_identifier_prov_confidence"
        ),
    )


class AliasProvenanceLink(Base):
    __tablename__ = "alias_provenance_links"

    alias_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entity_aliases.alias_id", ondelete="CASCADE"), primary_key=True
    )
    provenance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provenance_records.provenance_id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    evidence_role: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="chk_alias_prov_confidence"
        ),
    )


class RelationshipProvenanceLink(Base):
    __tablename__ = "relationship_provenance_links"

    relationship_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entity_relationships.relationship_id", ondelete="CASCADE"), primary_key=True
    )
    provenance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("provenance_records.provenance_id", ondelete="RESTRICT"), primary_key=True, index=True
    )
    evidence_role: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="chk_relationship_prov_confidence"
        ),
    )
