"""Domain Definitions for ATLAS INTELLIGENCE V1 (Stage 138).

Institutional-grade typed models for:
- Intelligence Views & Information Architecture
- Coordinated Investigation Contexts & Presets
- Section Statuses & Partial Result Representation
- Source Freshness, Coverage & Health Manifests
- Unified Search Results with Canonical Disambiguation
- Multi-Panel Intelligence Workspaces & Global Linking
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from atlas.event_graph.domain import CanonicalGraphNodeRef, GraphNodeType
from atlas.events.domain import EventCategory, EventVerificationStatus


class IntelligenceViewType(str, Enum):
    """Primary operational views within the /intelligence route."""
    OVERVIEW = "OVERVIEW"
    EVENTS = "EVENTS"
    ENTITIES = "ENTITIES"
    GRAPH = "GRAPH"
    EXPOSURE = "EXPOSURE"
    GEOGRAPHY = "GEOGRAPHY"
    INVESTIGATIONS = "INVESTIGATIONS"
    HISTORY = "HISTORY"
    SOURCES = "SOURCES"


class SectionStatus(str, Enum):
    """Operational availability status for aggregated intelligence sections."""
    READY = "READY"
    EMPTY = "EMPTY"
    PARTIAL = "PARTIAL"
    STALE = "STALE"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    ACCESS_DENIED = "ACCESS_DENIED"
    FAILED = "FAILED"


class IntelligencePanelType(str, Enum):
    """Institutional panel types registered for multi-panel intelligence workspaces."""
    EVENT_MONITOR = "EVENT_MONITOR"
    EVENT_INSPECTOR = "EVENT_INSPECTOR"
    ENTITY_CONTEXT = "ENTITY_CONTEXT"
    ENTITY_GRAPH = "ENTITY_GRAPH"
    EXPOSURE_SUMMARY = "EXPOSURE_SUMMARY"
    EXPOSURE_INSPECTOR = "EXPOSURE_INSPECTOR"
    GEOGRAPHY_MAP = "GEOGRAPHY_MAP"
    RESEARCH_EVIDENCE = "RESEARCH_EVIDENCE"
    SOURCE_INSPECTOR = "SOURCE_INSPECTOR"
    COVERAGE_PANEL = "COVERAGE_PANEL"


class IntelligencePanelDefinition(BaseModel):
    """Configuration descriptor for a registered intelligence workspace panel."""
    panel_type: IntelligencePanelType
    title: str
    description: str
    supported_context_types: List[str] = Field(default_factory=list)
    supports_historical_asof: bool = True
    supports_linking: bool = True
    default_width_pct: int = 50
    default_height_pct: int = 50


class SourceFreshnessRecord(BaseModel):
    """Factual telemetry describing underlying dataset freshness and licensing."""
    source_id: str
    source_name: str
    dataset: str
    status: SectionStatus = SectionStatus.READY
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    effective_data_date: Optional[datetime] = None
    coverage_percentage: Optional[Decimal] = None
    verification_supported: bool = True
    historical_supported: bool = True
    licensing_restriction: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class IntelligenceSearchResult(BaseModel):
    """Disambiguated search hit across events, entities, and sources."""
    result_type: str  # "EVENT", "ENTITY", "SOURCE", "RESEARCH_DOCUMENT"
    entity_type: Optional[GraphNodeType] = None
    canonical_id: str
    display_title: str
    disambiguation: str
    source_reference: Optional[str] = None
    timestamp: Optional[datetime] = None
    verification_status: Optional[str] = None
    is_entitled: bool = True


class IntelligenceInvestigationContext(BaseModel):
    """Typed context object shared across coordinated intelligence panels."""
    context_id: str
    selected_event_id: Optional[str] = None
    selected_entity_ref: Optional[CanonicalGraphNodeRef] = None
    selected_portfolio_id: Optional[str] = None
    selected_relationship_id: Optional[str] = None
    selected_exposure_run_id: Optional[str] = None
    selected_source_id: Optional[str] = None
    geographic_scope: Optional[Dict[str, Any]] = None
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid_at: Optional[datetime] = None
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: Optional[str] = None


class IntelligenceInvestigationPreset(BaseModel):
    """Pre-configured functional multi-panel layout preset."""
    preset_id: str
    name: str
    description: str
    panels: List[IntelligencePanelType]
    linking_channels: List[str] = Field(default_factory=list)


class IntelligenceSavedInvestigation(BaseModel):
    """Persisted structured investigation record for repeatable institutional research."""
    investigation_id: str
    title: str
    description: Optional[str] = None
    owner_id: str
    tenant_id: Optional[str] = None
    primary_subject: Optional[str] = None
    context: IntelligenceInvestigationContext
    preset_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntelligenceOverviewSection(BaseModel):
    """Component block within the unified Overview command center."""
    section_id: str
    title: str
    status: SectionStatus = SectionStatus.READY
    items_count: int = 0
    data: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntelligenceOverviewResponse(BaseModel):
    """Master response payload for the Intelligence Overview."""
    overview_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    known_as_of: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sections: Dict[str, IntelligenceOverviewSection] = Field(default_factory=dict)
    source_freshness: List[SourceFreshnessRecord] = Field(default_factory=list)
    active_warnings: List[str] = Field(default_factory=list)
    tenant_id: Optional[str] = None
