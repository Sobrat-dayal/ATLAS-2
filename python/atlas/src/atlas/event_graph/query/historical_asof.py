"""Bitemporal Point-in-Time Graph Evaluation (Stage 136).

Evaluates knowledge graph topology as-of any historical timestamp with zero look-ahead bias.
Enforces knowledge availability horizons (system time) alongside real-world validity (valid time).
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from ..domain import AtlasEventEntityRelationship
from .neighbors import filter_relationship


class HistoricalAsOfEvaluator:
    """Evaluates knowledge graph state at a specified historical timestamp."""

    @staticmethod
    def filter_relationships_as_of(
        relationships: Dict[str, AtlasEventEntityRelationship],
        as_of_time: datetime,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Filters relationships so that only edges known and valid at as_of_time are included."""
        valid_edges: List[AtlasEventEntityRelationship] = []
        for rel in relationships.values():
            if filter_relationship(rel, as_of=as_of_time, tenant_id=tenant_id):
                valid_edges.append(rel)
        return valid_edges

