"""Canonical Investigation Presets for ATLAS INTELLIGENCE V1 (Stage 138).

Pre-configured institutional multi-panel layouts mapping directly to Stage 120 Workspaces:
- Event Investigation
- Company Intelligence
- Economic Decision Analysis
- Geographic Event Investigation
- Portfolio Event Exposure
"""

from typing import Dict, List
from atlas.intelligence.domain import (
    IntelligenceInvestigationPreset,
    IntelligencePanelType,
)

CANONICAL_INVESTIGATION_PRESETS: Dict[str, IntelligenceInvestigationPreset] = {
    "preset_event_investigation": IntelligenceInvestigationPreset(
        preset_id="preset_event_investigation",
        name="Event Investigation",
        description="Source-backed investigation of verified events, linked entities, knowledge graph, and evidence.",
        panels=[
            IntelligencePanelType.EVENT_MONITOR,
            IntelligencePanelType.EVENT_INSPECTOR,
            IntelligencePanelType.ENTITY_GRAPH,
            IntelligencePanelType.RESEARCH_EVIDENCE,
        ],
        linking_channels=["selected_event_id", "selected_entity_ref"]
    ),
    "preset_company_intelligence": IntelligenceInvestigationPreset(
        preset_id="preset_company_intelligence",
        name="Company Intelligence",
        description="Company context, related events, knowledge graph topology, and documented exposure.",
        panels=[
            IntelligencePanelType.ENTITY_CONTEXT,
            IntelligencePanelType.EVENT_MONITOR,
            IntelligencePanelType.ENTITY_GRAPH,
            IntelligencePanelType.EXPOSURE_SUMMARY,
        ],
        linking_channels=["selected_entity_ref"]
    ),
    "preset_economic_decision": IntelligenceInvestigationPreset(
        preset_id="preset_economic_decision",
        name="Economic Decision Analysis",
        description="Central bank and macroeconomic announcements, indicator series, and policy jurisdictions.",
        panels=[
            IntelligencePanelType.EVENT_MONITOR,
            IntelligencePanelType.EVENT_INSPECTOR,
            IntelligencePanelType.RESEARCH_EVIDENCE,
            IntelligencePanelType.SOURCE_INSPECTOR,
        ],
        linking_channels=["selected_event_id", "time_window"]
    ),
    "preset_geographic_investigation": IntelligenceInvestigationPreset(
        preset_id="preset_geographic_investigation",
        name="Geographic Event Investigation",
        description="Physical events (earthquakes, wildfires, weather), corporate facilities, and infrastructure proximity.",
        panels=[
            IntelligencePanelType.GEOGRAPHY_MAP,
            IntelligencePanelType.EVENT_MONITOR,
            IntelligencePanelType.ENTITY_CONTEXT,
            IntelligencePanelType.SOURCE_INSPECTOR,
        ],
        linking_channels=["selected_event_id", "geographic_scope"]
    ),
    "preset_portfolio_exposure": IntelligenceInvestigationPreset(
        preset_id="preset_portfolio_exposure",
        name="Portfolio Event Exposure",
        description="Authorized portfolio holdings look-through, directly associated events, and documented exposure.",
        panels=[
            IntelligencePanelType.EXPOSURE_SUMMARY,
            IntelligencePanelType.EVENT_MONITOR,
            IntelligencePanelType.EXPOSURE_INSPECTOR,
            IntelligencePanelType.ENTITY_GRAPH,
        ],
        linking_channels=["selected_portfolio_id", "selected_event_id"]
    ),
}


def list_investigation_presets() -> List[IntelligenceInvestigationPreset]:
    """Return all canonical investigation presets."""
    return list(CANONICAL_INVESTIGATION_PRESETS.values())


def get_investigation_preset(preset_id: str) -> IntelligenceInvestigationPreset:
    """Retrieve preset by ID or raise KeyError."""
    if preset_id not in CANONICAL_INVESTIGATION_PRESETS:
        raise KeyError(f"Investigation preset '{preset_id}' not found.")
    return CANONICAL_INVESTIGATION_PRESETS[preset_id]

