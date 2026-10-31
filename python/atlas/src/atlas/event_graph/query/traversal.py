"""Bounded Multi-Hop Graph Traversal Engine (Stage 136).

Performs bounded path discovery and neighborhood extraction with:
- Strict maximum traversal depth enforcement (default max 5).
- Guaranteed cycle detection and avoidance.
- Tenant boundary enforcement.
- Bitemporal point-in-time filtering.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set

from ..domain import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    GraphPath,
    GraphPathHop,
    PredicateType,
    RelationshipVerificationStatus,
)
from ..errors import GraphCycleDetectedError, TraversalDepthExceededError
from .neighbors import NeighborQueryEngine, filter_relationship


class BoundedGraphTraversalEngine:
    """Institutional traversal engine over the knowledge graph."""

    def __init__(self, neighbor_engine: NeighborQueryEngine):
        self.neighbor_engine = neighbor_engine

    def find_paths(
        self,
        start_node: CanonicalGraphNodeRef,
        end_node: CanonicalGraphNodeRef,
        relationships: Dict[str, AtlasEventEntityRelationship],
        max_depth: int = 3,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[GraphPath]:
        """Finds all verified acyclic paths between start_node and end_node up to max_depth."""
        if max_depth > 5:
            raise TraversalDepthExceededError(requested_depth=max_depth, max_allowed=5)

        start_key = start_node.node_key
        end_key = end_node.node_key

        discovered_paths: List[GraphPath] = []
        # DFS with path tracking: (current_node, current_hops, visited_node_keys)
        stack: List[tuple[CanonicalGraphNodeRef, List[GraphPathHop], Set[str]]] = [
            (start_node, [], {start_key})
        ]

        while stack:
            current_node, hops, visited = stack.pop()

            if current_node.node_key == end_key and hops:
                # Discovered a valid path to end_node
                explanation_lines = [
                    f"Step {h.hop_number}: {h.from_node.canonical_name} --[{h.predicate.value}]--> {h.to_node.canonical_name}"
                    for h in hops
                ]
                factual_explanation = " -> ".join(
                    [hops[0].from_node.canonical_name] + [f"[{h.predicate.value}] {h.to_node.canonical_name}" for h in hops]
                ) + f" (Verified via {sum(len(h.evidence_ids) for h in hops)} evidence records)"

                discovered_paths.append(
                    GraphPath(
                        path_id=f"path-{uuid.uuid4().hex[:10]}",
                        source_node=start_node,
                        target_node=end_node,
                        hops=hops,
                        total_hops=len(hops),
                        factual_explanation=factual_explanation,
                    )
                )
                continue

            if len(hops) >= max_depth:
                continue

            # Look up outgoing edges from current node
            outgoing = self.neighbor_engine.get_node_outgoing_edges(
                current_node.node_key,
                relationships,
                as_of=as_of,
                tenant_id=tenant_id,
            )

            for rel in outgoing:
                next_node = rel.target_node
                next_key = next_node.node_key

                # Cycle avoidance: do not revisit any node already in active path
                if next_key in visited:
                    continue

                new_hop = GraphPathHop(
                    hop_number=len(hops) + 1,
                    from_node=current_node,
                    to_node=next_node,
                    predicate=rel.predicate,
                    relationship_id=rel.relationship_id,
                    verification_status=rel.verification_status,
                    evidence_ids=rel.evidence_ids,
                    temporal_valid_from=rel.temporal_valid_from,
                    temporal_valid_to=rel.temporal_valid_to,
                    explanation=(
                        f"{current_node.canonical_name} is linked to {next_node.canonical_name} "
                        f"via {rel.predicate.value}"
                        + (f" in role {rel.relationship_role}" if rel.relationship_role else "")
                        + f" [{rel.verification_status.value}]."
                    ),
                )

                new_visited = set(visited)
                new_visited.add(next_key)
                stack.append((next_node, hops + [new_hop], new_visited))

        return discovered_paths

    def extract_neighborhood(
        self,
        center_node: CanonicalGraphNodeRef,
        relationships: Dict[str, AtlasEventEntityRelationship],
        depth: int = 1,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extracts the k-hop neighborhood subgraph surrounding center_node."""
        if depth > 3:
            raise TraversalDepthExceededError(requested_depth=depth, max_allowed=3)

        visited_nodes: Dict[str, CanonicalGraphNodeRef] = {center_node.node_key: center_node}
        collected_relationships: Dict[str, AtlasEventEntityRelationship] = {}

        current_frontier = [center_node.node_key]

        for current_depth in range(depth):
            next_frontier = []
            for node_key in current_frontier:
                # Outgoing edges
                outgoing = self.neighbor_engine.get_node_outgoing_edges(
                    node_key,
                    relationships,
                    as_of=as_of,
                    tenant_id=tenant_id,
                )
                for rel in outgoing:
                    collected_relationships[rel.relationship_id] = rel
                    t_key = rel.target_node.node_key
                    if t_key not in visited_nodes:
                        visited_nodes[t_key] = rel.target_node
                        next_frontier.append(t_key)

            current_frontier = next_frontier
            if not current_frontier:
                break

        return {
            "center_node": center_node,
            "depth": depth,
            "nodes": list(visited_nodes.values()),
            "relationships": list(collected_relationships.values()),
            "total_nodes": len(visited_nodes),
            "total_relationships": len(collected_relationships),
        }

