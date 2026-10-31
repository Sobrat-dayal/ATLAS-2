"""Cache key generation and tenant-isolated caching for corporate geography (Stage 132)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Optional


def build_corporate_cache_key(
    prefix: str,
    company_id: str,
    scope: str,
    filters: dict[str, Any] | None = None,
    as_of: str | None = None,
    tenant_id: str | None = None,
) -> str:
    """Generate a collision-resistant, tenant-isolated cache key."""
    parts = {
        "company_id": company_id,
        "scope": scope,
        "filters": filters or {},
        "as_of": as_of or "latest",
        "tenant_id": tenant_id or "public",
    }
    serialized = json.dumps(parts, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
    return f"atlas:maps:corp:{prefix}:{company_id}:{digest}"

