"""
Layout Engine Schema Parser, Validator, and Recovery Utilities (Stage 120).
"""

import math
import uuid
from typing import Any, Optional, Set

from atlas.workspaces.enums import LayoutNodeType, SplitOrientation
from atlas.workspaces.errors import (
    WorkspaceLayoutCycleError,
    WorkspaceLayoutDepthExceededError,
    WorkspaceLayoutPanelDuplicateError,
    WorkspaceLayoutSchemaInvalidError,
    WorkspaceLayoutSizeInvalidError,
)
from atlas.workspaces.models import (
    LayoutNode,
    PanelNode,
    SplitNode,
    TabStackNode,
)

MAX_LAYOUT_DEPTH = 8
MAX_PANEL_COUNT = 24


def parse_layout_node(data: dict[str, Any]) -> LayoutNode:
    """Parses a dictionary into a typed LayoutNode."""
    if not isinstance(data, dict):
        raise WorkspaceLayoutSchemaInvalidError("Node must be a JSON dictionary.")

    node_type_str = data.get("node_type")
    node_id = data.get("node_id") or str(uuid.uuid4())

    if node_type_str == LayoutNodeType.SPLIT.value:
        orientation_str = data.get("orientation", SplitOrientation.HORIZONTAL.value)
        try:
            orientation = SplitOrientation(orientation_str)
        except ValueError:
            orientation = SplitOrientation.HORIZONTAL

        children_raw = data.get("children", [])
        if not isinstance(children_raw, list):
            raise WorkspaceLayoutSchemaInvalidError(
                f"SplitNode '{node_id}' children must be a list."
            )

        children = [parse_layout_node(c) for c in children_raw]
        size_ratios = data.get("size_ratios", [])
        if not isinstance(size_ratios, list):
            raise WorkspaceLayoutSchemaInvalidError(
                f"SplitNode '{node_id}' size_ratios must be a list of floats."
            )

        return SplitNode(
            node_id=node_id,
            orientation=orientation,
            children=children,
            size_ratios=[float(r) for r in size_ratios],
            min_size_rules=data.get("min_size_rules", {}),
        )

    elif node_type_str == LayoutNodeType.TAB_STACK.value:
        panel_instance_ids = data.get("panel_instance_ids", [])
        if not isinstance(panel_instance_ids, list):
            raise WorkspaceLayoutSchemaInvalidError(
                f"TabStackNode '{node_id}' panel_instance_ids must be a list."
            )

        active_id = data.get("active_panel_instance_id") or (
            panel_instance_ids[0] if panel_instance_ids else ""
        )
        return TabStackNode(
            node_id=node_id,
            panel_instance_ids=[str(p) for p in panel_instance_ids],
            active_panel_instance_id=str(active_id),
        )

    elif node_type_str == LayoutNodeType.PANEL.value:
        panel_instance_id = data.get("panel_instance_id", "")
        return PanelNode(
            node_id=node_id,
            panel_instance_id=str(panel_instance_id),
        )

    else:
        raise WorkspaceLayoutSchemaInvalidError(
            f"Unrecognized layout node_type '{node_type_str}' on node '{node_id}'."
        )


