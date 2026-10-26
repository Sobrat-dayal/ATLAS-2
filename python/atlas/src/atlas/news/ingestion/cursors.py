"""Incremental Ingestion Watermarks and Cursors (Stage 99)."""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class IngestionCursor(BaseModel):
    """Tracks incremental ingestion checkpoint for an authorized source."""

    source_id: str
    last_ingested_timestamp: datetime
    last_article_id: Optional[str] = None
    records_ingested_total: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(frozen=True)


class IngestionCursorStore:
    """Thread-safe storage for provider cursors."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cursors: Dict[str, IngestionCursor] = {}

    def get_cursor(self, source_id: str) -> Optional[IngestionCursor]:
        with self._lock:
            return self._cursors.get(source_id)

    def update_cursor(
        self,
        source_id: str,
        last_timestamp: datetime,
        last_article_id: Optional[str] = None,
        count: int = 0,
    ) -> IngestionCursor:
        with self._lock:
            prev = self._cursors.get(source_id)
            prev_total = prev.records_ingested_total if prev else 0
            cur = IngestionCursor(
                source_id=source_id,
                last_ingested_timestamp=last_timestamp,
                last_article_id=last_article_id,
                records_ingested_total=prev_total + count,
                updated_at=datetime.now(timezone.utc),
            )
            self._cursors[source_id] = cur
            return cur

    def clear(self) -> None:
        with self._lock:
            self._cursors.clear()


default_cursor_store = IngestionCursorStore()
