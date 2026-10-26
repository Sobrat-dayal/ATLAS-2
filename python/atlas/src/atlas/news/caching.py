"""Cache Management and Revision-Aware Invalidation for News (Stage 99)."""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple


class NewsFeedCache:
    """
    In-memory feed cache with TTL, revision invalidation, and entitlement isolation.
    """

    def __init__(self, default_ttl_seconds: int = 120):
        self._default_ttl = default_ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._revision_epoch: int = int(time.time())

    def generate_cache_key(self, query_dict: dict, entitlement_scope: str = "standard") -> str:
        """Computes a deterministic hash of feed parameters and entitlement tier."""
        serialized = json.dumps(query_dict, sort_keys=True, default=str)
        raw = f"{self._revision_epoch}:{entitlement_scope}:{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        expires_at, data = self._store[key]
        if time.time() > expires_at:
            del self._store[key]
            return None
        return data

    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        duration = ttl if ttl is not None else self._default_ttl
        self._store[key] = (time.time() + duration, data)

    def invalidate_all(self) -> None:
        """Invalidates all cached feeds by bumping the revision epoch."""
        self._revision_epoch = int(time.time() * 1000)
        self._store.clear()


# Global singleton cache instance for the News module
default_news_cache = NewsFeedCache(default_ttl_seconds=180)
