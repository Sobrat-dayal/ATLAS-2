"""Semantic Vector Search Engine for Stage 127 (Part XXIV).

Performs cosine similarity search between query embeddings and chunk embeddings.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from atlas.ai.research.domain import ResearchChunk
from atlas.ai.research.embeddings.provider_registry import EmbeddingProviderRegistry


class SemanticSearchEngine:
    """Computes cosine similarity ranking between query and chunks."""

    def __init__(self) -> None:
        self.embedding_registry = EmbeddingProviderRegistry.get_instance()
        self._cached_embeddings: Dict[str, List[float]] = {}

    async def score_chunks(
        self,
        query: str,
        chunks: List[ResearchChunk],
    ) -> List[Tuple[ResearchChunk, float]]:
        """Calculates cosine similarity between query and candidate chunks."""
        if not chunks:
            return []

        provider = self.embedding_registry.get_provider()
        query_vec = await provider.embed_text(query)

        scored: List[Tuple[ResearchChunk, float]] = []

        for chunk in chunks:
            chk_vec = self._cached_embeddings.get(chunk.chunk_id)
            if chk_vec is None:
                chk_vec = await provider.embed_text(chunk.clean_text)
                self._cached_embeddings[chunk.chunk_id] = chk_vec

            # Cosine similarity (vectors are unit-normalized)
            dot = sum(q * c for q, c in zip(query_vec, chk_vec))
            scored.append((chunk, float(dot)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

