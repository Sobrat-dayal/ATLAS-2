"""Corporate relationship graph traversal with bounded depth and cycle protection (Stage 132)."""

from __future__ import annotations

import datetime
from typing import Any

from atlas.maps.corporate.errors import CycleDetectedInCorporateGraphError


def is_edge_valid_as_of(edge: dict[str, Any], as_of: datetime.datetime | None) -> bool:
    """Check if a temporal corporate relationship edge is valid as of the specified datetime."""
    if as_of is None:
        return bool(edge.get("is_current", True))

    valid_from = edge.get("valid_from")
    valid_to = edge.get("valid_to")

    if isinstance(valid_from, str):
        try:
            valid_from = datetime.datetime.fromisoformat(valid_from.replace("Z", "+00:00"))
        except ValueError:
            valid_from = None
    elif isinstance(valid_from, datetime.date) and not isinstance(valid_from, datetime.datetime):
        valid_from = datetime.datetime.combine(valid_from, datetime.time.min, tzinfo=datetime.timezone.utc)

    if isinstance(valid_to, str):
        try:
            valid_to = datetime.datetime.fromisoformat(valid_to.replace("Z", "+00:00"))
        except ValueError:
            valid_to = None
    elif isinstance(valid_to, datetime.date) and not isinstance(valid_to, datetime.datetime):
        valid_to = datetime.datetime.combine(valid_to, datetime.time.max, tzinfo=datetime.timezone.utc)

    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=datetime.timezone.utc)
    if valid_from and valid_from.tzinfo is None:
        valid_from = valid_from.replace(tzinfo=datetime.timezone.utc)
    if valid_to and valid_to.tzinfo is None:
        valid_to = valid_to.replace(tzinfo=datetime.timezone.utc)

    if valid_from and valid_from > as_of:
        return False
    if valid_to and valid_to < as_of:
        return False

    return True


def traverse_subsidiaries(
    root_entity_id: str,
    edges: list[dict[str, Any]],
    max_depth: int = 4,
    as_of: datetime.datetime | None = None,
    raise_on_cycle: bool = True,
) -> set[str]:
    """Traverse corporate hierarchy to discover verified subsidiaries belonging to root entity.

    Guarantees:
    - Bounded execution depth (default max 4 tiers).
    - Temporal validity filtering without look-ahead bias.
    - Explicit cycle detection to prevent infinite recursion on malformed corporate graphs.
    """
    subsidiary_ids: set[str] = {root_entity_id}
    parent_to_children: dict[str, list[str]] = {}

    for edge in edges:
        rel_type = edge.get("relationship_type_key") or edge.get("relationship_type")
        source = edge.get("source_entity_id")
        target = edge.get("target_entity_id")

        if not source or not target:
            continue

        if not is_edge_valid_as_of(edge, as_of):
            continue

        # Treat PARENT_OF as source -> target, SUBSIDIARY_OF as target -> source
        if rel_type in ("PARENT_OF", "CONTROLS"):
            parent_to_children.setdefault(source, []).append(target)
        elif rel_type in ("SUBSIDIARY_OF", "CONTROLLED_BY"):
            parent_to_children.setdefault(target, []).append(source)

    def dfs(current_id: str, depth: int, path: list[str]) -> None:
        if depth >= max_depth:
            return

        children = parent_to_children.get(current_id, [])
        for child in children:
            if child in path:
                if raise_on_cycle:
                    raise CycleDetectedInCorporateGraphError(path + [child])
                continue

            subsidiary_ids.add(child)
            dfs(child, depth + 1, path + [child])

    dfs(root_entity_id, 0, [root_entity_id])
    return subsidiary_ids

