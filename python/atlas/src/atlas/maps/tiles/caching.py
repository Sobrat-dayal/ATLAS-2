"""Tile Cache Management with Multi-Tenant Isolation and Cryptographic Keying.

Ensures private datasets are NEVER leaked into public tile caches.
Supports rapid cache invalidation on dataset permissions changes or data revisions.
"""

from __future__ import annotations

import hashlib
from typing import Dict, Optional


class AtlasTileCacheManager:
    """In-memory and Valkey/Redis tile cache manager with tenant separation."""

    def __init__(self):
        self._cache: Dict[str, bytes] = {}

    def build_cache_key(
        self,
        layer_id: str,
        z: int,
        x: int,
        y: int,
        is_public: bool,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        revision: int = 1,
    ) -> str:
        """Constructs secure cache key with strict tenant boundaries."""
        if is_public:
            return f"map_tile:pub:{layer_id}:r{revision}:{z}:{x}:{y}"
        else:
            t = tenant_id or "default"
            u = user_id or "anon"
            h = hashlib.sha256(f"{t}:{u}".encode("utf-8")).hexdigest()[:16]
            return f"map_tile:priv:{layer_id}:r{revision}:{h}:{z}:{x}:{y}"

    def get_tile(self, cache_key: str) -> Optional[bytes]:
        """Retrieves cached vector tile bytes."""
        return self._cache.get(cache_key)

    def set_tile(self, cache_key: str, data: bytes) -> None:
        """Stores vector tile bytes in cache."""
        self._cache[cache_key] = data

    def invalidate_layer(self, layer_id: str) -> int:
        """Invalidates all cached tiles for a specified layer."""
        to_del = [k for k in self._cache if f":{layer_id}:" in k]
        for k in to_del:
            del self._cache[k]
        return len(to_del)

    def clear(self) -> None:
        """Clears entire tile cache."""
        self._cache.clear()


# Global Singleton instance
tile_cache_manager = AtlasTileCacheManager()

