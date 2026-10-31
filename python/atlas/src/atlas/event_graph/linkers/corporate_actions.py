"""Corporate Actions Relationship Linker (Stage 136).

Resolves M&A, tender offers, spinoffs, and splits, precisely separating
acquirer, target, and regulatory approval roles.
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


class CorporateActionRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for corporate action and M&A events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Acquirer / Initiator (Participant)
        acquirer_id = payload.get("acquirer_id") or payload.get("initiator_id") or payload.get("company_id")
        acquirer_ticker = payload.get("acquirer_ticker") or payload.get("ticker")
        if acquirer_id or acquirer_ticker:
            try:
                ident = str(acquirer_id or acquirer_ticker)
                id_type = "COMPANY_ID" if acquirer_id else "TICKER"
                acquirer_node = self.resolver.resolve(ident, id_type=id_type, as_of=as_of)
                rel_acq = self.build_relationship(
                    event=event,
                    target_node=acquirer_node,
                    predicate=PredicateType.CORPORATE_ACTION_PARTICIPANT,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="ACQUIRER",
                    evidence_ids=evidence_ids,
                    derivation_method="CORPORATE_ACTION_ROLES",
                    metadata={"deal_value_usd": payload.get("deal_value_usd")},
                )
                relationships.append(rel_acq)
            except Exception:
                pass

        # 2. Target Company
        target_id = payload.get("target_id")
        target_ticker = payload.get("target_ticker")
        if target_id or target_ticker:
            try:
                ident = str(target_id or target_ticker)
                id_type = "COMPANY_ID" if target_id else "TICKER"
                target_node = self.resolver.resolve(ident, id_type=id_type, as_of=as_of)
                rel_target = self.build_relationship(
                    event=event,
                    target_node=target_node,
                    predicate=PredicateType.CORPORATE_ACTION_TARGET,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="TARGET",
                    evidence_ids=evidence_ids,
                    derivation_method="CORPORATE_ACTION_ROLES",
                )
                relationships.append(rel_target)
            except Exception:
                pass

        # 3. Reviewing Regulatory Authority (e.g., FTC, DOJ, EC)
        regulator_id = payload.get("regulator_id")
        if regulator_id:
            try:
                reg_node = self.resolver.resolve(str(regulator_id), as_of=as_of)
                rel_reg = self.build_relationship(
                    event=event,
                    target_node=reg_node,
                    predicate=PredicateType.REGULATED_BY,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="REVIEWING_REGULATOR",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_reg)
            except Exception:
                pass

        return relationships
