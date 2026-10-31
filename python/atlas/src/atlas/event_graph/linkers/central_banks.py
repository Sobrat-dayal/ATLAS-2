"""Central Bank Decision Relationship Linker (Stage 136).

Links monetary policy announcements and interest rate decisions to
the central bank, sovereign jurisdiction, and policy instruments.
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


class CentralBankRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for central bank and monetary policy events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Deciding Central Bank
        cb_id = payload.get("central_bank_id") or payload.get("institution") or payload.get("issuer_id")
        if cb_id:
            try:
                cb_node = self.resolver.resolve(str(cb_id), as_of=as_of)
                rel_cb = self.build_relationship(
                    event=event,
                    target_node=cb_node,
                    predicate=PredicateType.DECIDED_BY,
                    origin=RelationshipOrigin.CENTRAL_BANK_RELEASE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="DECISION_MAKER",
                    evidence_ids=evidence_ids,
                    derivation_method="CENTRAL_BANK_RESOLVER",
                    metadata={
                        "decision_type": payload.get("decision_type"),
                        "rate_change_bps": payload.get("rate_change_bps"),
                    },
                )
                relationships.append(rel_cb)
            except Exception:
                pass

        # 2. Sovereign Jurisdiction
        country_code = event.geographic_scope.country_code or payload.get("country_code")
        if country_code:
            try:
                country_node = self.resolver.resolve(str(country_code), id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.HAS_ISSUING_JURISDICTION,
                    origin=RelationshipOrigin.CENTRAL_BANK_RELEASE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="MONETARY_JURISDICTION",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        # 3. Policy Target Rate / Benchmark Instrument
        benchmark_id = payload.get("benchmark_rate_id") or payload.get("benchmark_instrument_id")
        if benchmark_id:
            try:
                bm_node = self.resolver.resolve(str(benchmark_id), as_of=as_of)
                rel_bm = self.build_relationship(
                    event=event,
                    target_node=bm_node,
                    predicate=PredicateType.CONCERNS_INSTRUMENT,
                    origin=RelationshipOrigin.CENTRAL_BANK_RELEASE,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="BENCHMARK_INSTRUMENT",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_bm)
            except Exception:
                pass

        return relationships

