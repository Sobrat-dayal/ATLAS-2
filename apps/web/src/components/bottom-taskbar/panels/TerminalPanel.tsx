"use client";

import React from "react";
import { useBottomPanel } from "@/hooks/bottom-taskbar";
import { TerminalDrawer } from "@/components/terminal/TerminalDrawer";

export function TerminalPanel() {
  const { closePanel } = useBottomPanel();

  return (
    <div className="h-full w-full flex flex-col bg-atlas-surface-0">
      <TerminalDrawer onClose={closePanel} />
    </div>
  );
}
