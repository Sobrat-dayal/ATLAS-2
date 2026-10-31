"""Geopolitical Relationship Linker (Stage 136).

Links treaties, summits, and international trade developments to participating sovereign states.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from atlas.events.domain import AtlasUniversalEvent
from ..domain import (
    AtlasEventEntityRelationship,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from .base import BaseEventRelationshipLinker


class GeopoliticalRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for geopolitical and diplomatic events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Primary Actor Country
        actor_country = payload.get("actor_country") or event.geographic_scope.country_code
        if actor_country:
            try:
                actor_node = self.resolver.resolve(str(actor_country), id_type="ISO2", as_of=as_of)
                rel_actor = self.build_relationship(
                    event=event,
                    target_node=actor_node,
                    predicate=PredicateType.DIRECT_SUBJECT,
                    origin=RelationshipOrigin.GOVERNMENT_ACTION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="PRIMARY_STATE_ACTOR",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_actor)
            except Exception:
                pass

        # 2. Target or Secondary Countries
        target_countries = payload.get("target_countries") or []
        if isinstance(target_countries, str):
            target_countries = [target_countries]

        for tc in target_countries:
            try:
                tc_node = self.resolver.resolve(str(tc), id_type="ISO2", as_of=as_of)
                rel_tc = self.build_relationship(
                    event=event,
                    target_node=tc_node,
                    predicate=PredicateType.OCCURRED_IN,
                    origin=RelationshipOrigin.GOVERNMENT_ACTION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="PARTICIPATING_STATE",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_tc)
            except Exception:
                pass

        return relationships
