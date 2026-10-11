"use client";

import React from "react";
import { Terminal } from "lucide-react";
import { ReservedPanelState } from "../ReservedPanelState";

export function TerminalPanel() {
  return (
    <ReservedPanelState
      title="Terminal"
      icon={Terminal}
      description="The sandboxed ATLAS Terminal shell will be available in Stage 122. Terminal command input, interactive shell sessions, and execution are not available in this stage."
      details="Status: Launcher reserved | Session: None | Terminal Engine: Stage 122"
      notice="No shell prompt, command history, xterm.js, or subprocess execution is active in Stage 50."
    />
  );
}
