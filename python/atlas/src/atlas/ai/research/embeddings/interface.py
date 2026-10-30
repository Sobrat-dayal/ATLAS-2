"""Embedding Provider Abstraction for Stage 127 AI Research (Part XIX)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract interface for generating vector embeddings."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Identifier of the embedding provider."""
        ...

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version identifier of the embedding model."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Number of dimensions in generated vectors."""
        ...

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generates a normalized float vector for the input text."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates normalized float vectors for a batch of texts."""
        ...
