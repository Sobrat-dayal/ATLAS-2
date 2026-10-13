import type { ComponentType } from "react";
import { AtlasModuleId } from "@/config/atlas-modules";

export type HomeWidgetId =
  | "current-context"
  | "quick-launch"
  | "home-market-summary"
  | "home-personalized-activity"
  | "home-tasks-approvals"
  | "home-intelligence-feed"
  | "home-portfolio-summary"
  | "home-news-preview"
  | "home-economics-preview"
  | "home-map-preview"
  | "home-agent-activity";

export type HomeWidgetState =
  | "available"
  | "loading"
  | "empty"
  | "error"
  | "reserved"
  | "unavailable";

export type HomeWidgetPlacement =
  | "primary"
  | "secondary"
  | "tertiary"
  | "full";

export interface HomeWidgetDefinition {
  id: HomeWidgetId;
  title: string;
  subtitle?: string;
  description: string;
  targetStage: number;
  status: "implemented" | "reserved" | "planned";
  defaultState: HomeWidgetState;
  placement: HomeWidgetPlacement;
  minimumWidth?: number;
  requiredPermission?: string;
}

export interface QuickLaunchItem {
  id: AtlasModuleId;
  label: string;
  route: string;
  icon: ComponentType<{ className?: string; "aria-hidden"?: boolean | "true" | "false" }>;
  description: string;
  order: number;
  isPrimary: boolean;
  requiredPermission: string;
}
