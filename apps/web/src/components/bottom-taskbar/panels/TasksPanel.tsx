"use client";

import React from "react";
import { CheckSquare } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function TasksPanel() {
  return (
    <ReservedPanelState
      title="Tasks"
      icon={CheckSquare}
      description="Task management will appear here when ATLAS task services are connected. No task source is connected."
      details="Status: No active task source | Execution: Reserved | Approvals: Reserved"
      notice="Task execution, scheduling, approvals, and history are reserved for Stage 54+. Stage 50 provides the hosting shell."
    />
  );
}
