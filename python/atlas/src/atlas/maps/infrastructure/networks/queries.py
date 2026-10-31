"""Bounded Network Query Engine with Strict Traversal Limits (Stage 133)."""

from __future__ import annotations

from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple

from atlas.maps.infrastructure.domain import (
    ConnectivityClass,
    InfrastructureNetwork,
    NetworkEdge,
    NetworkNode,
)
from atlas.maps.infrastructure.errors import (
    CycleDetectedInNetworkError,
    InvalidTopologyError,
    TraversalDepthExceededError,
)


class BoundedNetworkQueryEngine:
    """Bounded graph query engine for infrastructure network topology."""

    def __init__(self, network: InfrastructureNetwork, max_depth: int = 5) -> None:
        self.network = network
        self.max_depth = max_depth
        self._nodes_by_id: Dict[str, NetworkNode] = {n.node_id: n for n in network.nodes}
        self._adj_list: Dict[str, List[Tuple[str, NetworkEdge]]] = {n.node_id: [] for n in network.nodes}

        for edge in network.edges:
            if edge.from_node_id not in self._nodes_by_id or edge.to_node_id not in self._nodes_by_id:
                raise InvalidTopologyError(
                    f"Edge '{edge.edge_id}' connects invalid nodes '{edge.from_node_id}' -> '{edge.to_node_id}'"
                )
            self._adj_list[edge.from_node_id].append((edge.to_node_id, edge))
            if edge.bidirectional:
                self._adj_list[edge.to_node_id].append((edge.from_node_id, edge))

    def get_reachable_subgraph(
        self,
        start_node_id: str,
        max_hops: Optional[int] = None,
        only_verified: bool = True,
    ) -> Dict[str, Any]:
        """Traverse connected nodes within strictly bounded depth, protecting against cycles."""
        effective_max_depth = min(max_hops or self.max_depth, self.max_depth)
        if (max_hops or 0) > self.max_depth:
            raise TraversalDepthExceededError(max_hops, self.max_depth)

        if start_node_id not in self._nodes_by_id:
            return {"nodes": [], "edges": [], "depth_reached": 0}

        visited_nodes: Set[str] = {start_node_id}
        visited_edge_ids: Set[str] = set()
        result_edges: List[NetworkEdge] = []

        # Queue contains (node_id, current_depth)
        queue: deque[Tuple[str, int]] = deque([(start_node_id, 0)])
        max_depth_reached = 0

        while queue:
            current_id, depth = queue.popleft()
            max_depth_reached = max(max_depth_reached, depth)

            if depth >= effective_max_depth:
                continue

            for neighbor_id, edge in self._adj_list.get(current_id, []):
                if only_verified and edge.connectivity_evidence != ConnectivityClass.VERIFIED:
                    continue

                if edge.edge_id not in visited_edge_ids:
                    visited_edge_ids.add(edge.edge_id)
                    result_edges.append(edge)

                if neighbor_id not in visited_nodes:
                    visited_nodes.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))

        return {
            "start_node_id": start_node_id,
            "depth_reached": max_depth_reached,
            "max_authorized_depth": effective_max_depth,
            "node_count": len(visited_nodes),
            "edge_count": len(result_edges),
            "nodes": [self._nodes_by_id[nid] for nid in visited_nodes],
            "edges": result_edges,
        }

    def find_shortest_path(
        self,
        start_node_id: str,
        target_node_id: str,
        only_verified: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Find verified path between two nodes using BFS, respecting depth bounds."""
        if start_node_id not in self._nodes_by_id or target_node_id not in self._nodes_by_id:
            return None

        if start_node_id == target_node_id:
            return {
                "path_node_ids": [start_node_id],
                "path_edges": [],
                "total_length_km": 0.0,
                "hop_count": 0,
            }

        queue: deque[Tuple[str, List[str], List[NetworkEdge], float]] = deque(
            [(start_node_id, [start_node_id], [], 0.0)]
        )
        visited: Set[str] = {start_node_id}

        while queue:
            current_id, path_nodes, path_edges, total_km = queue.popleft()

            if len(path_edges) >= self.max_depth:
                continue

            for neighbor_id, edge in self._adj_list.get(current_id, []):
                if only_verified and edge.connectivity_evidence != ConnectivityClass.VERIFIED:
                    continue

                if neighbor_id == target_node_id:
                    new_path_edges = path_edges + [edge]
                    new_km = total_km + (edge.length_km or 0.0)
                    return {
                        "path_node_ids": path_nodes + [neighbor_id],
                        "path_edges": new_path_edges,
                        "total_length_km": new_km,
                        "hop_count": len(new_path_edges),
                    }

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append(
                        (
                            neighbor_id,
                            path_nodes + [neighbor_id],
                            path_edges + [edge],
                            total_km + (edge.length_km or 0.0),
                        )
                    )

        return None
