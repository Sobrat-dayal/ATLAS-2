"use client";

import React from "react";
import { BellRing } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function AlertsPanel() {
  return (
    <ReservedPanelState
      title="Alerts"
      icon={BellRing}
      description="Alert monitoring and condition rules will appear here when ATLAS alert services are connected. No alert source is connected."
      details="Status: Rule engine not connected | Active Rules: None | Trigger History: Reserved"
      notice="Alerts define trigger conditions and monitoring rules (price, risk, watchlist). Delivered user messages are managed in the TopBar Notification Center (Stage 49)."
    />
  );
}
