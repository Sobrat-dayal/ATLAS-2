/**
 * Safe Deep Link and Badge Resolvers for Saved Resources.
 */

import { ResourceAvailabilityStatus, SavedModule, SavedTargetType } from "./types";

export function getTargetTypeBadgeVariant(
  targetType: SavedTargetType
): "default" | "outline" | "warning" | "primary" | "positive" | "negative" {
  switch (targetType) {
    case "INSTRUMENT":
    case "COMPANY":
      return "default";
    case "CHART_CONFIG":
    case "SCREENER_CONFIG":
      return "primary";
    case "PORTFOLIO_REFERENCE":
    case "PORTFOLIO_VIEW_CONFIG":
    case "PORTFOLIO_ANALYSIS_RUN":
      return "positive";
    case "RISK_RUN":
    case "RISK_SCENARIO":
      return "warning";
    case "RESEARCH_REPORT":
    case "RESEARCH_INVESTIGATION":
    case "RESEARCH_DOCUMENT":
      return "outline";
    default:
      return "outline";
  }
}

export function getAvailabilityBadgeVariant(
  status: ResourceAvailabilityStatus
): "default" | "outline" | "warning" | "primary" | "positive" | "negative" {
  switch (status) {
    case "AVAILABLE":
      return "positive";
    case "AVAILABLE_WITH_WARNINGS":
    case "TARGET_UPDATED":
      return "warning";
    case "TARGET_SUPERSEDED":
    case "PERMISSION_REVOKED":
    case "SOURCE_RESTRICTED":
      return "outline";
    case "TARGET_DELETED":
    case "TARGET_NOT_FOUND":
    case "RESOURCE_UNAVAILABLE":
    case "UNSUPPORTED_CONFIG_VERSION":
      return "negative";
    default:
      return "default";
  }
}

export function formatTargetTypeLabel(targetType: SavedTargetType): string {
  switch (targetType) {
    case "INSTRUMENT":
      return "Instrument";
    case "COMPANY":
      return "Company";
    case "CHART_CONFIG":
      return "Chart";
    case "SCREENER_CONFIG":
      return "Screener";
    case "WATCHLIST_REFERENCE":
      return "Watchlist";
    case "ECONOMIC_SERIES":
      return "Economics";
    case "NEWS_ARTICLE":
      return "News";
    case "RESEARCH_INVESTIGATION":
      return "Investigation";
    case "RESEARCH_DOCUMENT":
      return "Research Doc";
    case "RESEARCH_REPORT":
      return "Research Report";
    case "RESEARCH_ANALYSIS_RUN":
      return "Research Run";
    case "PORTFOLIO_REFERENCE":
      return "Portfolio";
    case "PORTFOLIO_VIEW_CONFIG":
      return "Portfolio View";
    case "PORTFOLIO_ANALYSIS_RUN":
      return "Portfolio Run";
    case "RISK_RUN":
      return "Risk Run";
    case "RISK_SCENARIO":
      return "Risk Scenario";
    case "MARKET_VIEW_CONFIG":
      return "Market View";
    case "MAP_VIEW_CONFIG":
      return "Map View";
    case "DATA_RESOURCE":
      return "Data Resource";
    case "AI_ARTIFACT":
      return "AI Artifact";
    case "INTELLIGENCE_ARTIFACT":
      return "Intelligence";
    default:
      return targetType;
  }
}
