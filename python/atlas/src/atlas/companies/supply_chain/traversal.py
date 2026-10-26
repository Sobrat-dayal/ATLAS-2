"""Graph Traversal Engine for Multi-Tier Corporate Supply Networks (Stage 88)."""

from collections import deque
from typing import Dict, List, Set, Tuple

from .errors import SupplyChainTraversalLimitExceededError
from .models import SupplyChainRelationship


def traverse_supply_network(
    root_company_id: str,
    all_relationships: List[SupplyChainRelationship],
    direction: str = "BOTH",
    max_depth: int = 2,
    max_nodes: int = 150,
    max_edges: int = 300,
) -> Tuple[Dict[str, int], List[SupplyChainRelationship]]:
    """Traverses corporate supply network using bounded Breadth-First Search (BFS).

    Returns:
        Tuple of:
            - node_tiers: Dict[company_id, tier_depth]
            - collected_edges: List[SupplyChainRelationship]
    """
    if max_depth > 3:
        raise SupplyChainTraversalLimitExceededError(max_depth, 3)

    # Build adjacency maps:
    # Upstream: target (customer) -> list of edges where it is customer
    upstream_adj: Dict[str, List[SupplyChainRelationship]] = {}
    # Downstream: source (supplier) -> list of edges where it is supplier
    downstream_adj: Dict[str, List[SupplyChainRelationship]] = {}

    for rel in all_relationships:
        # Upstream adjacency (customer <- supplier)
        upstream_adj.setdefault(rel.customer_entity_id, []).append(rel)
        # Downstream adjacency (supplier -> customer)
        downstream_adj.setdefault(rel.supplier_entity_id, []).append(rel)

    # Queue stores: (current_company_id, current_tier, search_direction)
    queue = deque([(root_company_id, 0, direction)])

    # Visited tracking
    node_tiers: Dict[str, int] = {root_company_id: 0}
    collected_edges: List[SupplyChainRelationship] = []
    seen_edge_ids: Set[str] = set()

    while queue:
        current_id, current_tier, active_dir = queue.popleft()

        if current_tier >= max_depth:
            continue

        if len(node_tiers) >= max_nodes or len(collected_edges) >= max_edges:
            break

        # 1. Upstream Traversal (Find suppliers of current_id)
        if active_dir in ("UPSTREAM_SUPPLIER", "BOTH"):
            for edge in upstream_adj.get(current_id, []):
                supplier_id = edge.supplier_entity_id

                if edge.relationship_id not in seen_edge_ids:
                    seen_edge_ids.add(edge.relationship_id)
                    # Mark edge tier relative to root
                    edge_copy = edge
                    edge_copy.tier = current_tier + 1
                    collected_edges.append(edge_copy)

                if supplier_id not in node_tiers:
                    node_tiers[supplier_id] = current_tier + 1
                    if len(node_tiers) < max_nodes:
                        queue.append((supplier_id, current_tier + 1, "UPSTREAM_SUPPLIER"))

        # 2. Downstream Traversal (Find customers of current_id)
        if active_dir in ("DOWNSTREAM_CUSTOMER", "BOTH"):
            for edge in downstream_adj.get(current_id, []):
                customer_id = edge.customer_entity_id

                if edge.relationship_id not in seen_edge_ids:
                    seen_edge_ids.add(edge.relationship_id)
                    edge_copy = edge
                    edge_copy.tier = current_tier + 1
                    collected_edges.append(edge_copy)

                if customer_id not in node_tiers:
                    node_tiers[customer_id] = current_tier + 1
                    if len(node_tiers) < max_nodes:
                        queue.append((customer_id, current_tier + 1, "DOWNSTREAM_CUSTOMER"))

    return node_tiers, collected_edges
