import type React from "react";

export type BottomPanelId =
  | "tasks"
  | "agents"
  | "jobs"
  | "alerts"
  | "downloads"
  | "system-health"
  | "terminal";

export type BottomPanelPlacement = "primary" | "trailing";
export type BottomPanelAvailability = "available" | "reserved";

export interface BottomPanelDefinition {
  id: BottomPanelId;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  placement: BottomPanelPlacement;
  availability: BottomPanelAvailability;
  component: React.ComponentType;
}

export interface BottomPanelState {
  activePanelId: BottomPanelId | null;
  isOpen: boolean;
  panelHeight: number;
}

export interface BottomPanelController {
  activePanelId: BottomPanelId | null;
  isOpen: boolean;
  panelHeight: number;
  openPanel: (id: BottomPanelId) => void;
  closePanel: () => void;
  togglePanel: (id: BottomPanelId) => void;
  setPanelHeight: (height: number) => void;
}
