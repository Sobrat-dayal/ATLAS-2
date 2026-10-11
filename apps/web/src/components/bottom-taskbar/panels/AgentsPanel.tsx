"use client";

import React from "react";
import { Bot } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function AgentsPanel() {
  return (
    <ReservedPanelState
      title="Agents"
      icon={Bot}
      description="Agent execution details, operational runs, and autonomous team status will appear here when the ATLAS Agent runtime is available."
      details="Status: Runtime not connected | Active Agents: None | Team Execution: Reserved"
      actionLink={{
        label: "Open Agents Module",
        href: "/agents",
      }}
      notice="The right Agent Dock provides quick shortcuts, while this workspace panel will host detailed logs and team runs (Stage 146+)."
    />
  );
}
