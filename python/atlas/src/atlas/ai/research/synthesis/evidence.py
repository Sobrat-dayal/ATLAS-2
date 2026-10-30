"""Evidence Extraction for Stage 127 AI Research (Part XXXVII & XXXVIII)."""

from __future__ import annotations

from atlas.ai.research.domain import (
    ResearchChunk,
    ResearchDocument,
    ResearchEvidence,
    ResearchSource,
)


def build_evidence_unit(
    chunk: ResearchChunk,
    document: ResearchDocument,
    source: ResearchSource,
    score: float,
) -> ResearchEvidence:
    """Constructs a verified ResearchEvidence instance from a retrieved chunk."""
    ev_id = f"ev_{chunk.chunk_id}"
    exact_span = chunk.clean_text[:300] if len(chunk.clean_text) > 300 else chunk.clean_text

    return ResearchEvidence(
        evidence_id=ev_id,
        chunk_id=chunk.chunk_id,
        document_id=document.document_id,
        revision_id=chunk.revision_id,
        title=document.title,
        symbol=document.symbol,
        page_number=chunk.page_number,
        section_title=chunk.section_title,
        publication_date=document.publication_date,
        effective_date=document.filing_date or document.publication_date,
        exact_span=exact_span,
        context_snippet=chunk.clean_text,
        relevance_score=round(score, 4),
        licensing_class=source.licensing_class,
        content_hash=chunk.content_hash,
        publisher=source.publisher,
    )
