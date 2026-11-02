"""Typed workflow graph contracts for Stage 147."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class WorkflowNodeType(StrEnum):
    MANUAL_TRIGGER = "MANUAL_TRIGGER"
    AI_AGENT = "AI_AGENT"
    ATLAS_TOOL = "ATLAS_TOOL"
    CONDITION = "CONDITION"
    RETURN = "RETURN"


class WorkflowPortType(StrEnum):
    ANY = "ANY"
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    JSON_OBJECT = "JSON_OBJECT"


@dataclass(frozen=True, slots=True)
class WorkflowNode:
    node_id: str
    node_type: WorkflowNodeType
    config: dict[str, Any] = field(default_factory=dict)
    input_type: WorkflowPortType = WorkflowPortType.ANY
    output_type: WorkflowPortType = WorkflowPortType.ANY


@dataclass(frozen=True, slots=True)
class WorkflowEdge:
    edge_id: str
    source_node_id: str
    target_node_id: str
    source_type: WorkflowPortType = WorkflowPortType.ANY
    target_type: WorkflowPortType = WorkflowPortType.ANY


@dataclass(frozen=True, slots=True)
class WorkflowGraph:
    nodes: tuple[WorkflowNode, ...]
    edges: tuple[WorkflowEdge, ...]
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_schema: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkflowVersion:
    version_id: str
    workflow_id: str
    version: int
    graph: WorkflowGraph
    status: str


@dataclass(frozen=True, slots=True)
class WorkflowDefinition:
    workflow_id: str
    tenant_id: str
    owner_id: str
    name: str
    description: str
    status: str
    versions: tuple[WorkflowVersion, ...]