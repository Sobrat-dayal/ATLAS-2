"""ATLAS Watchlist Enrichment Package (Stage 79).

Provides qualified financial enrichment capabilities:
- Company Fundamentals
- Valuation Ratios
- Technical Indicator Snapshots
- Corporate Events
- Earnings Metadata
- Canonical News References
"""

from .caching import EnrichmentCacheManager, default_enrichment_cache
from .events import CorporateEventsAdapter, register_verified_events_for_company
from .fundamentals import FundamentalDataAdapter, register_verified_statements_for_company
from .models import (
    EnrichmentCategory,
    EnrichmentColumnMetadata,
    EnrichmentStatus,
    WatchlistEnrichmentItemResult,
    WatchlistEnrichmentRequest,
    WatchlistEnrichmentResponse,
    WatchlistEnrichmentValue,
)
from .news import NewsReferenceAdapter, register_verified_articles_for_entity
from .planner import EnrichmentExecutionPlan, EnrichmentItemContext, EnrichmentPlanner
from .registry import (
    ENRICHMENT_CATALOG,
    ENRICHMENT_COLUMN_MAP,
    get_enrichment_metadata,
    is_enrichment_column,
    list_enrichment_columns,
)
from .router import router as watchlist_enrichment_router
from .service import WatchlistEnrichmentService
from .technicals import TechnicalIndicatorAdapter, register_verified_bars_for_series
from .valuation import ValuationRatiosAdapter

__all__ = [
    "EnrichmentCategory",
    "EnrichmentStatus",
    "WatchlistEnrichmentValue",
    "EnrichmentColumnMetadata",
    "WatchlistEnrichmentRequest",
    "WatchlistEnrichmentResponse",
    "WatchlistEnrichmentItemResult",
    "ENRICHMENT_CATALOG",
    "ENRICHMENT_COLUMN_MAP",
    "get_enrichment_metadata",
    "is_enrichment_column",
    "list_enrichment_columns",
    "default_enrichment_cache",
    "EnrichmentCacheManager",
    "FundamentalDataAdapter",
    "register_verified_statements_for_company",
    "ValuationRatiosAdapter",
    "TechnicalIndicatorAdapter",
    "register_verified_bars_for_series",
    "CorporateEventsAdapter",
    "register_verified_events_for_company",
    "NewsReferenceAdapter",
    "register_verified_articles_for_entity",
    "EnrichmentPlanner",
    "EnrichmentItemContext",
    "EnrichmentExecutionPlan",
    "WatchlistEnrichmentService",
    "watchlist_enrichment_router",
]
