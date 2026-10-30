"""Tenant-Isolated Cache for AI Research and Retrieval (Part LXXVIII)."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional, Tuple


class ResearchCache:
    """Tenant-isolated, time-bounded cache for passage searches and excerpts."""

    _store: Dict[str, Tuple[Any, float]] = {}

    @classmethod
    def _make_key(cls, tenant_id: str, namespace: str, payload: str) -> str:
        h = hashlib.sha256(payload.encode()).hexdigest()
        return f"{tenant_id}:{namespace}:{h}"

    @classmethod
    def get(cls, tenant_id: str, namespace: str, payload: str) -> Optional[Any]:
        key = cls._make_key(tenant_id, namespace, payload)
        item = cls._store.get(key)
        if not item:
            return None
        val, expires_at = item
        if time.time() > expires_at:
            del cls._store[key]
            return None
        return val

    @classmethod
    def set(
        cls,
        tenant_id: str,
        namespace: str,
        payload: str,
        value: Any,
        ttl_seconds: int = 300,
    ) -> None:
        key = cls._make_key(tenant_id, namespace, payload)
        cls._store[key] = (value, time.time() + ttl_seconds)

    @classmethod
    def invalidate_tenant(cls, tenant_id: str) -> None:
        prefix = f"{tenant_id}:"
        keys_to_del = [k for k in cls._store.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            del cls._store[k]
