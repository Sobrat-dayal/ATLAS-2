"""Event-to-Entity Knowledge Graph Service (Stage 136).

Orchestrates canonical resolution, family linkers, adjacency indexing,
bounded multi-hop graph traversals, bitemporal as-of evaluation,
multi-tenant isolation, and institutional review queues.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.events.domain import AtlasUniversalEvent, EventCategory
from .domain import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    EventEntityRelationshipRevision,
    GraphNodeType,
    GraphPath,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from .errors import (
    NodeNotFoundError,
    RelationshipNotFoundError,
    SourceRevokedError,
    TenantAccessDeniedError,
)
from .linkers import (
    BaseEventRelationshipLinker,
    CentralBankRelationshipLinker,
    CorporateActionRelationshipLinker,
    EarningsRelationshipLinker,
    EconomicReleaseRelationshipLinker,
    GeopoliticalRelationshipLinker,
    InfrastructureRelationshipLinker,
    NaturalEventRelationshipLinker,
    NewsReportedRelationshipLinker,
    RegulatoryRelationshipLinker,
    SanctionsRelationshipLinker,
)
from .predicates.registry import validate_predicate_allowed
from .query import (
    BoundedGraphTraversalEngine,
    HistoricalAsOfEvaluator,
    NeighborQueryEngine,
    filter_relationship,
    format_path_explanation,
)
from .resolution.resolver import CanonicalEntityResolver


class EventEntityKnowledgeGraphService:
    """Master service for the ATLAS Event-to-Entity Knowledge Graph."""

    def __init__(self, populate_seed_data: bool = True):
        self.resolver = CanonicalEntityResolver()
        self.neighbor_engine = NeighborQueryEngine()
        self.traversal_engine = BoundedGraphTraversalEngine(self.neighbor_engine)

        # Storage
        self._relationships: Dict[str, AtlasEventEntityRelationship] = {}
        self._revisions: Dict[str, List[EventEntityRelationshipRevision]] = {}
        self._review_queue: List[Dict[str, Any]] = []

        # Family linkers
        self._linkers: Dict[EventCategory, BaseEventRelationshipLinker] = {
            EventCategory.CORPORATE: CorporateActionRelationshipLinker(self.resolver),
            EventCategory.FINANCIAL: EarningsRelationshipLinker(self.resolver),
            EventCategory.ECONOMIC: EconomicReleaseRelationshipLinker(self.resolver),
            EventCategory.MONETARY_POLICY: CentralBankRelationshipLinker(self.resolver),
            EventCategory.SANCTIONS: SanctionsRelationshipLinker(self.resolver),
            EventCategory.REGULATORY: RegulatoryRelationshipLinker(self.resolver),
            EventCategory.GEOPOLITICAL: GeopoliticalRelationshipLinker(self.resolver),
            EventCategory.NATURAL_DISASTER: NaturalEventRelationshipLinker(self.resolver),
            EventCategory.PHYSICAL_WORLD: NaturalEventRelationshipLinker(self.resolver),
            EventCategory.INFRASTRUCTURE: InfrastructureRelationshipLinker(self.resolver),
            EventCategory.NEWS_REPORTED: NewsReportedRelationshipLinker(self.resolver),
        }

        if populate_seed_data:
            from .seed import seed_knowledge_graph_fixtures
            seed_knowledge_graph_fixtures(self)

    # -------------------------------------------------------------------------
    # Canonical Node Registration & Resolution
    # -------------------------------------------------------------------------
    def register_canonical_node(
        self,
        node: CanonicalGraphNodeRef,
        aliases: Optional[List[Dict[str, Any]]] = None,
    ) -> CanonicalGraphNodeRef:
        """Registers a canonical entity node and indexes its aliases."""
        return self.resolver.register_node(node, aliases)

    def get_node(self, node_type: GraphNodeType, entity_id: str) -> Optional[CanonicalGraphNodeRef]:
        """Retrieves a registered node by type and ID."""
        return self.resolver.get_node(node_type, entity_id)

    def resolve_entity(
        self,
        identifier: str,
        id_type: Optional[str] = None,
        as_of: Optional[datetime] = None,
        require_exact: bool = False,
    ) -> CanonicalGraphNodeRef:
        """Resolves an external identifier to a canonical graph node."""
        return self.resolver.resolve(
            identifier=identifier,
            id_type=id_type,
            as_of=as_of,
            require_exact=require_exact,
        )

    # -------------------------------------------------------------------------
    # Relationship Ingestion & Management
    # -------------------------------------------------------------------------
    def link_event(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Runs the appropriate family linker to extract relationships from an event."""
        linker = self._linkers.get(event.event_category)
        if not linker:
            # Fall back to news/general linker
            linker = self._linkers[EventCategory.NEWS_REPORTED]

        rels = linker.extract_relationships(event, evidence_ids=evidence_ids, as_of=as_of)
        stored_rels: List[AtlasEventEntityRelationship] = []
        for rel in rels:
            saved = self.add_relationship(rel)
            stored_rels.append(saved)
            if saved.verification_status in [
                RelationshipVerificationStatus.CANDIDATE,
                RelationshipVerificationStatus.CONFLICTED,
            ]:
                self._review_queue.append({
                    "relationship_id": saved.relationship_id,
                    "event_id": saved.event_id,
                    "status": saved.verification_status.value,
                    "reason": "Uncorroborated candidate or conflicting claims require institutional analyst review.",
                    "added_at": datetime.now(timezone.utc).isoformat(),
                    "tenant_id": saved.tenant_id,
                })

        return stored_rels

    def add_relationship(self, rel: AtlasEventEntityRelationship) -> AtlasEventEntityRelationship:
        """Validates, stores, and indexes a relationship edge."""
        # Validate predicate against node types
        validate_predicate_allowed(
            predicate_str=rel.predicate.value,
            source_type=rel.source_node.node_type,
            target_type=rel.target_node.node_type,
        )

        # Register source and target nodes in canonical resolver
        self.resolver.register_node(rel.source_node)
        self.resolver.register_node(rel.target_node)

        self._relationships[rel.relationship_id] = rel
        self.neighbor_engine.index_relationship(rel)

        # Record revision 1
        rev = EventEntityRelationshipRevision(
            revision_id=f"rev-{uuid.uuid4().hex[:8]}",
            relationship_id=rel.relationship_id,
            revision_number=1,
            changed_fields={"initial_state": rel.model_dump(mode="json")},
            reason="Initial relationship ingestion.",
        )
        self._revisions[rel.relationship_id] = [rev]
        return rel

    def add_structural_edge(
        self,
        source_node: CanonicalGraphNodeRef,
        target_node: CanonicalGraphNodeRef,
        predicate: PredicateType,
        relationship_role: Optional[str] = None,
        verification_status: RelationshipVerificationStatus = RelationshipVerificationStatus.VERIFIED_DIRECT,
        evidence_ids: Optional[List[str]] = None,
        temporal_valid_from: Optional[datetime] = None,
        temporal_valid_to: Optional[datetime] = None,
        knowledge_available_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> AtlasEventEntityRelationship:
        """Adds a verified entity-to-entity foundational edge (e.g. SUBSIDIARY_OF, OPERATED_BY)."""
        rel_id = f"rel-{uuid.uuid4().hex[:12]}"
        rel = AtlasEventEntityRelationship(
            relationship_id=rel_id,
            event_id="STRUCTURAL_RELATIONSHIP",
            event_revision_id="rev-1",
            source_node=source_node,
            target_node=target_node,
            predicate=predicate,
            relationship_role=relationship_role,
            assertion_origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
            verification_status=verification_status,
            temporal_valid_from=temporal_valid_from,
            temporal_valid_to=temporal_valid_to,
            knowledge_available_at=knowledge_available_at or datetime.now(timezone.utc),
            evidence_ids=evidence_ids or [],
            derivation_method="REGISTRY_STRUCTURAL_GRAPH",
            metadata=metadata or {},
            tenant_id=tenant_id,
        )
        return self.add_relationship(rel)

    def get_relationship(
        self,
        relationship_id: str,
        tenant_id: Optional[str] = None,
    ) -> AtlasEventEntityRelationship:
        """Retrieves a relationship by ID with tenant access control."""
        rel = self._relationships.get(relationship_id)
        if not rel:
            raise RelationshipNotFoundError(relationship_id=relationship_id)

        if rel.tenant_id is not None and rel.tenant_id != tenant_id:
            raise TenantAccessDeniedError(tenant_id=tenant_id, target_tenant_id=rel.tenant_id)

        return rel

    def get_relationship_revisions(self, relationship_id: str) -> List[EventEntityRelationshipRevision]:
        """Returns non-destructive historical revision audit trail for a relationship."""
        return self._revisions.get(relationship_id, [])

    def revoke_relationship(
        self,
        relationship_id: str,
        reason: str,
        tenant_id: Optional[str] = None,
    ) -> AtlasEventEntityRelationship:
        """Revokes a relationship edge non-destructively."""
        rel = self.get_relationship(relationship_id, tenant_id=tenant_id)
        rel.is_revoked = True
        rel.revocation_reason = reason
        rel.verification_status = RelationshipVerificationStatus.REVOKED

        rev = EventEntityRelationshipRevision(
            revision_id=f"rev-{uuid.uuid4().hex[:8]}",
            relationship_id=relationship_id,
            revision_number=len(self._revisions.get(relationship_id, [])) + 1,
            changed_fields={"is_revoked": True, "revocation_reason": reason},
            reason=reason,
        )
        self._revisions.setdefault(relationship_id, []).append(rev)
        return rel

    def handle_event_retraction(self, event_id: str, reason: str):
        """When an event is retracted in Stage 135, non-destructively revokes its graph edges."""
        for rel in list(self._relationships.values()):
            if rel.event_id == event_id and not rel.is_revoked:
                self.revoke_relationship(
                    relationship_id=rel.relationship_id,
                    reason=f"Event {event_id} was retracted: {reason}",
                    tenant_id=rel.tenant_id,
                )

    # -------------------------------------------------------------------------
    # Query & Traversal Operations
    # -------------------------------------------------------------------------
    def get_event_neighbors(
        self,
        event_id: str,
        predicate: Optional[PredicateType] = None,
        min_verification: Optional[RelationshipVerificationStatus] = None,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns verified entities linked to this event."""
        return self.neighbor_engine.get_event_neighbors(
            event_id=event_id,
            relationships=self._relationships,
            predicate=predicate,
            min_verification=min_verification,
            as_of=as_of,
            tenant_id=tenant_id,
        )

    def get_entity_events(
        self,
        node_type: GraphNodeType,
        entity_id: str,
        predicate: Optional[PredicateType] = None,
        min_verification: Optional[RelationshipVerificationStatus] = None,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns verified events linked to this entity."""
        return self.neighbor_engine.get_entity_events(
            node_type=node_type,
            entity_id=entity_id,
            relationships=self._relationships,
            predicate=predicate,
            min_verification=min_verification,
            as_of=as_of,
            tenant_id=tenant_id,
        )

    def find_paths(
        self,
        source_node_type: GraphNodeType,
        source_id: str,
        target_node_type: GraphNodeType,
        target_id: str,
        max_depth: int = 3,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> List[GraphPath]:
        """Finds bounded verified paths between two nodes with cycle prevention."""
        if max_depth > 5:
            from .errors import TraversalDepthExceededError
            raise TraversalDepthExceededError(requested_depth=max_depth, max_allowed=5)

        source_node = self.resolver.get_node(source_node_type, source_id)
        if not source_node:
            raise NodeNotFoundError(node_type=source_node_type.value, entity_id=source_id)

        target_node = self.resolver.get_node(target_node_type, target_id)
        if not target_node:
            raise NodeNotFoundError(node_type=target_node_type.value, entity_id=target_id)

        return self.traversal_engine.find_paths(
            start_node=source_node,
            end_node=target_node,
            relationships=self._relationships,
            max_depth=max_depth,
            as_of=as_of,
            tenant_id=tenant_id,
        )

    def get_neighborhood(
        self,
        node_type: GraphNodeType,
        entity_id: str,
        depth: int = 1,
        as_of: Optional[datetime] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extracts the k-hop neighborhood centered around an entity or event."""
        center_node = self.resolver.get_node(node_type, entity_id)
        if not center_node:
            raise NodeNotFoundError(node_type=node_type.value, entity_id=entity_id)

        return self.traversal_engine.extract_neighborhood(
            center_node=center_node,
            relationships=self._relationships,
            depth=depth,
            as_of=as_of,
            tenant_id=tenant_id,
        )

    def evaluate_as_of(
        self,
        as_of_time: datetime,
        tenant_id: Optional[str] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Returns all knowledge graph relationships valid and known as of the specified historical horizon."""
        return HistoricalAsOfEvaluator.filter_relationships_as_of(
            relationships=self._relationships,
            as_of_time=as_of_time,
            tenant_id=tenant_id,
        )

    def get_review_queue(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns uncorroborated candidate or conflicted relationships requiring analyst review."""
        if tenant_id is None:
            return self._review_queue
        return [item for item in self._review_queue if item.get("tenant_id") in [None, tenant_id]]
