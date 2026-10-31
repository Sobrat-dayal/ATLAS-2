"""Earnings Relationship Linker (Stage 136).

Links earnings announcements and financial results to the reporting company or issuer.
Enforces institutional invariant: Never explodes into unmentioned securities,
ADRs, or distinct share classes (e.g., Class A vs Class C).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from atlas.events.domain import AtlasUniversalEvent
from ..domain import (
    AtlasEventEntityRelationship,
    GraphNodeType,
    PredicateType,
    RelationshipOrigin,
    RelationshipVerificationStatus,
)
from .base import BaseEventRelationshipLinker


class EarningsRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for corporate earnings events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Resolve reporting company / issuer
        company_id = payload.get("company_id") or payload.get("issuer_id")
        ticker = payload.get("ticker")
        cik = payload.get("cik")
        lei = payload.get("lei")

        company_node = None
        for identifier, id_type in [(lei, "LEI"), (cik, "CIK"), (ticker, "TICKER"), (company_id, "COMPANY_ID")]:
            if identifier:
                try:
                    company_node = self.resolver.resolve(str(identifier), id_type=id_type, as_of=as_of)
                    break
                except Exception:
                    continue

        if company_node:
            rel = self.build_relationship(
                event=event,
                target_node=company_node,
                predicate=PredicateType.ANNOUNCED_BY,
                origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                relationship_role="REPORTING_ISSUER",
                evidence_ids=evidence_ids,
                derivation_method="CANONICAL_EARNINGS_LINKER",
                metadata={"fiscal_period": payload.get("period") or payload.get("fiscal_quarter")},
            )
            relationships.append(rel)

        # 2. Check if a specific primary instrument is explicitly mentioned
        primary_instrument_id = payload.get("primary_instrument_id")
        if primary_instrument_id:
            try:
                instrument_node = self.resolver.resolve(str(primary_instrument_id), id_type="ISIN", as_of=as_of)
                rel_inst = self.build_relationship(
                    event=event,
                    target_node=instrument_node,
                    predicate=PredicateType.CONCERNS_INSTRUMENT,
                    origin=RelationshipOrigin.OFFICIAL_DISCLOSURE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="PRIMARY_EQUITY_INSTRUMENT",
                    evidence_ids=evidence_ids,
                    derivation_method="EXPLICIT_SECURITY_MENTION",
                )
                relationships.append(rel_inst)
            except Exception:
                pass

        # 3. Country / Jurisdiction of incorporation or reporting
        if event.geographic_scope.country_code:
            try:
                country_node = self.resolver.resolve(event.geographic_scope.country_code, id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.OCCURRED_IN,
                    origin=RelationshipOrigin.REGULATORY_FILING,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        return relationships

