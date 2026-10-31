"""FastAPI Router for ATLAS Event-to-Entity Knowledge Graph (Stage 136).

Prefix: /api/v1/knowledge-graph
Provides institutional endpoints for:
- Canonical entity resolution and disambiguation
- Event-to-entity direct neighbor extraction
- Reverse entity-to-event queries
- Bounded multi-hop graph path discovery with cycle prevention
- Neighborhood subgraph exploration
- Zero look-ahead bitemporal as-of evaluation
- Review queue management for uncorroborated / candidate relations
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status

from atlas.auth import AuthPrincipal
from atlas.event_graph import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    EventEntityKnowledgeGraphService,
    EventEntityRelationshipRevision,
    GraphNodeType,
    GraphPath,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from atlas.event_graph.errors import (
    GraphCycleDetectedError,
    GraphDomainError,
    IdentityResolutionError,
    InvalidPredicateError,
    LookAheadViolationError,
    NodeNotFoundError,
    ProhibitedPredicateError,
    RelationshipNotFoundError,
    SourceRevokedError,
    TenantAccessDeniedError,
    TraversalDepthExceededError,
)
from atlas.event_graph.predicates.registry import ALLOWED_NODE_PAIRS, PROHIBITED_PREDICATES

from ..auth.dependencies import get_optional_user

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])

# Singleton service instance populated with Stage 136 seed fixtures
_graph_service = EventEntityKnowledgeGraphService(populate_seed_data=True)


def get_graph_service() -> EventEntityKnowledgeGraphService:
    """Dependency injector for knowledge graph service."""
    return _graph_service


# Request / Response Schemas
class ResolveEntityRequest(BaseModel):
    identifier: str
    id_type: Optional[str] = None
    as_of: Optional[datetime] = None
    require_exact: bool = False


class PathSearchRequest(BaseModel):
    source_node_type: GraphNodeType
    source_id: str
    target_node_type: GraphNodeType
    target_id: str
    max_depth: int = Field(default=3, ge=1, le=5)
    as_of: Optional[datetime] = None


class NeighborhoodRequest(BaseModel):
    node_type: GraphNodeType
    entity_id: str
    depth: int = Field(default=1, ge=1, le=3)
    as_of: Optional[datetime] = None


class AsOfEvaluationRequest(BaseModel):
    as_of_time: datetime


class RevokeRelationshipRequest(BaseModel):
    reason: str


class GraphQueryRequest(BaseModel):
    event_id: Optional[str] = None
    entity_id: Optional[str] = None
    node_type: Optional[GraphNodeType] = None
    predicate: Optional[PredicateType] = None
    min_verification: Optional[RelationshipVerificationStatus] = None
    as_of: Optional[datetime] = None


# -----------------------------------------------------------------------------
# Metadata & Capability Endpoints
# -----------------------------------------------------------------------------
@router.get("/capabilities")
async def get_capabilities(user: Optional[AuthPrincipal] = Depends(get_optional_user)):
    """Returns knowledge graph capabilities and configuration boundaries."""
    return {
        "stage": "136",
        "subsystem": "Event-to-Entity Knowledge Graph and Relationship Intelligence Engine",
        "max_traversal_depth": 5,
        "supported_node_types": [nt.value for nt in GraphNodeType],
        "supported_predicates": [p.value for p in PredicateType],
        "prohibited_predicates": list(PROHIBITED_PREDICATES),
        "zero_look_ahead_enforced": True,
        "cycle_detection_enforced": True,
        "multi_tenancy_supported": True,
    }


@router.get("/node-types")
async def get_node_types(user: Optional[AuthPrincipal] = Depends(get_optional_user)):
    """Lists all supported canonical graph node types."""
    return {
        "node_types": [
            {"code": nt.value, "description": nt.name.replace("_", " ").title()}
            for nt in GraphNodeType
        ]
    }


@router.get("/predicates")
async def get_predicates(user: Optional[AuthPrincipal] = Depends(get_optional_user)):
    """Lists all approved graph predicates and forbidden causal/speculative predicates."""
    return {
        "approved_predicates": [
            {
                "code": p.value,
                "name": p.name.replace("_", " ").title(),
                "allowed_pairs_count": len(ALLOWED_NODE_PAIRS.get(p, [])),
            }
            for p in PredicateType
        ],
        "prohibited_predicates": list(PROHIBITED_PREDICATES),
    }


# -----------------------------------------------------------------------------
# Canonical Resolution
# -----------------------------------------------------------------------------
@router.post("/resolve-entity", response_model=CanonicalGraphNodeRef)
async def resolve_entity(
    req: ResolveEntityRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Resolves an external identifier (LEI, CIK, Ticker, ISIN, etc.) to a canonical graph node."""
    try:
        return service.resolve_entity(
            identifier=req.identifier,
            id_type=req.id_type,
            as_of=req.as_of,
            require_exact=req.require_exact,
        )
    except IdentityResolutionError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


