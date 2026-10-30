/**
 * Client Capability Registry for ATLAS Stage 121: Global Workspace Linking.
 */

import { ContextDimension, PanelContextCapability } from "./types";

export const PANEL_CAPABILITIES: Record<string, PanelContextCapability> = {
  MARKET_OVERVIEW: {
    panel_type_id: "MARKET_OVERVIEW",
    publishable_dimensions: ["INSTRUMENT"],
    subscribable_dimensions: ["REPORTING_CURRENCY"],
    accepted_entity_types: ["INSTRUMENT", "CURRENCY"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: true,
  },
  INSTRUMENT_CHART: {
    panel_type_id: "INSTRUMENT_CHART",
    publishable_dimensions: ["INSTRUMENT", "TIMEFRAME", "DATE_RANGE"],
    subscribable_dimensions: [
      "INSTRUMENT",
      "TIMEFRAME",
      "DATE_RANGE",
      "AS_OF_DATE",
      "REPORTING_CURRENCY",
    ],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: {
      COMPANY: "PRIMARY_LISTING",
      OPTION: "UNDERLYING",
    },
    supported_timeframes: ["1m", "5m", "15m", "1h", "1D", "1W", "1M", "1Y"],
    supports_as_of: true,
    supports_currency: true,
  },
  WATCHLIST: {
    panel_type_id: "WATCHLIST",
    publishable_dimensions: ["INSTRUMENT", "COMPANY"],
    subscribable_dimensions: [],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
  SCREENER: {
    panel_type_id: "SCREENER",
    publishable_dimensions: ["INSTRUMENT", "COMPANY"],
    subscribable_dimensions: [],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
  COMPANY_OVERVIEW: {
    panel_type_id: "COMPANY_OVERVIEW",
    publishable_dimensions: ["COMPANY"],
    subscribable_dimensions: ["COMPANY", "INSTRUMENT", "REPORTING_CURRENCY"],
    accepted_entity_types: ["COMPANY", "INSTRUMENT"],
    required_transformations: {
      INSTRUMENT: "COMPANY",
    },
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: true,
  },
  ECONOMIC_SERIES: {
    panel_type_id: "ECONOMIC_SERIES",
    publishable_dimensions: ["ECONOMIC_SERIES", "DATE_RANGE"],
    subscribable_dimensions: ["ECONOMIC_SERIES", "DATE_RANGE", "REGION"],
    accepted_entity_types: ["ECONOMIC_SERIES"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: true,
    supports_currency: false,
  },
  NEWS_FEED: {
    panel_type_id: "NEWS_FEED",
    publishable_dimensions: [],
    subscribable_dimensions: ["INSTRUMENT", "COMPANY", "REGION"],
    accepted_entity_types: ["INSTRUMENT", "COMPANY"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
  RESEARCH_DOCUMENT: {
    panel_type_id: "RESEARCH_DOCUMENT",
    publishable_dimensions: [],
    subscribable_dimensions: ["INSTRUMENT", "COMPANY"],
    accepted_entity_types: ["INSTRUMENT", "COMPANY"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
  RESEARCH_REPORT: {
    panel_type_id: "RESEARCH_REPORT",
    publishable_dimensions: [],
    subscribable_dimensions: ["INSTRUMENT", "COMPANY"],
    accepted_entity_types: ["INSTRUMENT", "COMPANY"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
  PORTFOLIO_SUMMARY: {
    panel_type_id: "PORTFOLIO_SUMMARY",
    publishable_dimensions: ["PORTFOLIO", "INSTRUMENT"],
    subscribable_dimensions: ["PORTFOLIO", "REPORTING_CURRENCY"],
    accepted_entity_types: ["PORTFOLIO"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: true,
  },
  PORTFOLIO_PERFORMANCE: {
    panel_type_id: "PORTFOLIO_PERFORMANCE",
    publishable_dimensions: [],
    subscribable_dimensions: [
      "PORTFOLIO",
      "BENCHMARK",
      "DATE_RANGE",
      "REPORTING_CURRENCY",
    ],
    accepted_entity_types: ["PORTFOLIO", "BENCHMARK"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: true,
    supports_currency: true,
  },
  RISK_OVERVIEW: {
    panel_type_id: "RISK_OVERVIEW",
    publishable_dimensions: [],
    subscribable_dimensions: [
      "PORTFOLIO",
      "BENCHMARK",
      "AS_OF_DATE",
      "REPORTING_CURRENCY",
    ],
    accepted_entity_types: ["PORTFOLIO"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: true,
    supports_currency: true,
  },
  RISK_ANALYSIS: {
    panel_type_id: "RISK_ANALYSIS",
    publishable_dimensions: [],
    subscribable_dimensions: [
      "PORTFOLIO",
      "BENCHMARK",
      "AS_OF_DATE",
      "REPORTING_CURRENCY",
    ],
    accepted_entity_types: ["PORTFOLIO"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: true,
    supports_currency: true,
  },
  DATA_TABLE: {
    panel_type_id: "DATA_TABLE",
    publishable_dimensions: ["INSTRUMENT"],
    subscribable_dimensions: ["INSTRUMENT", "DATE_RANGE", "REPORTING_CURRENCY"],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: true,
  },
  OPTIONS_ANALYTICS: {
    panel_type_id: "OPTIONS_ANALYTICS",
    publishable_dimensions: ["INSTRUMENT"],
    subscribable_dimensions: ["INSTRUMENT", "TIMEFRAME"],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: { OPTION: "UNDERLYING" },
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: true,
  },
  MAP_VIEW: {
    panel_type_id: "MAP_VIEW",
    publishable_dimensions: ["REGION", "INSTRUMENT"],
    subscribable_dimensions: ["REGION", "INSTRUMENT"],
    accepted_entity_types: ["INSTRUMENT"],
    required_transformations: {},
    supported_timeframes: [],
    supports_as_of: false,
    supports_currency: false,
  },
};

export function getPanelCapability(panelTypeId: string): PanelContextCapability | undefined {
  return PANEL_CAPABILITIES[panelTypeId];
}

export function isDimensionSubscribable(
  panelTypeId: string,
  dimension: ContextDimension
): boolean {
  const cap = getPanelCapability(panelTypeId);
  return cap ? cap.subscribable_dimensions.includes(dimension) : false;
}

export function isDimensionPublishable(
  panelTypeId: string,
  dimension: ContextDimension
): boolean {
  const cap = getPanelCapability(panelTypeId);
  return cap ? cap.publishable_dimensions.includes(dimension) : false;
}

