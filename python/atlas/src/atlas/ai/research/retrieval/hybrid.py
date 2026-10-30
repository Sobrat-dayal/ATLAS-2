"""Hybrid Search and Reciprocal Rank Fusion for Stage 127 (Part XXV).

Combines lexical (BM25) and semantic (vector) rankings via Reciprocal Rank Fusion (RRF).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from atlas.ai.research.domain import ResearchChunk, RetrievalStrategy
from atlas.ai.research.retrieval.lexical import LexicalSearchEngine
from atlas.ai.research.retrieval.semantic import SemanticSearchEngine


class HybridRetrievalEngine:
    """Executes hybrid retrieval combining lexical and semantic results."""

    def __init__(self) -> None:
        self.lexical_engine = LexicalSearchEngine()
        self.semantic_engine = SemanticSearchEngine()

    async def retrieve(
        self,
        query: str,
        candidate_chunks: List[ResearchChunk],
        strategy: RetrievalStrategy = RetrievalStrategy.HYBRID_FUSION,
        limit: int = 5,
        rrf_k: int = 60,
    ) -> List[Tuple[ResearchChunk, float]]:
        """Retrieves and ranks chunks based on strategy."""
        if not candidate_chunks:
            return []

        if strategy == RetrievalStrategy.LEXICAL:
            lexical_ranked = [
                item
                for item in self.lexical_engine.score_chunks(query, candidate_chunks)
                if item[1] > 0.0
            ]
            return lexical_ranked[:limit]

        if strategy == RetrievalStrategy.SEMANTIC:
            semantic_ranked = [
                item
                for item in await self.semantic_engine.score_chunks(query, candidate_chunks)
                if item[1] > 0.15
            ]
            return semantic_ranked[:limit]

        # HYBRID_FUSION: Compute both and combine with Reciprocal Rank Fusion
        lexical_ranked = self.lexical_engine.score_chunks(query, candidate_chunks)
        semantic_ranked = await self.semantic_engine.score_chunks(query, candidate_chunks)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, ResearchChunk] = {c.chunk_id: c for c in candidate_chunks}

        for rank, (chunk, score) in enumerate(lexical_ranked):
            if score > 0.0:
                rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (
                    1.0 / (rrf_k + rank + 1)
                )

        for rank, (chunk, score) in enumerate(semantic_ranked):
            if score > 0.15:
                rrf_scores[chunk.chunk_id] = rrf_scores.get(chunk.chunk_id, 0.0) + (
                    1.0 / (rrf_k + rank + 1)
                )

        fused = [(chunk_map[chk_id], score) for chk_id, score in rrf_scores.items()]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:limit]
