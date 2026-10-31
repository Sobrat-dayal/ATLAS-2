"""Domain models for ATLAS God's Eye Financial Intelligence (Stage 140).

Defines canonical types for:
- 8 Investigation Lenses
- 2D/3D Geographic & Situational Models
- Bitemporal Context & Point-in-time constraints
- Bounded Cross-Domain Payloads
- Explicit Institutional Disclaimers (Causality, Damage, Exposure, Priority, Trading)
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GodsEyeLensType(str, Enum):
    """The 8 canonical investigation lenses for God's Eye Financial Intelligence."""
    GLOBAL_EVENTS = "GLOBAL_EVENTS"
    MONETARY_POLICY = "MONETARY_POLICY"
    CORPORATE_INTELLIGENCE = "CORPORATE_INTELLIGENCE"
    GEOPOLITICAL = "GEOPOLITICAL"
    COMMODITY_INFRASTRUCTURE = "COMMODITY_INFRASTRUCTURE"
    PHYSICAL_WORLD = "PHYSICAL_WORLD"
    PORTFOLIO_INTELLIGENCE = "PORTFOLIO_INTELLIGENCE"
    HISTORICAL_RESEARCH = "HISTORICAL_RESEARCH"


class GodsEyeViewMode(str, Enum):
    """Spatial visualization mode for the situational canvas."""
    TWO_DIMENSIONAL = "TWO_DIMENSIONAL"
    THREE_DIMENSIONAL_GLOBE = "THREE_DIMENSIONAL_GLOBE"
    HYBRID_SPLIT = "HYBRID_SPLIT"


class GodsEyeDamageAssessmentStatus(str, Enum):
    """Institutional damage assessment tier; never assumed from proximity alone."""
    UNKNOWN = "UNKNOWN"
    CONFIRMED_OPERATIONAL = "CONFIRMED_OPERATIONAL"
    REPORTED_DISRUPTED = "REPORTED_DISRUPTED"
    CONFIRMED_DAMAGED = "CONFIRMED_DAMAGED"
    DESTROYED = "DESTROYED"


class GodsEyeSectionStatus(str, Enum):
    """Execution status for sub-domains within the unified query plan."""
    READY = "READY"
    DEGRADED = "DEGRADED"
    EMPTY = "EMPTY"
    RESTRICTED = "RESTRICTED"
    ERROR = "ERROR"


# Canonical Institutional Disclaimers
INSTITUTIONAL_DISCLAIMERS: Dict[str, str] = {
    "causality": "Correlation is not causation. Co-occurrence or temporal proximity between an event and market move is observational and does not establish causal transmission.",
    "damage": "Spatial proximity to a physical event or natural hazard does not imply confirmed physical damage or operational shutdown. Status is UNKNOWN unless officially reported.",
    "exposure": "Structural exposure quantifies revenue concentration or portfolio look-through weights, not projected monetary loss or default risk.",
    "priority": "Intelligence priority score reflects operational review priority and informational importance, not an investment recommendation or return forecast.",
    "trading": "God's Eye is an analytical research and situational awareness system. No automated order placement, broker routing, or portfolio mutation is performed.",
    "omniscience": "God's Eye provides situational awareness aggregated from licensed, verified, and public sources. It does not possess covert, classified, or omniscient surveillance capabilities.",
}


class MarketContextSnapshot(BaseModel):
    """Observational market movements around an event window without causal attribution."""
    benchmark_symbol: str
    price_before: float
    price_after: float
    pct_change: float
    time_window: str
    is_observational_only: bool = True
    disclaimer: str = INSTITUTIONAL_DISCLAIMERS["causality"]


class GodsEyeMapFeature(BaseModel):
    """GeoJSON-compatible spatial feature for facilities, ports, pipelines, or event perimeters."""
    id: str
    feature_type: str  # "FACILITY", "PORT", "PIPELINE", "HAZARD_PERIMETER", "EVENT_EPICENTER", "CORPORATE_HQ"
    name: str
    coordinates: List[float]  # [longitude, latitude] or nested coordinates
    geometry_type: str = "Point"  # "Point", "Polygon", "LineString"
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    verified: bool = True
    damage_status: GodsEyeDamageAssessmentStatus = GodsEyeDamageAssessmentStatus.UNKNOWN


class GodsEyeLensDefinition(BaseModel):
    """Metadata specification for a canonical investigation lens."""
    lens_id: GodsEyeLensType
    label: str
    description: str
    primary_event_categories: List[str]
    default_layers: List[str]
    default_view_mode: GodsEyeViewMode = GodsEyeViewMode.TWO_DIMENSIONAL
    requires_portfolio: bool = False
    supported_graph_predicates: List[str] = Field(default_factory=list)


class GodsEyeContext(BaseModel):
    """Request context configuring the scope of a God's Eye investigation."""
    lens: GodsEyeLensType = GodsEyeLensType.GLOBAL_EVENTS
    as_of: Optional[datetime] = None
    selected_entity_id: Optional[str] = None
    selected_event_id: Optional[str] = None
    selected_portfolio_id: Optional[str] = None
    tenant_id: str = "default"
    user_id: Optional[str] = None
    bounding_box: Optional[List[float]] = None  # [min_lon, min_lat, max_lon, max_lat]
    view_mode: GodsEyeViewMode = GodsEyeViewMode.TWO_DIMENSIONAL
    max_graph_depth: int = 2
    max_entities: int = 50
    scoring_policy_id: Optional[str] = None
    search_query: Optional[str] = None


class GodsEyeHistoricalVintage(BaseModel):
    """Information known and effective strictly as-of a specific point-in-time."""
    vintage_date: datetime
    known_as_of: datetime
    active_corporate_entity: str
    verified_relationship_count: int
    prior_parent_name: Optional[str] = None
    current_parent_name: Optional[str] = None
    disclosures_available_count: int


class GodsEyeInvestigationResult(BaseModel):
    """Unified institutional response object returned by God's Eye."""
    investigation_id: str
    lens: GodsEyeLensType
    as_of: datetime
    is_historical_reconstruction: bool = False
    view_mode: GodsEyeViewMode = GodsEyeViewMode.TWO_DIMENSIONAL
    events: List[Dict[str, Any]] = Field(default_factory=list)
    map_features: List[GodsEyeMapFeature] = Field(default_factory=list)
    knowledge_graph_subgraph: Dict[str, Any] = Field(default_factory=dict)
    exposure_summary: Optional[Dict[str, Any]] = None
    scoring_summary: Optional[Dict[str, Any]] = None
    market_context: Optional[MarketContextSnapshot] = None
    evidence_sources: List[Dict[str, Any]] = Field(default_factory=list)
    section_statuses: Dict[str, GodsEyeSectionStatus] = Field(default_factory=dict)
    disclaimers: Dict[str, str] = Field(default_factory=lambda: dict(INSTITUTIONAL_DISCLAIMERS))
    coverage_notes: List[str] = Field(default_factory=list)
    telemetry: Dict[str, Any] = Field(default_factory=dict)


class CrossDomainQueryPlan(BaseModel):
    """Execution plan orchestrating bounded fanout across intelligence subsystems."""
    plan_id: str
    lens: GodsEyeLensType
    as_of: datetime
    subsystems: List[str]
    bounded_graph_depth: int
    bounded_max_entities: int
    is_portfolio_authorized: bool = True

