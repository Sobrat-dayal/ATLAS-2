"""Infrastructure Relationship Linker (Stage 136).

Links infrastructure outages, pipeline closures, and port disruptions to
the physical asset, operating entity, and host jurisdiction.
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


class InfrastructureRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for infrastructure and physical asset events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Physical Infrastructure Asset
        asset_id = payload.get("asset_id") or payload.get("infrastructure_id")
        if asset_id:
            try:
                asset_node = self.resolver.resolve(str(asset_id), id_type="ASSET_ID", as_of=as_of)
                rel_asset = self.build_relationship(
                    event=event,
                    target_node=asset_node,
                    predicate=PredicateType.REFERENCES_INFRASTRUCTURE_ASSET,
                    origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="PRIMARY_INFRASTRUCTURE_ASSET",
                    evidence_ids=evidence_ids,
                    derivation_method="INFRASTRUCTURE_REGISTRY_MATCH",
                    metadata={"asset_type": payload.get("asset_type")},
                )
                relationships.append(rel_asset)
            except Exception:
                pass

        # 2. Operating Entity
        operator_id = payload.get("operator_id") or payload.get("company_id")
        if operator_id:
            try:
                op_node = self.resolver.resolve(str(operator_id), as_of=as_of)
                rel_op = self.build_relationship(
                    event=event,
                    target_node=op_node,
                    predicate=PredicateType.DIRECT_SUBJECT,
                    origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="ASSET_OPERATOR",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_op)
            except Exception:
                pass

        # 3. Country / Jurisdiction
        country_code = event.geographic_scope.country_code or payload.get("country_code")
        if country_code:
            try:
                country_node = self.resolver.resolve(str(country_code), id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.OCCURRED_IN,
                    origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        return relationships

