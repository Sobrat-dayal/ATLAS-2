"""Query Router and Execution Engine Dispatcher (Stage 131).

Routes incoming spatial analytics queries to precomputed materializations,
ClickHouse analytical rollups, or PostGIS spatial aggregation.
"""

from __future__ import annotations

from typing import Any, Dict, List

from atlas.maps.analytics.domain import SpatialAnalyticsQuery, SpatialAnalyticsResult
from atlas.maps.analytics.engines.postgis import PostGISSpatialAggregationEngine


class SpatialQueryRouter:
    """Intelligently routes analytical spatial queries based on dataset volume and index availability."""

    def __init__(self, postgis_engine: PostGISSpatialAggregationEngine):
        self.postgis_engine = postgis_engine

    def route_and_execute(
        self,
        query: SpatialAnalyticsQuery,
        features: List[Dict[str, Any]],
        dataset_version: str = "v1",
    ) -> SpatialAnalyticsResult:
        # Currently defaults to optimized in-process PostGIS spatial binning
        return self.postgis_engine.execute_query(
            query=query,
            features=features,
            dataset_version=dataset_version,
        )
