"""Pure graph validation and deterministic workflow compilation."""

from __future__ import annotations

from dataclasses import dataclass

from atlas.ai.providers.registry import get_model_capability
from atlas.ai.tools.registry import AtlasAiToolRegistry
from atlas.workflows.domain import WorkflowGraph, WorkflowNodeType, WorkflowPortType
from atlas.workflows.errors import WorkflowValidationError

MAX_WORKFLOW_NODES = 100


@dataclass(frozen=True, slots=True)
class CompiledWorkflow:
    execution_order: tuple[str, ...]
    node_count: int
    edge_count: int


def validate_and_compile(graph: WorkflowGraph) -> CompiledWorkflow:
    errors: list[str] = []
    if not graph.nodes:
        errors.append("Workflow must contain at least one node.")
    if len(graph.nodes) > MAX_WORKFLOW_NODES:
        errors.append(f"Workflow cannot contain more than {MAX_WORKFLOW_NODES} nodes.")

    node_ids = [node.node_id for node in graph.nodes]
    node_map = {node.node_id: node for node in graph.nodes}
    if len(node_map) != len(node_ids):
        errors.append("Node IDs must be unique.")

    triggers = [node for node in graph.nodes if node.node_type is WorkflowNodeType.MANUAL_TRIGGER]
    returns = [node for node in graph.nodes if node.node_type is WorkflowNodeType.RETURN]
    if len(triggers) != 1:
        errors.append("Workflow must contain exactly one MANUAL_TRIGGER node.")
    if not returns:
        errors.append("Workflow must contain at least one RETURN node.")

    edge_ids = [edge.edge_id for edge in graph.edges]
    if len(set(edge_ids)) != len(edge_ids):
        errors.append("Edge IDs must be unique.")

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_map}
    incoming: dict[str, int] = {node_id: 0 for node_id in node_map}
    for edge in graph.edges:
        source = node_map.get(edge.source_node_id)
        target = node_map.get(edge.target_node_id)
        if source is None or target is None:
            errors.append(f"Edge '{edge.edge_id}' references an unknown node.")
            continue
        if edge.source_node_id == edge.target_node_id:
            errors.append(f"Edge '{edge.edge_id}' cannot connect a node to itself.")
            continue
        if not _types_compatible(edge.source_type, edge.target_type):
            errors.append(f"Edge '{edge.edge_id}' connects incompatible port types.")
        adjacency[edge.source_node_id].append(edge.target_node_id)
        incoming[edge.target_node_id] += 1

    for node in graph.nodes:
        if node.node_type is WorkflowNodeType.AI_AGENT:
            model_id = node.config.get("model_id")
            if not isinstance(model_id, str):
                errors.append(f"AI node '{node.node_id}' requires model_id.")
            else:
                try:
                    get_model_capability(model_id)
                except Exception:
                    errors.append(f"AI node '{node.node_id}' references an ineligible model.")
        if node.node_type is WorkflowNodeType.ATLAS_TOOL:
            tool_id = node.config.get("tool_id")
            if not isinstance(tool_id, str) or not AtlasAiToolRegistry.get_instance().is_registered(tool_id):
                errors.append(f"Tool node '{node.node_id}' references an unregistered tool.")

    if errors:
        raise WorkflowValidationError(errors)

    reachable = _reachable(triggers[0].node_id, adjacency)
    missing = sorted(set(node_map) - reachable)
    if missing:
        raise WorkflowValidationError([f"Unreachable nodes: {', '.join(missing)}."])

    order = _topological_order(adjacency, incoming)
    if order is None:
        raise WorkflowValidationError("Workflow graph contains an unsupported cycle.")
    return CompiledWorkflow(
        execution_order=tuple(order),
        node_count=len(graph.nodes),
        edge_count=len(graph.edges),
    )


def _types_compatible(source: WorkflowPortType, target: WorkflowPortType) -> bool:
    return source is WorkflowPortType.ANY or target is WorkflowPortType.ANY or source is target


def _reachable(start: str, adjacency: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    pending = [start]
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        pending.extend(adjacency.get(current, []))
    return visited


def _topological_order(
    adjacency: dict[str, list[str]], incoming: dict[str, int]
) -> list[str] | None:
    remaining = dict(incoming)
    pending = sorted(node_id for node_id, count in remaining.items() if count == 0)
    order: list[str] = []
    while pending:
        current = pending.pop(0)
        order.append(current)
        for target in sorted(adjacency[current]):
            remaining[target] -= 1
            if remaining[target] == 0:
                pending.append(target)
                pending.sort()
    return order if len(order) == len(adjacency) else None
