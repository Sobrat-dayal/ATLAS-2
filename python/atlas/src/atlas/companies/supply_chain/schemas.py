"""Pydantic Request and Response Schemas for Company Supply Chain Intelligence API (Stage 88)."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import (
    ConcentrationScope,
    EntityKind,
    RelationshipLifecycleStatus,
    SupplyChainRelationshipType,
    VerificationStatus,
)


class RelationshipEvidenceDTO(BaseModel):
    """Supporting source evidence citation."""

    evidence_id: str
    source_filing_ref: str
    source_provider: str
    source_document_id: Optional[str] = None
    section_anchor: Optional[str] = None
    excerpt: str
    published_at: datetime
    review_status: str

    model_config = ConfigDict(from_attributes=True)


class SupplyChainRelationshipDTO(BaseModel):
    """Detailed view of a verified commercial relationship."""

    relationship_id: str
    supplier_entity_id: str
    supplier_name: str
    supplier_ticker: Optional[str] = None
    supplier_country: str
    customer_entity_id: str
    customer_name: str
    customer_ticker: Optional[str] = None
    customer_country: str
    relationship_type: SupplyChainRelationshipType
    supplied_item_type: str
    supplied_item_description: str
    verification_status: VerificationStatus
    lifecycle_status: RelationshipLifecycleStatus
    tier: int
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    reported_as_of: str
    revenue_exposure_pct: Optional[Decimal] = None
    formatted_revenue_exposure: Optional[str] = None
    spend_exposure_pct: Optional[Decimal] = None
    is_critical: bool = False
    evidence_count: int
    evidence: List[RelationshipEvidenceDTO] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SupplyChainNodeDTO(BaseModel):
    """Node in corporate network graph."""

    entity_id: str
    name: str
    ticker: Optional[str] = None
    entity_kind: EntityKind
    country: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    tier: int
    is_subject: bool

    model_config = ConfigDict(from_attributes=True)


class SupplyChainEdgeDTO(BaseModel):
    """Directed edge in corporate network graph."""

    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: SupplyChainRelationshipType
    product_context: str
    verification_status: VerificationStatus
    lifecycle_status: RelationshipLifecycleStatus
    tier: int
    evidence_count: int
    reported_as_of: str

    model_config = ConfigDict(from_attributes=True)


class SupplyChainNetworkResponseDTO(BaseModel):
    """Directed corporate network graph response."""

    subject_company_id: str
    total_nodes: int
    total_edges: int
    traversal_depth: int
    nodes: List[SupplyChainNodeDTO]
    edges: List[SupplyChainEdgeDTO]


class ConcentrationObservationDTO(BaseModel):
    """Customer revenue or supplier spend dependency observation."""

    observation_id: str
    subject_company_id: str
    counterparty_name: str
    scope: ConcentrationScope
    period_id: str
    counterparty_entity_id: Optional[str] = None
    is_anonymous: bool = False
    reported_percentage: Optional[Decimal] = None
    formatted_percentage: str
    revenue_amount: Optional[Decimal] = None
    formatted_amount: Optional[str] = None
    currency: str = "USD"
    source_filing_ref: str
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HistoricalRelationshipEventDTO(BaseModel):
    """Historical timeline event."""

    event_id: str
    relationship_id: str
    event_date: str
    event_type: str
    description: str
    source_ref: str

    model_config = ConfigDict(from_attributes=True)


class SupplyChainOverviewResponseDTO(BaseModel):
    """Top-level executive summary for supply chain workspace."""

    subject_company_id: str
    subject_company_name: str
    direct_suppliers_count: int
    direct_customers_count: int
    tier_2_suppliers_count: int
    top_suppliers: List[SupplyChainRelationshipDTO]
    top_customers: List[SupplyChainRelationshipDTO]
    customer_concentration_summary: Optional[str] = None
    supplier_concentration_summary: Optional[str] = None
    key_highlights: Dict[str, str] = Field(default_factory=dict)


class SuppliersListResponseDTO(BaseModel):
    """Paginated list of suppliers."""

    subject_company_id: str
    total_count: int
    items: List[SupplyChainRelationshipDTO]


class CustomersListResponseDTO(BaseModel):
    """Paginated list of customers."""

    subject_company_id: str
    total_count: int
    items: List[SupplyChainRelationshipDTO]


class ConcentrationResponseDTO(BaseModel):
    """Disclosed customer and supplier concentration metrics."""

    subject_company_id: str
    customer_dependencies: List[ConcentrationObservationDTO]
    supplier_dependencies: List[ConcentrationObservationDTO]


class HistoricalTimelineResponseDTO(BaseModel):
    """Historical milestone timeline."""

    subject_company_id: str
    total_events: int
    events: List[HistoricalRelationshipEventDTO]


class SupplyChainCoverageResponseDTO(BaseModel):
    """Disclosure coverage and data quality assessment."""

    subject_company_id: str
    disclosed_suppliers_coverage: str
    disclosed_customers_coverage: str
    primary_sources: List[str]
    data_freshness_as_of: str
    limitations: List[str]
