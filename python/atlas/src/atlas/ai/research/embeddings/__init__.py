"""Embeddings package for Stage 127 AI Research."""

from atlas.ai.research.embeddings.generation import (
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_MODEL_VERSION,
    AtlasDeterministicEmbeddingProvider,
)
from atlas.ai.research.embeddings.interface import EmbeddingProvider
from atlas.ai.research.embeddings.provider_registry import EmbeddingProviderRegistry

__all__ = [
    "EmbeddingProvider",
    "AtlasDeterministicEmbeddingProvider",
    "EmbeddingProviderRegistry",
    "DEFAULT_EMBEDDING_DIMENSIONS",
    "DEFAULT_MODEL_VERSION",
]
