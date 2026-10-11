"use client";

import React from "react";
import { Layers } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function JobsPanel() {
  return (
    <ReservedPanelState
      title="Jobs"
      icon={Layers}
      description="Background jobs, data ingestion tasks, and worker processing will appear here when ATLAS job services are connected. No job source is connected."
      details="Status: Job queue not exposed | Queued: 0 | Running: 0 | History: Reserved"
      notice="Market data ingestion workers run as backend processes; user-facing job management endpoints are not exposed in this stage."
    />
  );
}
