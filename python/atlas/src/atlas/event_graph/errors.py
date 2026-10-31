"""Exception definitions for ATLAS Event-to-Entity Knowledge Graph (Stage 136).

Provides typed domain errors for relationship integrity, prohibited predicates,
identity resolution failures, multi-tenant boundaries, and bitemporal look-ahead violations.
"""

from typing import Optional


class GraphDomainError(Exception):
    """Base exception for all Event-to-Entity Knowledge Graph domain operations."""
    def __init__(self, message: str, code: str = "GRAPH_DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class RelationshipNotFoundError(GraphDomainError):
    """Raised when a specified relationship ID does not exist."""
    def __init__(self, relationship_id: str):
        super().__init__(
            f"Relationship with ID '{relationship_id}' not found.",
            code="RELATIONSHIP_NOT_FOUND"
        )
        self.relationship_id = relationship_id


class NodeNotFoundError(GraphDomainError):
    """Raised when a specified node reference cannot be found in canonical registries."""
    def __init__(self, node_type: str, entity_id: str):
        super().__init__(
            f"Node '{node_type}:{entity_id}' not found in canonical registries.",
            code="NODE_NOT_FOUND"
        )
        self.node_type = node_type
        self.entity_id = entity_id


class InvalidPredicateError(GraphDomainError):
    """Raised when an edge predicate is incompatible with node types or malformed."""
    def __init__(self, predicate: str, reason: str):
        super().__init__(
            f"Predicate '{predicate}' is invalid: {reason}",
            code="INVALID_PREDICATE"
        )
        self.predicate = predicate
        self.reason = reason


class ProhibitedPredicateError(GraphDomainError):
    """Raised when attempting to use causal or speculative predicates (e.g., AFFECTS, DAMAGED)."""
    def __init__(self, predicate: str):
        super().__init__(
            f"Predicate '{predicate}' is strictly prohibited. ATLAS Knowledge Graph records verified "
            f"factual associations only, not speculative economic exposure or causal loss claims.",
            code="PROHIBITED_PREDICATE"
        )
        self.predicate = predicate


class TraversalDepthExceededError(GraphDomainError):
    """Raised when a graph traversal request exceeds institutional maximum depth."""
    def __init__(self, requested_depth: int, max_allowed: int = 5):
        super().__init__(
            f"Traversal depth {requested_depth} exceeds maximum allowable institutional depth ({max_allowed}).",
            code="TRAVERSAL_DEPTH_EXCEEDED"
        )
        self.requested_depth = requested_depth
        self.max_allowed = max_allowed


class GraphCycleDetectedError(GraphDomainError):
    """Raised when an invalid cyclic path is encountered during bounded acyclic exploration."""
    def __init__(self, cycle_path: str):
        super().__init__(
            f"Graph cycle detected along path: {cycle_path}",
            code="GRAPH_CYCLE_DETECTED"
        )
        self.cycle_path = cycle_path


class IdentityResolutionError(GraphDomainError):
    """Raised when an entity reference cannot be unambiguously resolved to a canonical node."""
    def __init__(self, identifier: str, reason: str):
        super().__init__(
            f"Failed to resolve identifier '{identifier}': {reason}",
            code="IDENTITY_RESOLUTION_ERROR"
        )
        self.identifier = identifier
        self.reason = reason


class SourceRevokedError(GraphDomainError):
    """Raised when relationship evidence relies on a revoked or de-authorized data source."""
    def __init__(self, source_id: str, relationship_id: str):
        super().__init__(
            f"Access denied: Relationship '{relationship_id}' is grounded by revoked/unentitled source '{source_id}'.",
            code="SOURCE_REVOKED"
        )
        self.source_id = source_id
        self.relationship_id = relationship_id


class LookAheadViolationError(GraphDomainError):
    """Raised when a point-in-time query requests knowledge from after the as-of horizon."""
    def __init__(self, as_of_time: str, knowledge_time: str):
        super().__init__(
            f"Look-ahead violation: Knowledge available at {knowledge_time} cannot be queried as-of {as_of_time}.",
            code="LOOK_AHEAD_VIOLATION"
        )
        self.as_of_time = as_of_time
        self.knowledge_time = knowledge_time


class TenantAccessDeniedError(GraphDomainError):
    """Raised when attempting to access a relationship belonging to another tenant."""
    def __init__(self, tenant_id: Optional[str], target_tenant_id: Optional[str]):
        super().__init__(
            f"Access denied: Tenant '{tenant_id}' is not authorized to access resource belonging to '{target_tenant_id}'.",
            code="TENANT_ACCESS_DENIED"
        )
        self.tenant_id = tenant_id
        self.target_tenant_id = target_tenant_id

