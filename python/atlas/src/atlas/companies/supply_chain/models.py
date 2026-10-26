"""Domain Models and Dataclasses for Company Supply Chain Intelligence (Stage 88)."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from .enums import (
    ConcentrationScope,
    EntityKind,
    RelationshipLifecycleStatus,
    SupplyChainRelationshipType,
    VerificationStatus,
)


@dataclass
class RelationshipEvidence:
    """Verifiable supporting source evidence citation for a commercial relationship."""

    evidence_id: str
    source_filing_ref: str
    source_provider: str = "SEC_EDGAR"
    source_document_id: Optional[str] = None
    section_anchor: Optional[str] = None
    excerpt: str = ""
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    review_status: str = "VERIFIED_AUDITED"


@dataclass
class SupplyChainRelationship:
    """Canonical directed commercial relationship (Supplier -> Customer)."""

    relationship_id: str
    supplier_entity_id: str
    customer_entity_id: str
    relationship_type: SupplyChainRelationshipType
    supplied_item_type: str
    supplied_item_description: str
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    lifecycle_status: RelationshipLifecycleStatus = RelationshipLifecycleStatus.ACTIVE_CONFIRMED
    tier: int = 1
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    reported_as_of: str = "2024-09-28"
    revenue_exposure_pct: Optional[Decimal] = None
    spend_exposure_pct: Optional[Decimal] = None
    is_critical: bool = False
    evidence: List[RelationshipEvidence] = field(default_factory=list)


@dataclass
class SupplyChainNode:
    """Node representation in a directed corporate supply chain graph."""

    entity_id: str
    name: str
    ticker: Optional[str] = None
    entity_kind: EntityKind = EntityKind.PUBLIC_COMPANY
    country: str = "United States"
    sector: Optional[str] = None
    industry: Optional[str] = None
    tier: int = 1
    is_subject: bool = False


@dataclass
class SupplyChainEdge:
    """Directed edge in a corporate supply chain network visualization."""

    relationship_id: str
    source_entity_id: str  # Supplier
    target_entity_id: str  # Customer
    relationship_type: SupplyChainRelationshipType
    product_context: str
    verification_status: VerificationStatus
    lifecycle_status: RelationshipLifecycleStatus
    tier: int
    evidence_count: int
    reported_as_of: str


@dataclass
class ConcentrationObservation:
    """Disclosed customer revenue or supplier spend dependency observation."""

    observation_id: str
    subject_company_id: str
    counterparty_name: str
    scope: ConcentrationScope
    period_id: str
    counterparty_entity_id: Optional[str] = None
    is_anonymous: bool = False
    reported_percentage: Optional[Decimal] = None
    formatted_percentage: str = "N/A"
    revenue_amount: Optional[Decimal] = None
    formatted_amount: Optional[str] = None
    currency: str = "USD"
    source_filing_ref: str = "Form 10-K, Item 1"
    notes: Optional[str] = None


@dataclass
class HistoricalRelationshipEvent:
    """Verifiable historical milestone or contract change in a commercial relationship."""

    event_id: str
    relationship_id: str
    event_date: str
    event_type: str
    description: str
    source_ref: str
