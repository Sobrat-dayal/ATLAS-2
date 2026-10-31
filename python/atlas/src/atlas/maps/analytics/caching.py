"""Permission-Aware Cache Key Derivation and Invalidation (Stage 131).

Ensures multi-tenant cache isolation by salting cache keys with tenant and user IDs
for proprietary datasets, preventing cross-tenant aggregate cache poisoning.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from atlas.maps.analytics.domain import SpatialAnalyticsQuery


def generate_spatial_analytics_cache_key(
    query: SpatialAnalyticsQuery,
    dataset_version: str = "v1",
    is_public_dataset: bool = True,
) -> str:
    """Generates a deterministic, collision-resistant, permission-aware cache key.

    For private/tenant datasets, the key includes tenant_id and user_id to prevent
    unauthorized cross-tenant cache leakage (Fixture K).
    """
    key_dict: Dict[str, Any] = {
        "dataset_id": query.dataset_id,
        "dataset_version": dataset_version,
        "metric_id": query.metric_id,
        "aggregation": query.aggregation.value,
        "h3_resolution": query.h3_resolution,
        "visualization_type": query.visualization_type.value,
        "bounds": query.bounds.to_list() if query.bounds else None,
        "filters": query.filters,
        "time_start": query.time_range_start.isoformat() if query.time_range_start else None,
        "time_end": query.time_range_end.isoformat() if query.time_range_end else None,
        "time_bucket": query.time_bucket.value if query.time_bucket else None,
        "as_of": query.historical_as_of.isoformat() if query.historical_as_of else None,
    }

    if not is_public_dataset:
        key_dict["tenant_id"] = query.tenant_id or "default"
        key_dict["user_id"] = query.user_id or "anon"

    serialized = json.dumps(key_dict, sort_keys=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:24]

    tenant_scope = query.tenant_id if not is_public_dataset and query.tenant_id else "global"
    return f"atlas:maps:analytics:{tenant_scope}:{query.dataset_id}:{query.h3_resolution}:{digest}"
