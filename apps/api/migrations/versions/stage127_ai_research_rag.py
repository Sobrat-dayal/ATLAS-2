"""stage127_ai_research_rag

Revision ID: stage127_ai_research_rag
Revises: stage126_ai_tool_gateway
Create Date: 2026-10-30 00:00:00.000000

Stage 127 — AI Research and Retrieval-Augmented Generation:
- research_sources: Regulatory & institutional research source registry with licensing and disclosure rules.
- research_documents: Canonical documents with filing dates, publication dates, and access tiers.
- research_document_revisions: Point-in-time document revisions and restatements.
- research_document_chunks: Structurally bounded chunk passages with page numbers and offsets.
- ai_research_runs: Grounded research run execution records.
- ai_research_citations: Server-authoritative claim citations.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "stage127_ai_research_rag"
down_revision: Union[str, Sequence[str], None] = "stage126_ai_tool_gateway"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. research_sources
    op.create_table(
        "research_sources",
        sa.Column("source_id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("licensing_class", sa.String(length=64), nullable=False, server_default="PUBLIC_DOMAIN"),
        sa.Column("provider_disclosure", sa.String(length=64), nullable=False, server_default="ALLOWED"),
        sa.Column("publisher", sa.String(length=255), nullable=False),
        sa.Column("reliability_tier", sa.String(length=64), nullable=False, server_default="PRIMARY_REGULATORY"),
        sa.Column("owner_user_id", sa.String(length=64), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_sources_category", "research_sources", ["category"])
    op.create_index("ix_research_sources_tenant_id", "research_sources", ["tenant_id"])

    # 2. research_documents
    op.create_table(
        "research_documents",
        sa.Column("document_id", sa.String(length=64), primary_key=True),
        sa.Column("source_id", sa.String(length=64), sa.ForeignKey("research_sources.source_id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("publication_date", sa.String(length=64), nullable=False),
        sa.Column("company_id", sa.String(length=64), nullable=True),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("filing_date", sa.String(length=64), nullable=True),
        sa.Column("period_end_date", sa.String(length=64), nullable=True),
        sa.Column("access_tier", sa.String(length=32), nullable=False, server_default="PUBLIC"),
        sa.Column("owner_user_id", sa.String(length=64), nullable=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=True),
        sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_research_documents_source_id", "research_documents", ["source_id"])
    op.create_index("ix_research_documents_symbol", "research_documents", ["symbol"])
    op.create_index("ix_research_documents_publication_date", "research_documents", ["publication_date"])
    op.create_index("ix_research_documents_tenant_id", "research_documents", ["tenant_id"])

    # 3. research_document_revisions
    op.create_table(
        "research_document_revisions",
        sa.Column("revision_id", sa.String(length=64), primary_key=True),
        sa.Column("document_id", sa.String(length=64), sa.ForeignKey("research_documents.document_id"), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("effective_date", sa.String(length=64), nullable=False),
        sa.Column("as_of_date", sa.String(length=64), nullable=False),
        sa.Column("is_restatement", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
    )
    op.create_index("ix_research_document_revisions_doc_id", "research_document_revisions", ["document_id"])

    # 4. research_document_chunks
    op.create_table(
        "research_document_chunks",
        sa.Column("chunk_id", sa.String(length=64), primary_key=True),
        sa.Column("document_id", sa.String(length=64), sa.ForeignKey("research_documents.document_id"), nullable=False),
        sa.Column("revision_id", sa.String(length=64), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("section_title", sa.String(length=255), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("clean_text", sa.Text(), nullable=False),
        sa.Column("char_start", sa.Integer(), nullable=False),
        sa.Column("char_end", sa.Integer(), nullable=False),
        sa.Column("token_estimate", sa.Integer(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
    )
    op.create_index("ix_research_document_chunks_doc_id", "research_document_chunks", ["document_id"])

    # 5. ai_research_runs
    op.create_table(
        "ai_research_runs",
        sa.Column("run_id", sa.String(length=64), primary_key=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("strategy", sa.String(length=32), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("limitations", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("conversation_id", sa.String(length=64), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_ai_research_runs_user_id", "ai_research_runs", ["user_id"])
    op.create_index("ix_ai_research_runs_tenant_id", "ai_research_runs", ["tenant_id"])

    # 6. ai_research_citations
    op.create_table(
        "ai_research_citations",
        sa.Column("citation_id", sa.String(length=64), primary_key=True),
        sa.Column("run_id", sa.String(length=64), sa.ForeignKey("ai_research_runs.run_id"), nullable=False),
        sa.Column("evidence_id", sa.String(length=64), nullable=False),
        sa.Column("document_id", sa.String(length=64), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("section_title", sa.String(length=255), nullable=False),
        sa.Column("publication_date", sa.String(length=64), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("quote_span", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="VERIFIED"),
        sa.Column("validation_reason", sa.Text(), nullable=True),
    )
    op.create_index("ix_ai_research_citations_run_id", "ai_research_citations", ["run_id"])


def downgrade() -> None:
    op.drop_table("ai_research_citations")
    op.drop_table("ai_research_runs")
    op.drop_table("research_document_chunks")
    op.drop_table("research_document_revisions")
    op.drop_table("research_documents")
    op.drop_table("research_sources")

