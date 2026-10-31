"""Domain Definitions for Event-to-Entity Knowledge Graph (Stage 136).

Institutional-grade typed graph nodes, typed directed predicates,
relationship representations, verification statuses, bitemporal validities,
and factual path hops.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodeType(str, Enum):
    """Canonical graph node types across the ATLAS platform."""
    EVENT = "EVENT"
    COMPANY = "COMPANY"
    ISSUER = "ISSUER"
    LEGAL_ENTITY = "LEGAL_ENTITY"
    FINANCIAL_INSTRUMENT = "FINANCIAL_INSTRUMENT"
    SECTOR = "SECTOR"
    INDUSTRY = "INDUSTRY"
    COUNTRY = "COUNTRY"
    ADMINISTRATIVE_REGION = "ADMINISTRATIVE_REGION"
    COMMODITY = "COMMODITY"
    ECONOMIC_INDICATOR = "ECONOMIC_INDICATOR"
    CENTRAL_BANK = "CENTRAL_BANK"
    REGULATORY_AUTHORITY = "REGULATORY_AUTHORITY"
    CORPORATE_FACILITY = "CORPORATE_FACILITY"
    INFRASTRUCTURE_ASSET = "INFRASTRUCTURE_ASSET"
    OTHER_SUPPORTED_CANONICAL_ENTITY = "OTHER_SUPPORTED_CANONICAL_ENTITY"


class PredicateType(str, Enum):
    """Institutional directed graph predicates.
    
    Ambiguous predicates such as 'AFFECTS', 'CAUSED_LOSS', or 'DAMAGED'
    are strictly prohibited.
    """
    # Event-to-Entity Direct & Mention Predicates
    DIRECT_SUBJECT = "DIRECT_SUBJECT"
    EXPLICITLY_MENTIONS = "EXPLICITLY_MENTIONS"
    ANNOUNCED_BY = "ANNOUNCED_BY"
    ISSUED_BY = "ISSUED_BY"
    REGULATED_BY = "REGULATED_BY"
    OFFICIALLY_DESIGNATES = "OFFICIALLY_DESIGNATES"
    OFFICIAL_ACTION_TARGET = "OFFICIAL_ACTION_TARGET"
    CORPORATE_ACTION_PARTICIPANT = "CORPORATE_ACTION_PARTICIPANT"
    CORPORATE_ACTION_TARGET = "CORPORATE_ACTION_TARGET"
    CONCERNS_INSTRUMENT = "CONCERNS_INSTRUMENT"
    RELEASES_INDICATOR = "RELEASES_INDICATOR"
    DECIDED_BY = "DECIDED_BY"
    HAS_ISSUING_JURISDICTION = "HAS_ISSUING_JURISDICTION"
    OCCURRED_IN = "OCCURRED_IN"
    REPORTED_AT = "REPORTED_AT"
    REFERENCES_COMMODITY = "REFERENCES_COMMODITY"
    REFERENCES_SECTOR = "REFERENCES_SECTOR"
    REFERENCES_INDUSTRY = "REFERENCES_INDUSTRY"
    REFERENCES_FACILITY = "REFERENCES_FACILITY"
    REFERENCES_INFRASTRUCTURE_ASSET = "REFERENCES_INFRASTRUCTURE_ASSET"
    GEOGRAPHICALLY_NEAR = "GEOGRAPHICALLY_NEAR"
    SOURCE_REPORTED_ASSOCIATION = "SOURCE_REPORTED_ASSOCIATION"

    # Event-to-Event Predicates
    REVISES = "REVISES"
    SUPERSEDES = "SUPERSEDES"
    CORRECTS = "CORRECTS"
    RETRACTS = "RETRACTS"
    FORMAL_FOLLOW_UP_TO = "FORMAL_FOLLOW_UP_TO"
    IMPLEMENTS = "IMPLEMENTS"
    OFFICIALLY_RESPONDS_TO = "OFFICIALLY_RESPONDS_TO"

    # Entity-to-Entity Foundational Structure Predicates (for multi-hop traversals)
    SUBSIDIARY_OF = "SUBSIDIARY_OF"
    PARENT_OF = "PARENT_OF"
    ISSUED_BY_COMPANY = "ISSUED_BY_COMPANY"
    OPERATED_BY = "OPERATED_BY"
    LOCATED_IN = "LOCATED_IN"
    PRIMARY_EXCHANGE_IN = "PRIMARY_EXCHANGE_IN"
    COMPRISING_SECTOR = "COMPRISING_SECTOR"


class RelationshipOrigin(str, Enum):
    """Assertion origin for graph edges."""
    OFFICIAL_DISCLOSURE = "OFFICIAL_DISCLOSURE"
    REGULATORY_FILING = "REGULATORY_FILING"
    GOVERNMENT_ACTION = "GOVERNMENT_ACTION"
    STATISTICAL_AGENCY = "STATISTICAL_AGENCY"
    CENTRAL_BANK_RELEASE = "CENTRAL_BANK_RELEASE"
    NEWS_REPORT = "NEWS_REPORT"
    GEOSPATIAL_CALCULATION = "GEOSPATIAL_CALCULATION"
    HUMAN_ANALYST = "HUMAN_ANALYST"
    AUTOMATED_LINKER = "AUTOMATED_LINKER"


class RelationshipVerificationStatus(str, Enum):
    """Institutional verification state for knowledge graph edges."""
    VERIFIED_DIRECT = "VERIFIED_DIRECT"
    SOURCE_SUPPORTED = "SOURCE_SUPPORTED"
    CORROBORATED = "CORROBORATED"
    CANDIDATE = "CANDIDATE"
    CONFLICTED = "CONFLICTED"
    REJECTED = "REJECTED"
    REVOKED = "REVOKED"


class CanonicalGraphNodeRef(BaseModel):
    """Reference to a canonical node within the ATLAS knowledge graph."""
    node_type: GraphNodeType
    entity_id: str
    canonical_name: str
    identifier_map: Dict[str, str] = Field(default_factory=dict)
    country_code: Optional[str] = None
    sector: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: Optional[str] = None

    @property
    def node_key(self) -> str:
        """Composite unique key for adjacency lookups."""
        return f"{self.node_type.value}:{self.entity_id}"


class AtlasEventEntityRelationship(BaseModel):
    """Institutional canonical relationship edge connecting an event to an entity,
    or linking entities through verified foundational registries.
    """
    relationship_id: str
    event_id: str
    event_revision_id: Optional[str] = None
    source_node: CanonicalGraphNodeRef
    target_node: CanonicalGraphNodeRef
    predicate: PredicateType
    relationship_role: Optional[str] = None
    assertion_origin: RelationshipOrigin
    verification_status: RelationshipVerificationStatus = RelationshipVerificationStatus.SOURCE_SUPPORTED
    temporal_valid_from: Optional[datetime] = None
    temporal_valid_to: Optional[datetime] = None
    knowledge_available_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_ids: List[str] = Field(default_factory=list)
    derivation_method: str = "DIRECT_EXTRACTED"
    proximity_metadata: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: Optional[str] = None
    is_revoked: bool = False
    revocation_reason: Optional[str] = None


class EventEntityRelationshipRevision(BaseModel):
    """Non-destructive historical revision audit entry for graph relationships."""
    revision_id: str
    relationship_id: str
    revision_number: int
    changed_fields: Dict[str, Any]
    reason: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphPathHop(BaseModel):
    """A single verified step along a multi-hop graph path."""
    hop_number: int
    from_node: CanonicalGraphNodeRef
    to_node: CanonicalGraphNodeRef
    predicate: PredicateType
    relationship_id: str
    verification_status: RelationshipVerificationStatus
    evidence_ids: List[str] = Field(default_factory=list)
    temporal_valid_from: Optional[datetime] = None
    temporal_valid_to: Optional[datetime] = None
    explanation: str


class GraphPath(BaseModel):
    """A verified path connecting two nodes with factual explanations and zero speculative leaps."""
    path_id: str
    source_node: CanonicalGraphNodeRef
    target_node: CanonicalGraphNodeRef
    hops: List[GraphPathHop]
    total_hops: int
    factual_explanation: str
