"""Sanctions Relationship Linker (Stage 136).

Links official sanctions designations to the sanctioning authority, designated legal entities,
and issuing jurisdiction. Enforces institutional invariant: Strict exact identifier or official
registry match; NEVER performs fuzzy name matching to prevent false-positive designations of innocent firms.
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


class SanctionsRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for sanctions events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Sanctions Authority (e.g., OFAC, EU_COUNCIL, UK_OFSI)
        authority_id = payload.get("authority_id") or payload.get("issuing_authority")
        if authority_id:
            try:
                auth_node = self.resolver.resolve(str(authority_id), as_of=as_of)
                rel_auth = self.build_relationship(
                    event=event,
                    target_node=auth_node,
                    predicate=PredicateType.ISSUED_BY,
                    origin=RelationshipOrigin.GOVERNMENT_ACTION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="SANCTIONS_AUTHORITY",
                    evidence_ids=evidence_ids,
                    derivation_method="OFFICIAL_GOVERNMENT_ACTION",
                )
                relationships.append(rel_auth)
            except Exception:
                pass

        # 2. Designated Legal Entities - STRICT EXACT MATCH ONLY
        designated_entities = payload.get("designated_entities") or []
        if isinstance(designated_entities, str):
            designated_entities = [designated_entities]

        # Also check single entity fields
        designated_id = payload.get("designated_entity_id")
        designated_lei = payload.get("designated_lei")
        if designated_id and designated_id not in designated_entities:
            designated_entities.append(designated_id)
        if designated_lei and designated_lei not in designated_entities:
            designated_entities.append(designated_lei)

        for target_id in designated_entities:
            try:
                # require_exact=True enforces zero fuzzy match
                target_node = self.resolver.resolve(
                    str(target_id),
                    as_of=as_of,
                    require_exact=True,
                )
                rel_target = self.build_relationship(
                    event=event,
                    target_node=target_node,
                    predicate=PredicateType.OFFICIALLY_DESIGNATES,
                    origin=RelationshipOrigin.GOVERNMENT_ACTION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="DESIGNATED_SANCTION_TARGET",
                    evidence_ids=evidence_ids,
                    derivation_method="EXACT_LEGAL_ENTITY_REGISTRY_MATCH",
                    metadata={
                        "program": payload.get("program"),
                        "legal_basis": payload.get("legal_basis"),
                    },
                )
                relationships.append(rel_target)
            except Exception:
                # If cannot resolve exactly, skip or flag in metadata rather than fuzzy-matching innocent entity
                pass

        # 3. Issuing Jurisdiction / Country
        country_code = event.geographic_scope.country_code or payload.get("country_code")
        if country_code:
            try:
                country_node = self.resolver.resolve(str(country_code), id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.HAS_ISSUING_JURISDICTION,
                    origin=RelationshipOrigin.GOVERNMENT_ACTION,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="SANCTIONS_JURISDICTION",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        return relationships

