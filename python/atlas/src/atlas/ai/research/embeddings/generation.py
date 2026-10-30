"""Deterministic Normalized Embedding Generator for Stage 127 AI Research (Part XIX)."""

from __future__ import annotations

import hashlib
import math
from typing import List

from atlas.ai.research.embeddings.interface import EmbeddingProvider

DEFAULT_EMBEDDING_DIMENSIONS = 384
DEFAULT_MODEL_VERSION = "atlas-fin-embed-v1"


class AtlasDeterministicEmbeddingProvider(EmbeddingProvider):
    """Generates high-fidelity, deterministic, L2-normalized 384-dimensional embeddings.

    Uses stable token hashing and dense projection with unit normalization,
    ensuring dot-product directly yields cosine similarity.
    """

    def __init__(
        self,
        dimensions: int = DEFAULT_EMBEDDING_DIMENSIONS,
        model_version: str = DEFAULT_MODEL_VERSION,
    ) -> None:
        self._dimensions = dimensions
        self._model_version = model_version

    @property
    def provider_id(self) -> str:
        return "atlas_deterministic"

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def dimensions(self) -> int:
        return self._dimensions

    async def embed_text(self, text: str) -> List[float]:
        return self._compute_embedding(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._compute_embedding(t) for t in texts]

    def _compute_embedding(self, text: str) -> List[float]:
        """Computes a normalized dense vector from text."""
        vec = [0.0] * self._dimensions
        tokens = text.lower().split()
        if not tokens:
            # Non-zero default unit vector for empty text
            vec[0] = 1.0
            return vec

        for idx, token in enumerate(tokens):
            # Generate deterministic hashes for each token
            h = hashlib.sha256(token.encode()).digest()
            # Spread across dimensions
            for i in range(0, min(len(h), 32), 2):
                dim_idx = (h[i] * 256 + h[i + 1]) % self._dimensions
                sign = 1.0 if h[i] % 2 == 0 else -1.0
                weight = 1.0 / math.sqrt(idx + 1)
                vec[dim_idx] += sign * weight

        # Calculate L2 norm and normalize to unit sphere
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec

