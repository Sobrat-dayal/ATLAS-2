"""Embedding Registry and Version Management for Stage 127."""

from __future__ import annotations

from typing import Dict, Optional

from atlas.ai.research.embeddings.generation import (
    AtlasDeterministicEmbeddingProvider,
)
from atlas.ai.research.embeddings.interface import EmbeddingProvider
from atlas.ai.research.errors import ResearchEmbeddingUnavailableError


class EmbeddingProviderRegistry:
    """Singleton registry for embedding providers."""

    _instance: Optional[EmbeddingProviderRegistry] = None

    def __init__(self) -> None:
        self._providers: Dict[str, EmbeddingProvider] = {}
        # Register default deterministic provider
        self.register_provider(AtlasDeterministicEmbeddingProvider())

    @classmethod
    def get_instance(cls) -> EmbeddingProviderRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_provider(self, provider: EmbeddingProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: Optional[str] = None) -> EmbeddingProvider:
        if not provider_id:
            provider_id = "atlas_deterministic"
        provider = self._providers.get(provider_id)
        if not provider:
            raise ResearchEmbeddingUnavailableError(
                provider_id, f"Provider '{provider_id}' is not registered."
            )
        return provider
