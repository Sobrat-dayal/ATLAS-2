"""Abstract base class for AI Model Providers."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from atlas.ai.domain import StreamEvent


class BaseAiProvider(ABC):
    """Abstract interface for AI model inference providers."""

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
        cancellation_check: Optional[Any] = None,
    ) -> AsyncIterator[StreamEvent]:
        """Stream chunks from the model provider via Server-Sent Event objects."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model_id: str,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        """Generate a complete non-streaming response."""
        pass

