"""Regulatory and Legal Relationship Linker (Stage 136).

Links regulatory filings, antitrust proceedings, and SEC enforcement actions to
the regulatory authority and investigated legal entities.
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


class RegulatoryRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for regulatory enforcement and legal actions."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Regulatory Authority (SEC, DOJ, FTC, CFTC, FCA)
        regulator_id = payload.get("regulator_id") or payload.get("issuing_authority")
        if regulator_id:
            try:
                reg_node = self.resolver.resolve(str(regulator_id), as_of=as_of)
                rel_reg = self.build_relationship(
                    event=event,
                    target_node=reg_node,
                    predicate=PredicateType.REGULATED_BY,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="ENFORCEMENT_REGULATOR",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_reg)
            except Exception:
                pass

        # 2. Target Company or Entity Under Action
        target_id = payload.get("target_id") or payload.get("company_id")
        if target_id:
            try:
                target_node = self.resolver.resolve(str(target_id), as_of=as_of)
                rel_target = self.build_relationship(
                    event=event,
                    target_node=target_node,
                    predicate=PredicateType.OFFICIAL_ACTION_TARGET,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="INVESTIGATION_TARGET",
                    evidence_ids=evidence_ids,
                    metadata={"matter_type": payload.get("matter_type")},
                )
                relationships.append(rel_target)
            except Exception:
                pass

        return relationships
