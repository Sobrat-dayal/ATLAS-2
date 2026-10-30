"""Deduplication and Reranking for Stage 127 AI Research (Part XXVIII & XXIX)."""

from __future__ import annotations

from typing import List, Set, Tuple

from atlas.ai.research.domain import ResearchChunk


def deduplicate_chunks(
    ranked_chunks: List[Tuple[ResearchChunk, float]],
) -> List[Tuple[ResearchChunk, float]]:
    """Deduplicates redundant chunks while preserving distinct document revisions."""
    seen_hashes: Set[str] = set()
    deduped: List[Tuple[ResearchChunk, float]] = []

    for chunk, score in ranked_chunks:
        # Key on content hash combined with revision id to allow intentional restatement revisions
        unique_key = f"{chunk.revision_id}_{chunk.content_hash}"
        if unique_key not in seen_hashes:
            seen_hashes.add(unique_key)
            deduped.append((chunk, score))

    return deduped


def rerank_evidence(
    ranked_chunks: List[Tuple[ResearchChunk, float]],
    reliability_tier: str = "PRIMARY_REGULATORY",
) -> List[Tuple[ResearchChunk, float]]:
    """Applies institutional reranking boost for primary regulatory filings."""
    boosted: List[Tuple[ResearchChunk, float]] = []

    for chunk, score in ranked_chunks:
        adj = score
        # Give modest boost if chunk is from audited 10-K / 10-Q
        if "10-k" in chunk.section_title.lower() or "consolidated" in chunk.section_title.lower():
            adj *= 1.15
        boosted.append((chunk, adj))

    boosted.sort(key=lambda x: x[1], reverse=True)
    return boosted
