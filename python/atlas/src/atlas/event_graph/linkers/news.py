"""News and Rumor Relationship Linker (Stage 136).

Links journalistic reporting, rumors, and market chatter to mentioned entities
using qualified SOURCE_REPORTED_ASSOCIATION and CANDIDATE verification status.
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


class NewsReportedRelationshipLinker(BaseEventRelationshipLinker):
    """Specialized linker for news-reported and rumor events."""

    def extract_relationships(
        self,
        event: AtlasUniversalEvent,
        evidence_ids: Optional[List[str]] = None,
        as_of: Optional[datetime] = None,
    ) -> List[AtlasEventEntityRelationship]:
        relationships: List[AtlasEventEntityRelationship] = []
        payload = event.event_payload or {}

        # Entities mentioned in the article/rumor
        mentioned_entities = payload.get("mentioned_entities") or []
        if isinstance(mentioned_entities, str):
            mentioned_entities = [mentioned_entities]

        company_id = payload.get("company_id") or payload.get("ticker")
        if company_id and company_id not in mentioned_entities:
            mentioned_entities.append(company_id)

        for ent in mentioned_entities:
            try:
                ent_node = self.resolver.resolve(str(ent), as_of=as_of)
                # If unverified news rumor, use CANDIDATE or SOURCE_SUPPORTED
                v_status = (
                    RelationshipVerificationStatus.CANDIDATE
                    if payload.get("is_rumor")
                    else RelationshipVerificationStatus.SOURCE_SUPPORTED
                )
                rel_ent = self.build_relationship(
                    event=event,
                    target_node=ent_node,
                    predicate=PredicateType.SOURCE_REPORTED_ASSOCIATION,
                    origin=RelationshipOrigin.NEWS_REPORT,
                    verification_status=v_status,
                    relationship_role="REPORTED_SUBJECT",
                    evidence_ids=evidence_ids,
                    derivation_method="NEWS_TEXT_EXTRACTION",
                    metadata={"outlet": payload.get("source_outlet")},
                )
                relationships.append(rel_ent)
            except Exception:
                pass

        return relationships
