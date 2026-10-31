"""ATLAS Intelligence Subsystem (Stage 136).

Provides Event-to-Entity Knowledge Graph and relationship intelligence capabilities.
"""

from atlas.event_graph import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    EventEntityKnowledgeGraphService,
    EventEntityRelationshipRevision,
    GraphNodeType,
    GraphPath,
    GraphPathHop,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)

__all__ = [
    "AtlasEventEntityRelationship",
    "CanonicalGraphNodeRef",
    "EventEntityKnowledgeGraphService",
    "EventEntityRelationshipRevision",
    "GraphNodeType",
    "GraphPath",
    "GraphPathHop",
    "PredicateType",
    "RelationshipOrigin",
    "RelationshipVerificationStatus",
]
