"""Base abstract class for ATLAS AI Context Adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from atlas.ai.context.domain import AtlasAiContextItem, ContextType


class BaseAiContextAdapter(ABC):
    """Abstract interface for module-specific context extraction and formatting."""

    @property
    @abstractmethod
    def adapter_id(self) -> str:
        """Unique identifier for this adapter."""
        pass

    @property
    @abstractmethod
    def context_type(self) -> ContextType:
        """Canonical context category."""
        pass

    @property
    @abstractmethod
    def supported_module(self) -> str:
        """Primary module associated with this adapter."""
        pass

    @abstractmethod
    async def resolve(
        self,
        target_id: str,
        user_id: str,
        tenant_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> AtlasAiContextItem:
        """Resolves authorized, source-backed context data for the target entity/resource."""
        pass

    @abstractmethod
    def summarize_for_model(self, item: AtlasAiContextItem) -> str:
        """Compresses the structured payload into a clean, source-grounded text block for LLM prompt context."""
        pass
