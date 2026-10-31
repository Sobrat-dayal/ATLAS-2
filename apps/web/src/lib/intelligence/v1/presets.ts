import { IntelligenceInvestigationPreset } from "./types";

export const CLIENT_INVESTIGATION_PRESETS: Record<string, IntelligenceInvestigationPreset> = {
  preset_event_investigation: {
    preset_id: "preset_event_investigation",
    name: "Event Investigation",
    description: "Source-backed investigation of verified events, linked entities, knowledge graph, and evidence.",
    panels: ["EVENT_MONITOR", "EVENT_INSPECTOR", "ENTITY_GRAPH", "RESEARCH_EVIDENCE"],
    linking_channels: ["selected_event_id", "selected_entity_ref"]
  },
  preset_company_intelligence: {
    preset_id: "preset_company_intelligence",
    name: "Company Intelligence",
    description: "Company context, related events, knowledge graph topology, and documented exposure.",
    panels: ["ENTITY_CONTEXT", "EVENT_MONITOR", "ENTITY_GRAPH", "EXPOSURE_SUMMARY"],
    linking_channels: ["selected_entity_ref"]
  },
  preset_economic_decision: {
    preset_id: "preset_economic_decision",
    name: "Economic Decision Analysis",
    description: "Central bank and macroeconomic announcements, indicator series, and policy jurisdictions.",
    panels: ["EVENT_MONITOR", "EVENT_INSPECTOR", "RESEARCH_EVIDENCE", "SOURCE_INSPECTOR"],
    linking_channels: ["selected_event_id", "time_window"]
  },
  preset_geographic_investigation: {
    preset_id: "preset_geographic_investigation",
    name: "Geographic Event Investigation",
    description: "Physical events (earthquakes, wildfires, weather), corporate facilities, and infrastructure proximity.",
    panels: ["GEOGRAPHY_MAP", "EVENT_MONITOR", "ENTITY_CONTEXT", "SOURCE_INSPECTOR"],
    linking_channels: ["selected_event_id", "geographic_scope"]
  },
  preset_portfolio_exposure: {
    preset_id: "preset_portfolio_exposure",
    name: "Portfolio Event Exposure",
    description: "Authorized portfolio holdings look-through, directly associated events, and documented exposure.",
    panels: ["EXPOSURE_SUMMARY", "EVENT_MONITOR", "EXPOSURE_INSPECTOR", "ENTITY_GRAPH"],
    linking_channels: ["selected_portfolio_id", "selected_event_id"]
  }
};

