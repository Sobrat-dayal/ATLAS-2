"""Base Linker for Event-to-Entity Knowledge Graph (Stage 136)."""

from __future__ import annotations

import abc
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from atlas.events.domain import AtlasUniversalEvent
from ..domain import (
    AtlasEventEntityRelationship,
    CanonicalGraphNodeRef,
    GraphNodeType,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from ..resolution.resolver import CanonicalEntityResolver


class BaseEventRelationshipLinker(abc.ABC):
    """Abstract base linker for establishing verified event-to-entity relationships."""

    def __init__(self, resolver: CanonicalEntityResolver):
        self.resolver = resolver

    @abc.abstractmethod
    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        """Extracts verified relationships from an event according to domain family rules."""
        pass

    def create_event_node(self, event: AtlasUniversalEvent) -> CanonicalGraphNodeRef:
        """Constructs a canonical graph node representation of the event."""
        return CanonicalGraphNodeRef(
            node_type=GraphNodeType.EVENT,
            entity_id=event.event_id,
            canonical_name=event.title,
            identifier_map={"CANONICAL_KEY": event.canonical_event_key},
            country_code=event.geographic_scope.country_code,
            metadata={
                "event_category": event.event_category.value,
                "event_type": event.event_type,
                "lifecycle_status": event.lifecycle_status.value,
                "verification_status": event.verification_status.value,
            },
            tenant_id=event.tenant_id,
        )

    def build_relationship(
        self,
        event: AtlasUniversalEvent,
        target_node: CanonicalGraphNodeRef,
        predicate: PredicateType,
        origin: RelationshipOrigin,
        verification_status: RelationshipVerificationStatus,
        relationship_role: Optional[str] = None,
        evidence_ids: Optional[List[str]] = None,
        temporal_valid_from: Optional[datetime] = None,
        temporal_valid_to: Optional[datetime] = None,
        proximity_metadata: Optional[Dict[str, Any]] = None,
        derivation_method: str = "DIRECT_EXTRACTED",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AtlasEventEntityRelationship:
        """Constructs an institutional AtlasEventEntityRelationship edge."""
        event_node = self.create_event_node(event)
        rel_id = f"rel-{uuid.uuid4().hex[:12]}"
        
        return AtlasEventEntityRelationship(
            relationship_id=rel_id,
            event_id=event.event_id,
            event_revision_id=f"rev-{event.current_revision_number}",
            source_node=event_node,
            target_node=target_node,
            predicate=predicate,
            relationship_role=relationship_role,
            assertion_origin=origin,
            verification_status=verification_status,
            temporal_valid_from=temporal_valid_from or event.occurred_at or event.announced_at,
            temporal_valid_to=temporal_valid_to,
            knowledge_available_at=event.first_ingested_at or datetime.now(timezone.utc),
            evidence_ids=evidence_ids or [],
            derivation_method=derivation_method,
            proximity_metadata=proximity_metadata,
            metadata=metadata or {},
            tenant_id=event.tenant_id,
        )

