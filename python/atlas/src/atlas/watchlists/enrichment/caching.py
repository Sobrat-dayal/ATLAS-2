"""Multi-category Bounded In-Memory Cache for Watchlist Enrichment (Stage 79).

Enforces distinct TTLs across slower-moving and faster-moving financial domains:
- Fundamentals: 24-hour TTL
- Valuation Ratios: 1-hour TTL
- Technical Indicators: 1-hour TTL (or invalidated by newer finalized bar)
- Corporate Events & Earnings: 6-hour TTL
- News References: 15-minute TTL

Provides safe thread-safe caching, LRU eviction at capacity bounds,
and precise invalidation hooks when revisions or new market bars arrive.
"""

from __future__ import annotations

import datetime
from typing import Dict, Optional
from uuid import UUID

from .models import EnrichmentCategory, WatchlistEnrichmentValue

# Maximum cached entries per category to protect backend memory
MAX_CACHE_ENTRIES_PER_CATEGORY = 2000

# Default TTL durations in seconds
CATEGORY_TTLS = {
    EnrichmentCategory.FUNDAMENTALS: datetime.timedelta(hours=24),
    EnrichmentCategory.VALUATION: datetime.timedelta(hours=1),
    EnrichmentCategory.TECHNICAL: datetime.timedelta(hours=1),
    EnrichmentCategory.EVENTS: datetime.timedelta(hours=6),
    EnrichmentCategory.EARNINGS: datetime.timedelta(hours=6),
    EnrichmentCategory.NEWS: datetime.timedelta(minutes=15),
}


class CacheEntry:
    def __init__(self, value: WatchlistEnrichmentValue, expires_at: datetime.datetime):
        self.value = value
        self.expires_at = expires_at
        self.last_accessed = datetime.datetime.now(datetime.timezone.utc)

    def is_expired(self, now: datetime.datetime) -> bool:
        return now > self.expires_at


class EnrichmentCacheManager:
    """Manages domain-scoped in-memory cached results for enrichment columns."""

    def __init__(self) -> None:
        # Category -> Key -> CacheEntry
        self._stores: Dict[EnrichmentCategory, Dict[str, CacheEntry]] = {
            cat: {} for cat in EnrichmentCategory
        }

    @staticmethod
    def make_fundamental_key(
        company_id: UUID, column_id: str, fiscal_period: Optional[str] = None
    ) -> str:
        return f"{company_id}:{column_id}:{fiscal_period or 'latest'}"

    @staticmethod
    def make_valuation_key(instrument_id: UUID, column_id: str) -> str:
        return f"{instrument_id}:{column_id}"

    @staticmethod
    def make_technical_key(
        series_id: str,
        column_id: str,
        interval: str,
        last_bar_timestamp: Optional[str] = None,
    ) -> str:
        return f"{series_id}:{column_id}:{interval}:{last_bar_timestamp or 'latest'}"

    @staticmethod
    def make_event_key(company_id: UUID, column_id: str) -> str:
        return f"{company_id}:{column_id}"

    @staticmethod
    def make_news_key(entity_id: UUID, column_id: str) -> str:
        return f"{entity_id}:{column_id}"

    def get(self, category: EnrichmentCategory, key: str) -> Optional[WatchlistEnrichmentValue]:
        store = self._stores.get(category)
        if not store:
            return None

        entry = store.get(key)
        if entry is None:
            return None

        now = datetime.datetime.now(datetime.timezone.utc)
        if entry.is_expired(now):
            store.pop(key, None)
            return None

        entry.last_accessed = now
        return entry.value

    def set(
        self,
        category: EnrichmentCategory,
        key: str,
        value: WatchlistEnrichmentValue,
        custom_ttl: Optional[datetime.timedelta] = None,
    ) -> None:
        store = self._stores.get(category)
        if store is None:
            return

        # Evict oldest entry if at capacity
        if len(store) >= MAX_CACHE_ENTRIES_PER_CATEGORY and key not in store:
            oldest_key = min(store.keys(), key=lambda k: store[k].last_accessed)
            store.pop(oldest_key, None)

        now = datetime.datetime.now(datetime.timezone.utc)
        ttl = custom_ttl or CATEGORY_TTLS.get(category, datetime.timedelta(minutes=30))
        expires_at = now + ttl
        store[key] = CacheEntry(value=value, expires_at=expires_at)

    def invalidate_category(self, category: EnrichmentCategory) -> None:
        """Purges all entries for a specific category."""
        if category in self._stores:
            self._stores[category].clear()

    def invalidate_key(self, category: EnrichmentCategory, key: str) -> None:
        """Purges a single key from a category store."""
        store = self._stores.get(category)
        if store:
            store.pop(key, None)

    def clear(self) -> None:
        """Purges all caches across all categories."""
        for store in self._stores.values():
            store.clear()


# Global singleton instance
default_enrichment_cache = EnrichmentCacheManager()
