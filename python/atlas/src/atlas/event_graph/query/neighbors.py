"""Direct Neighbor Retrieval (Stage 136).

Provides 1-hop bidirectional lookups:
- Event -> Linked Entities
- Entity -> Linked Events
With strict filtering by verification status, predicate, tenant, and as-of horizon.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from ..domain import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    GraphNodeType,
    PredicateType,
    RelationshipVerificationStatus,
)


def filter_relationship(
    rel: AtlasEventEntityRelationship,
    predicate: Optional[PredicateType] = None,
    min_verification: Optional[RelationshipVerificationStatus] = None,
    as_of: Optional[datetime] = None,
    tenant_id: Optional[str] = None,
) -> bool:
    """Evaluates whether a relationship passes filtering and entitlement checks."""
    # Multi-tenant isolation:
    # If relationship is tenant-specific, query must match tenant_id.
    # If relationship is global (tenant_id is None), accessible to all.
    if rel.tenant_id is not None and rel.tenant_id != tenant_id:
        return False

    # Check revocation
    if rel.is_revoked:
        return False

    # Filter by predicate
    if predicate is not None and rel.predicate != predicate:
        return False

    # Filter by minimum verification status
    if min_verification is not None:
        status_rank = {
            RelationshipVerificationStatus.VERIFIED_DIRECT: 4,
            RelationshipVerificationStatus.CORROBORATED: 3,
            RelationshipVerificationStatus.SOURCE_SUPPORTED: 2,
            RelationshipVerificationStatus.CANDIDATE: 1,
            RelationshipVerificationStatus.CONFLICTED: 0,
            RelationshipVerificationStatus.REJECTED: -1,
            RelationshipVerificationStatus.REVOKED: -2,
        }
        if status_rank.get(rel.verification_status, 0) < status_rank.get(min_verification, 0):
            return False

    # Point-in-time as-of check (Zero Look-Ahead Bias)
    if as_of is not None:
        # Knowledge horizon check
        if rel.knowledge_available_at > as_of:
            return False
        # Temporal validity window check
        if rel.temporal_valid_from and rel.temporal_valid_from > as_of:
            return False
        if rel.temporal_valid_to and rel.temporal_valid_to < as_of:
            return False

    return True


class NeighborQueryEngine:
    """Index and query engine for direct graph neighbor relations."""

    def __init__(self):
        # Index: event_id -> List[relationship_id]
        self._event_index: Dict[str, List[str]] = {}
        # Index: node_key -> List[relationship_id]
        self._target_node_index: Dict[str, List[str]] = {}
        # Index: node_key -> List[relationship_id] for source nodes (structural edges)
        self._source_node_index: Dict[str, List[str]] = {}

    def index_relationship(self, rel: AtlasEventEntityRelationship):
        """Indexes a relationship in forward and reverse lookup structures."""
        # Event index
        self._event_index.setdefault(rel.event_id, []).append(rel.relationship_id)
        # Target node index
        target_key = rel.target_node.node_key
        self._target_node_index.setdefault(target_key, []).append(rel.relationship_id)
        # Source node index
        source_key = rel.source_node.node_key
        self._source_node_index.setdefault(source_key, []).append(rel.relationship_id)

    def remove_relationship(self, rel: AtlasEventEntityRelationship):
        """Removes a relationship from indexing structures."""
        if rel.event_id in self._event_index and rel.relationship_id in self._event_index[rel.event_id]:
            self._event_index[rel.event_id].remove(rel.relationship_id)
        target_key = rel.target_node.node_key
        if target_key in self._target_node_index and rel.relationship_id in self._target_node_index[target_key]:
            self._target_node_index[target_key].remove(rel.relationship_id)
        source_key = rel.source_node.node_key
        if source_key in self._source_node_index and rel.relationship_id in self._source_node_index[source_key]:
            self._source_node_index[source_key].remove(rel.relationship_id)

    def get_event_neighbors(
        self,
        event_id: str,
        relationships: Dict[str, AtlasEventEntityRelationship],
        predicate: Optional[PredicateType] = None,
        min_verification: Optional[RelationshipVerificationStatus] = None,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns all valid relationships connected from this event."""
        rel_ids = self._event_index.get(event_id, [])
        results: List[AtlasEventEntityRelationship] = []
        for rid in rel_ids:
            rel = relationships.get(rid)
            if rel and filter_relationship(rel, predicate, min_verification, as_of, tenant_id):
                results.append(rel)
        return results

    def get_entity_events(
        self,
        node_type: GraphNodeType,
        entity_id: str,
        relationships: Dict[str, AtlasEventEntityRelationship],
        predicate: Optional[PredicateType] = None,
        min_verification: Optional[RelationshipVerificationStatus] = None,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns all valid event relationships where this entity is the target."""
        node_key = f"{node_type.value}:{entity_id}"
        rel_ids = self._target_node_index.get(node_key, [])
        results: List[AtlasEventEntityRelationship] = []
        for rid in rel_ids:
            rel = relationships.get(rid)
            if rel and filter_relationship(rel, predicate, min_verification, as_of, tenant_id):
                results.append(rel)
        return results

    def get_node_outgoing_edges(
        self,
        node_key: str,
        relationships: Dict[str, AtlasEventEntityRelationship],
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns outgoing edges from a specific node (structural entity-to-entity or event-to-entity)."""
        rel_ids = self._source_node_index.get(node_key, [])
        results: List[AtlasEventEntityRelationship] = []
        for rid in rel_ids:
            rel = relationships.get(rid)
            if rel and filter_relationship(rel, as_of=as_of, tenant_id=tenant_id):
                results.append(rel)
        return results

