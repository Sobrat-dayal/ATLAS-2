"""SQLAlchemy ORM models for Stage 127: AI Research and Retrieval-Augmented Generation.

Defines tables for research sources, documents, revisions, chunks, embeddings,
research runs, citations, and evidence manifests.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from atlas.infrastructure.database import Base


class ResearchSourceModel(Base):
    """Registered source or publisher of research and regulatory documents."""

    __tablename__ = "research_sources"

    source_id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    licensing_class = Column(String(64), nullable=False, default="PUBLIC_DOMAIN")
    provider_disclosure = Column(String(64), nullable=False, default="ALLOWED")
    publisher = Column(String(255), nullable=False)
    reliability_tier = Column(String(64), nullable=False, default="PRIMARY_REGULATORY")
    owner_user_id = Column(String(64), nullable=True, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ResearchDocumentModel(Base):
    """Canonical document record (10-K, transcript, analyst report, memo)."""

    __tablename__ = "research_documents"

    document_id = Column(String(64), primary_key=True)
    source_id = Column(
        String(64), ForeignKey("research_sources.source_id"), nullable=False, index=True
    )
    title = Column(String(255), nullable=False)
    document_type = Column(String(64), nullable=False, index=True)
    publication_date = Column(String(64), nullable=False, index=True)
    company_id = Column(String(64), nullable=True, index=True)
    symbol = Column(String(32), nullable=True, index=True)
    filing_date = Column(String(64), nullable=True)
    period_end_date = Column(String(64), nullable=True)
    access_tier = Column(String(32), nullable=False, default="PUBLIC")
    owner_user_id = Column(String(64), nullable=True, index=True)
    tenant_id = Column(String(64), nullable=True, index=True)
    is_revoked = Column(Boolean, nullable=False, default=False, index=True)
    content_hash = Column(String(64), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ResearchDocumentRevisionModel(Base):
    """Document revision or accounting restatement representing point-in-time truth."""

    __tablename__ = "research_document_revisions"

    revision_id = Column(String(64), primary_key=True)
    document_id = Column(
        String(64), ForeignKey("research_documents.document_id"), nullable=False, index=True
    )
    revision_number = Column(Integer, nullable=False, default=1)
    effective_date = Column(String(64), nullable=False, index=True)
    as_of_date = Column(String(64), nullable=False, index=True)
    is_restatement = Column(Boolean, nullable=False, default=False)
    content_hash = Column(String(64), nullable=False)
    summary = Column(Text, nullable=True)


class ResearchDocumentChunkModel(Base):
    """Structurally bounded passage belonging to a document revision."""

    __tablename__ = "research_document_chunks"

    chunk_id = Column(String(64), primary_key=True)
    document_id = Column(
        String(64), ForeignKey("research_documents.document_id"), nullable=False, index=True
    )
    revision_id = Column(String(64), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    section_title = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    clean_text = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=False)
    char_end = Column(Integer, nullable=False)
    token_estimate = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False)
    metadata_json = Column(JSONB, nullable=False, default=dict)


class AiResearchRunModel(Base):
    """Record of a research generation run."""

    __tablename__ = "ai_research_runs"

    run_id = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(64), nullable=False, index=True)
    query = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, index=True)
    strategy = Column(String(32), nullable=False)
    answer_text = Column(Text, nullable=False, default="")
    limitations = Column(JSONB, nullable=False, default=list)
    conversation_id = Column(String(64), nullable=True, index=True)
    execution_time_ms = Column(Float, nullable=False, default=0.0)
    started_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AiResearchCitationModel(Base):
    """Verified claim citation backing research answers."""

    __tablename__ = "ai_research_citations"

    citation_id = Column(String(64), primary_key=True)
    run_id = Column(String(64), ForeignKey("ai_research_runs.run_id"), nullable=False, index=True)
    evidence_id = Column(String(64), nullable=False)
    document_id = Column(String(64), nullable=False, index=True)
    symbol = Column(String(32), nullable=True)
    title = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=False)
    section_title = Column(String(255), nullable=False)
    publication_date = Column(String(64), nullable=False)
    claim_text = Column(Text, nullable=False)
    quote_span = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="VERIFIED")
    validation_reason = Column(Text, nullable=True)