def validate_layout_tree(
    root: LayoutNode, allowed_panel_ids: Optional[Set[str]] = None
) -> list[str]:
    """
    Validates all architectural invariants of the layout tree.
    Returns the ordered list of all active panel_instance_ids found in the tree.
    Raises domain exceptions if any invariant is violated.
    """
    seen_node_ids: set[str] = set()
    seen_panel_ids: set[str] = set()
    panel_order: list[str] = []

    def _traverse(node: LayoutNode, depth: int, ancestor_nodes: set[str]):
        if depth > MAX_LAYOUT_DEPTH:
            raise WorkspaceLayoutDepthExceededError(depth, MAX_LAYOUT_DEPTH)

        if node.node_id in ancestor_nodes:
            raise WorkspaceLayoutCycleError(node.node_id)

        if node.node_id in seen_node_ids:
            raise WorkspaceLayoutSchemaInvalidError(
                f"Duplicate node_id '{node.node_id}' found in layout tree."
            )
        seen_node_ids.add(node.node_id)

        current_ancestors = ancestor_nodes | {node.node_id}

        if isinstance(node, SplitNode):
            if len(node.children) < 2:
                raise WorkspaceLayoutSchemaInvalidError(
                    f"SplitNode '{node.node_id}' must have at least 2 children, found {len(node.children)}."
                )

            if len(node.children) != len(node.size_ratios):
                # Auto-initialize balanced ratios if missing or mismatched
                node.size_ratios = [1.0 / len(node.children)] * len(node.children)

            # Validate ratios
            total_ratio = 0.0
            for r in node.size_ratios:
                if math.isnan(r) or math.isinf(r) or r <= 0.0:
                    raise WorkspaceLayoutSizeInvalidError(
                        f"SplitNode '{node.node_id}' has invalid ratio {r}. Ratios must be finite positive numbers."
                    )
                total_ratio += r

            if abs(total_ratio - 1.0) > 1e-4:
                # Normalize ratios
                node.size_ratios = [r / total_ratio for r in node.size_ratios]

            for child in node.children:
                _traverse(child, depth + 1, current_ancestors)

        elif isinstance(node, TabStackNode):
            if not node.panel_instance_ids:
                raise WorkspaceLayoutSchemaInvalidError(
                    f"TabStackNode '{node.node_id}' must contain at least 1 panel."
                )

            for pid in node.panel_instance_ids:
                if not pid:
                    continue
                if pid in seen_panel_ids:
                    raise WorkspaceLayoutPanelDuplicateError(pid)
                seen_panel_ids.add(pid)
                panel_order.append(pid)

            if node.active_panel_instance_id not in node.panel_instance_ids:
                node.active_panel_instance_id = node.panel_instance_ids[0]

        elif isinstance(node, PanelNode):
            pid = node.panel_instance_id
            if not pid:
                raise WorkspaceLayoutSchemaInvalidError(
                    f"PanelNode '{node.node_id}' missing panel_instance_id."
                )
            if pid in seen_panel_ids:
                raise WorkspaceLayoutPanelDuplicateError(pid)
            seen_panel_ids.add(pid)
            panel_order.append(pid)

    _traverse(root, 1, set())

    if len(seen_panel_ids) > MAX_PANEL_COUNT:
        raise WorkspaceLayoutSchemaInvalidError(
            f"Layout panel count {len(seen_panel_ids)} exceeds maximum allowable limit of {MAX_PANEL_COUNT}."
        )

    if allowed_panel_ids is not None:
        orphans = seen_panel_ids - allowed_panel_ids
        if orphans:
            raise WorkspaceLayoutSchemaInvalidError(
                f"Panels {orphans} in layout do not exist in workspace panel instances."
            )

    return panel_order


def create_safe_recovery_layout(panel_instance_ids: list[str]) -> LayoutNode:
    """
    Creates a resilient, clean fallback layout containing the given panel instances.
    If 0 panels: single empty panel placeholder node.
    If 1 panel: PanelNode.
    If 2-4 panels: Horizontal split.
    If > 4 panels: TabStackNode.
    """
    if not panel_instance_ids:
        return PanelNode(node_id="panel_empty", panel_instance_id="placeholder")

    if len(panel_instance_ids) == 1:
        return PanelNode(
            node_id=f"node_{uuid.uuid4().hex[:8]}", panel_instance_id=panel_instance_ids[0]
        )

    if len(panel_instance_ids) <= 4:
        count = len(panel_instance_ids)
        children = [
            PanelNode(node_id=f"node_{uuid.uuid4().hex[:8]}", panel_instance_id=pid)
            for pid in panel_instance_ids
        ]
        return SplitNode(
            node_id=f"split_{uuid.uuid4().hex[:8]}",
            orientation=SplitOrientation.HORIZONTAL,
            children=children,
            size_ratios=[1.0 / count] * count,
        )

    # For larger collections, use a tab stack to prevent microscopic columns
    return TabStackNode(
        node_id=f"tabs_{uuid.uuid4().hex[:8]}",
        panel_instance_ids=list(panel_instance_ids),
        active_panel_instance_id=panel_instance_ids[0],
    )
