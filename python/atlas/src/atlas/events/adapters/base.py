"""Base Abstract Ingestion Adapter for Universal Events (Stage 135)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from ..domain import AtlasUniversalEvent, EventSourceRecord


class BaseEventAdapter(ABC):
    """Abstract interface for source ingestion adapters."""

    def __init__(self, source_id: str):
        self.source_id = source_id

    @abstractmethod
    def parse_source_payload(
        self,
        raw_payload: Dict[str, Any],
        source_record: Optional[EventSourceRecord] = None,
    ) -> Tuple[AtlasUniversalEvent, List[Dict[str, Any]]]:
        """Parse an external source record into a canonical AtlasUniversalEvent and claims."""
        pass
