"""Verified Network Topology Rules and Crossing Validation (Stage 133)."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from atlas.maps.infrastructure.domain import (
    ConnectivityClass,
    NetworkEdge,
    NetworkNode,
)
from atlas.maps.infrastructure.errors import InvalidTopologyError


def validate_network_topology(nodes: List[NetworkNode], edges: List[NetworkEdge]) -> None:
    """Validate that all edge endpoints refer to existing nodes in the network."""
    node_ids: Set[str] = {node.node_id for node in nodes}

    for edge in edges:
        if edge.from_node_id not in node_ids:
            raise InvalidTopologyError(
                f"Edge '{edge.edge_id}' references non-existent source node '{edge.from_node_id}'."
            )
        if edge.to_node_id not in node_ids:
            raise InvalidTopologyError(
                f"Edge '{edge.edge_id}' references non-existent target node '{edge.to_node_id}'."
            )


def verify_crossing_separation(
    edge_a: NetworkEdge,
    edge_b: NetworkEdge,
    explicit_junction_nodes: List[NetworkNode],
) -> bool:
    """Enforce geometric crossing separation invariant (Fixtures C & D).

    Crossing lines (e.g. pipelines crossing, rail overpass on a bridge) do NOT
    establish a connection unless an explicit physical junction node exists at that location.

    Returns:
        True if edges are legitimately connected via a shared junction node.
        False if they are crossing lines without physical connectivity.
    """
    junction_ids = {node.node_id for node in explicit_junction_nodes}

    shared_endpoints = {edge_a.from_node_id, edge_a.to_node_id}.intersection(
        {edge_b.from_node_id, edge_b.to_node_id}
    )

    if not shared_endpoints:
        # No shared endpoints -> geometrically crossing but topologically disconnected
        return False

    # Check if the shared endpoint is an explicit junction
    for endpoint in shared_endpoints:
        if endpoint in junction_ids:
            return True

    return False
