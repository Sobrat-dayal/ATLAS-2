"""Fund Look-Through Traversal & Cycle Detection (Stage 137).

Enforces institutional look-through invariants:
- Computes indirect holding allocations via compounding weights along verified holding edges:
  e.g., Portfolio holds 20% in Fund F, Fund F holds 30% in Company C => 6% indirect weight.
- Strict cycle detection: halts immediately upon detecting a cyclical holding chain (CycleDetectedError)
  preventing infinite loops or fabricated multi-pass allocations.
- Bounded depth limits.
"""

from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple
from atlas.exposure.errors import CycleDetectedError


class FundConstituentEdge:
    def __init__(self, parent_fund_id: str, child_entity_id: str, weight: Decimal, child_is_fund: bool = False):
        self.parent_fund_id = parent_fund_id
        self.child_entity_id = child_entity_id
        self.weight = weight  # Decimal 0.0 - 1.0 (or percentage / 100)
        self.child_is_fund = child_is_fund


def calculate_fund_lookthrough(
    start_entity_id: str,
    target_entity_id: str,
    fund_holdings: Dict[str, List[FundConstituentEdge]],
    max_depth: int = 5
) -> Tuple[Decimal, List[str]]:
    """Traverse fund constituent holdings to compute effective indirect weight.
    
    Returns:
        Tuple[effective_weight, path_traversed]
        
    Raises:
        CycleDetectedError: If a cycle in fund holdings is encountered.
    """
    total_effective_weight = Decimal("0.0")
    found_paths: List[List[str]] = []

    def dfs(current_id: str, current_weight: Decimal, visited_path: List[str], depth: int):
        nonlocal total_effective_weight
        if depth > max_depth:
            return

        if current_id in visited_path:
            cycle = visited_path + [current_id]
            raise CycleDetectedError(cycle_path=cycle)

        new_path = visited_path + [current_id]

        edges = fund_holdings.get(current_id, [])
        for edge in edges:
            compounded = current_weight * edge.weight
            if edge.child_entity_id == target_entity_id:
                total_effective_weight += compounded
                found_paths.append(new_path + [target_entity_id])
            elif edge.child_is_fund:
                dfs(edge.child_entity_id, compounded, new_path, depth + 1)

    dfs(start_entity_id, Decimal("1.0"), [], 0)
    primary_path = found_paths[0] if found_paths else [start_entity_id]
    return total_effective_weight, primary_path
