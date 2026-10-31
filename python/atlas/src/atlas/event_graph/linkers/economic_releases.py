"""Economic Releases Relationship Linker (Stage 136).

Links macroeconomic statistical releases to economic indicators, statistical agencies,
and sovereign jurisdictions.
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


class EconomicReleaseRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for macroeconomic release events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # 1. Economic Indicator (e.g. CPI_US, NFP_US, GDP_EU)
        indicator_id = payload.get("indicator_id") or payload.get("series_id")
        if indicator_id:
            try:
                ind_node = self.resolver.resolve(str(indicator_id), id_type="INDICATOR_ID", as_of=as_of)
                rel_ind = self.build_relationship(
                    event=event,
                    target_node=ind_node,
                    predicate=PredicateType.RELEASES_INDICATOR,
                    origin=RelationshipOrigin.STATISTICAL_AGENCY,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="REPORTED_INDICATOR",
                    evidence_ids=evidence_ids,
                    derivation_method="STATISTICAL_SERIES_MATCH",
                    metadata={
                        "actual_value": payload.get("actual_value"),
                        "prior_value": payload.get("prior_value"),
                        "consensus_value": payload.get("consensus_value"),
                    },
                )
                relationships.append(rel_ind)
            except Exception:
                pass

        # 2. Issuing Statistical Agency
        agency_id = payload.get("agency_id") or payload.get("reporting_agency")
        if agency_id:
            try:
                agency_node = self.resolver.resolve(str(agency_id), as_of=as_of)
                rel_agency = self.build_relationship(
                    event=event,
                    target_node=agency_node,
                    predicate=PredicateType.ANNOUNCED_BY,
                    origin=RelationshipOrigin.STATISTICAL_AGENCY,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="STATISTICAL_AGENCY",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_agency)
            except Exception:
                pass

        # 3. Sovereign Jurisdiction / Country
        country_code = event.geographic_scope.country_code or payload.get("country_code")
        if country_code:
            try:
                country_node = self.resolver.resolve(str(country_code), id_type="ISO2", as_of=as_of)
                rel_country = self.build_relationship(
                    event=event,
                    target_node=country_node,
                    predicate=PredicateType.HAS_ISSUING_JURISDICTION,
                    origin=RelationshipOrigin.STATISTICAL_AGENCY,
                    verification_status=RelationshipVerificationStatus.VERIFIED_DIRECT,
                    relationship_role="SOVEREIGN_JURISDICTION",
                    evidence_ids=evidence_ids,
                )
                relationships.append(rel_country)
            except Exception:
                pass

        return relationships