# -----------------------------------------------------------------------------
# Direct Neighbors (1-Hop Lookups)
# -----------------------------------------------------------------------------
@router.get("/events/{event_id}/neighbors", response_model=List[AtlasEventEntityRelationship])
async def get_event_neighbors(
    event_id: str,
    predicate: Optional[str] = None,
    min_verification: Optional[str] = None,
    as_of: Optional[datetime] = None,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Retrieves all canonical entities connected to a specified event."""
    pred = PredicateType(predicate.upper()) if predicate else None
    min_v = RelationshipVerificationStatus(min_verification.upper()) if min_verification else None
    tenant_id = getattr(user, "tenant_id", None)

    return service.get_event_neighbors(
        event_id=event_id,
        predicate=pred,
        min_verification=min_v,
        as_of=as_of,
        tenant_id=tenant_id,
    )


@router.get("/entities/{node_type}/{entity_id}/events", response_model=List[AtlasEventEntityRelationship])
async def get_entity_events(
    node_type: str,
    entity_id: str,
    predicate: Optional[str] = None,
    min_verification: Optional[str] = None,
    as_of: Optional[datetime] = None,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Retrieves all canonical events linked to a specified entity (reverse lookup)."""
    try:
        nt = GraphNodeType(node_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid node_type '{node_type}'.",
        )

    pred = PredicateType(predicate.upper()) if predicate else None
    min_v = RelationshipVerificationStatus(min_verification.upper()) if min_verification else None
    tenant_id = getattr(user, "tenant_id", None)

    return service.get_entity_events(
        node_type=nt,
        entity_id=entity_id,
        predicate=pred,
        min_verification=min_v,
        as_of=as_of,
        tenant_id=tenant_id,
    )


# -----------------------------------------------------------------------------
# Relationship Details & History
# -----------------------------------------------------------------------------
@router.get("/relationships/{relationship_id}", response_model=AtlasEventEntityRelationship)
async def get_relationship(
    relationship_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Retrieves a specific relationship edge by ID."""
    tenant_id = getattr(user, "tenant_id", None)
    try:
        return service.get_relationship(relationship_id=relationship_id, tenant_id=tenant_id)
    except RelationshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except TenantAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


@router.get("/relationships/{relationship_id}/evidence")
async def get_relationship_evidence(
    relationship_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Returns supporting evidence identifiers and derivation metadata for a relationship."""
    tenant_id = getattr(user, "tenant_id", None)
    try:
        rel = service.get_relationship(relationship_id=relationship_id, tenant_id=tenant_id)
        return {
            "relationship_id": rel.relationship_id,
            "evidence_ids": rel.evidence_ids,
            "derivation_method": rel.derivation_method,
            "assertion_origin": rel.assertion_origin.value,
            "verification_status": rel.verification_status.value,
            "proximity_metadata": rel.proximity_metadata,
        }
    except RelationshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("/relationships/{relationship_id}/history", response_model=List[EventEntityRelationshipRevision])
async def get_relationship_history(
    relationship_id: str,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Returns the non-destructive revision audit trail for a relationship."""
    tenant_id = getattr(user, "tenant_id", None)
    # Validate access
    try:
        service.get_relationship(relationship_id=relationship_id, tenant_id=tenant_id)
    except RelationshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except TenantAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)

    return service.get_relationship_revisions(relationship_id)


@router.post("/relationships/{relationship_id}/revoke", response_model=AtlasEventEntityRelationship)
async def revoke_relationship(
    relationship_id: str,
    req: RevokeRelationshipRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Revokes a relationship edge non-destructively."""
    tenant_id = getattr(user, "tenant_id", None)
    try:
        return service.revoke_relationship(
            relationship_id=relationship_id,
            reason=req.reason,
            tenant_id=tenant_id,
        )
    except RelationshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except TenantAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)


# -----------------------------------------------------------------------------
# Multi-Hop Traversal & Path Discovery
# -----------------------------------------------------------------------------
@router.post("/paths", response_model=List[GraphPath])
async def find_paths(
    req: PathSearchRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Discovers bounded multi-hop paths between two nodes with guaranteed cycle prevention."""
    tenant_id = getattr(user, "tenant_id", None)
    try:
        return service.find_paths(
            source_node_type=req.source_node_type,
            source_id=req.source_id,
            target_node_type=req.target_node_type,
            target_id=req.target_id,
            max_depth=req.max_depth,
            as_of=req.as_of,
            tenant_id=tenant_id,
        )
    except NodeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except TraversalDepthExceededError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/neighborhood")
async def get_neighborhood(
    req: NeighborhoodRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Extracts the k-hop neighborhood centered around an entity or event."""
    tenant_id = getattr(user, "tenant_id", None)
    try:
        return service.get_neighborhood(
            node_type=req.node_type,
            entity_id=req.entity_id,
            depth=req.depth,
            as_of=req.as_of,
            tenant_id=tenant_id,
        )
    except NodeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    except TraversalDepthExceededError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


# -----------------------------------------------------------------------------
# Historical As-Of & Review Queue
# -----------------------------------------------------------------------------
@router.post("/as-of", response_model=List[AtlasEventEntityRelationship])
async def evaluate_as_of(
    req: AsOfEvaluationRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Reconstructs the knowledge graph point-in-time as-of a historical timestamp (Zero Look-Ahead)."""
    tenant_id = getattr(user, "tenant_id", None)
    return service.evaluate_as_of(as_of_time=req.as_of_time, tenant_id=tenant_id)


@router.get("/review-queue")
async def get_review_queue(
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """Retrieves uncorroborated candidate or conflicted relationships requiring analyst review."""
    tenant_id = getattr(user, "tenant_id", None)
    return service.get_review_queue(tenant_id=tenant_id)


@router.post("/query", response_model=List[AtlasEventEntityRelationship])
async def query_relationships(
    req: GraphQueryRequest,
    user: Optional[AuthPrincipal] = Depends(get_optional_user),
    service: EventEntityKnowledgeGraphService = Depends(get_graph_service),
):
    """General query endpoint for filtering relationships by event, entity, predicate, or status."""
    tenant_id = getattr(user, "tenant_id", None)
    if req.event_id:
        return service.get_event_neighbors(
            event_id=req.event_id,
            predicate=req.predicate,
            min_verification=req.min_verification,
            as_of=req.as_of,
            tenant_id=tenant_id,
        )
    elif req.entity_id and req.node_type:
        return service.get_entity_events(
            node_type=req.node_type,
            entity_id=req.entity_id,
            predicate=req.predicate,
            min_verification=req.min_verification,
            as_of=req.as_of,
            tenant_id=tenant_id,
        )
    elif req.as_of:
        return service.evaluate_as_of(as_of_time=req.as_of, tenant_id=tenant_id)
    else:
        # Return all active relationships for tenant
        all_rels = service._relationships.values()
        return [
            r for r in all_rels
            if (req.predicate is None or r.predicate == req.predicate)
            and (req.min_verification is None or r.verification_status == req.min_verification)
            and (r.tenant_id in [None, tenant_id])
            and not r.is_revoked
        ]
