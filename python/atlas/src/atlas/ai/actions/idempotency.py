"""Idempotency management for effectful AI financial actions (Stage 128, Part XX, LXXXVI)."""

from __future__ import annotations

import copy
from typing import Any, Dict, Optional


class AtlasActionIdempotencyManager:
    """Stores execution results by client idempotency key to prevent duplicate execution (Fixture G)."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get_cached_response(self, idempotency_key: str) -> Optional[Dict[str, Any]]:
        res = self._cache.get(idempotency_key)
        return copy.deepcopy(res) if res else None

    def record_response(self, idempotency_key: str, response_payload: Dict[str, Any]) -> None:
        self._cache[idempotency_key] = copy.deepcopy(response_payload)


_IDEMPOTENCY_MANAGER = AtlasActionIdempotencyManager()


def get_idempotency_manager() -> AtlasActionIdempotencyManager:
    return _IDEMPOTENCY_MANAGER

