"""News Ingestion Subsystem (Stage 99)."""

from atlas.news.ingestion.adapters import (
    BaseNewsAdapter,
    FinancialWireNewsAdapter,
    OpenBBNewsAdapter,
    RegulatoryAnnouncementsAdapter,
)
from atlas.news.ingestion.cursors import (
    IngestionCursor,
    IngestionCursorStore,
    default_cursor_store,
)

__all__ = [
    "BaseNewsAdapter",
    "OpenBBNewsAdapter",
    "FinancialWireNewsAdapter",
    "RegulatoryAnnouncementsAdapter",
    "IngestionCursor",
    "IngestionCursorStore",
    "default_cursor_store",
]
