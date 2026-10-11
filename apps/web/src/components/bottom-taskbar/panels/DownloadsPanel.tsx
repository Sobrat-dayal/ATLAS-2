"use client";

import React from "react";
import { Download } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function DownloadsPanel() {
  return (
    <ReservedPanelState
      title="Downloads"
      icon={Download}
      description="Generated reports, dataset exports, and download tracking will appear here when download services are available. No download tracking is available."
      details="Status: Download tracker not connected | Active Downloads: None | Artifacts: Reserved"
      notice="Browser downloads are not intercepted. Stage 50 provides the hosting workspace shell."
    />
  );
}
