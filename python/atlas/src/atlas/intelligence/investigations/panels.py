"""Intelligence Panel Capabilities & Registry for ATLAS INTELLIGENCE V1 (Stage 138)."""

from typing import Dict, List
from atlas.intelligence.domain import (
    IntelligencePanelDefinition,
    IntelligencePanelType,
)

PANEL_REGISTRY: Dict[IntelligencePanelType, IntelligencePanelDefinition] = {
    IntelligencePanelType.EVENT_MONITOR: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.EVENT_MONITOR,
        title="Event Monitor & Timeline",
        description="Source-backed financial, economic, and physical event stream with multi-clock temporal filters.",
        supported_context_types=["selected_event_id", "time_window", "known_as_of"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.EVENT_INSPECTOR: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.EVENT_INSPECTOR,
        title="Event Detail Inspector",
        description="Deep inspection of canonical claims, revisions, retractions, and primary source citations.",
        supported_context_types=["selected_event_id"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.ENTITY_CONTEXT: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.ENTITY_CONTEXT,
        title="Entity Intelligence Context",
        description="Canonical entity metadata, official identifiers, sector classifications, and associated events.",
        supported_context_types=["selected_entity_ref", "known_as_of"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.ENTITY_GRAPH: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.ENTITY_GRAPH,
        title="Event-to-Entity Knowledge Graph",
        description="Stage 136 interactive relationship topology, bounded path expansions, and verification states.",
        supported_context_types=["selected_event_id", "selected_entity_ref", "known_as_of"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.EXPOSURE_SUMMARY: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.EXPOSURE_SUMMARY,
        title="Financial Exposure Summary",
        description="Stage 137 quantitative exposure calculations, net/gross footprints, and unallocated residuals.",
        supported_context_types=["selected_entity_ref", "selected_portfolio_id", "selected_event_id"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.EXPOSURE_INSPECTOR: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.EXPOSURE_INSPECTOR,
        title="Exposure Lineage & Quality Inspector",
        description="Exact numerator/denominator breakdown, point-in-time rates, and mathematical audit trail.",
        supported_context_types=["selected_exposure_run_id"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.GEOGRAPHY_MAP: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.GEOGRAPHY_MAP,
        title="Geographic Intelligence Map",
        description="Interactive 2D/3D map displaying physical events, corporate facilities, and infrastructure proximity.",
        supported_context_types=["selected_event_id", "geographic_scope"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.RESEARCH_EVIDENCE: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.RESEARCH_EVIDENCE,
        title="Source-Backed Research & Evidence",
        description="Stage 127 verified filings, press releases, regulatory transcripts, and source grounding.",
        supported_context_types=["selected_event_id", "selected_source_id"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.SOURCE_INSPECTOR: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.SOURCE_INSPECTOR,
        title="Data Freshness & Source Inspector",
        description="Dataset health telemetry, effective dates, provider entitlements, and conflict resolution logs.",
        supported_context_types=["selected_source_id"],
        supports_historical_asof=False,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    ),
    IntelligencePanelType.COVERAGE_PANEL: IntelligencePanelDefinition(
        panel_type=IntelligencePanelType.COVERAGE_PANEL,
        title="Data Coverage & Residuals",
        description="Explicit breakdown of measured population vs unallocated residuals without artificial scaling.",
        supported_context_types=["selected_exposure_run_id"],
        supports_historical_asof=True,
        supports_linking=True,
        default_width_pct=50,
        default_height_pct=50
    )
}


def list_panel_definitions() -> List[IntelligencePanelDefinition]:
    """Return all registered intelligence panel definitions."""
    return list(PANEL_REGISTRY.values())

