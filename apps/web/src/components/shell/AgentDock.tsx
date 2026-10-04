"use client";

import { useShellState } from "@/hooks/shell/useShellState";
import { Bot, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

export function AgentDock() {
  const { agentDockOpen, setAgentDockOpen, agentDockWidth, setAgentDockWidth } = useShellState();
  const [isResizing, setIsResizing] = useState(false);
  const dockRef = useRef<HTMLDivElement>(null);

  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (mouseMoveEvent: MouseEvent) => {
      if (isResizing) {
        // Calculate new width: window inner width minus mouse X
        const newWidth = window.innerWidth - mouseMoveEvent.clientX;
        // Constrain width
        if (newWidth >= 220 && newWidth <= 600) {
          setAgentDockWidth(newWidth);
        }
      }
    },
    [isResizing, setAgentDockWidth]
  );

  useEffect(() => {
    window.addEventListener("mousemove", resize);
    window.addEventListener("mouseup", stopResizing);
    return () => {
      window.removeEventListener("mousemove", resize);
      window.removeEventListener("mouseup", stopResizing);
    };
  }, [resize, stopResizing]);

  if (!agentDockOpen) return null;

  return (
    <div
      ref={dockRef}
      style={{ width: `${agentDockWidth}px` }}
      className="relative flex h-full flex-col border-l border-atlas-border-default bg-atlas-surface-1 shrink-0 z-10"
    >
      {/* Resize Handle */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 -translate-x-1/2 cursor-ew-resize hover:bg-atlas-accent opacity-0 hover:opacity-100 transition-opacity z-20"
        onMouseDown={startResizing}
      />

      {/* Dock Header */}
      <div className="flex h-10 items-center justify-between border-b border-atlas-border-default px-3 shrink-0">
        <div className="flex items-center text-sm font-semibold text-atlas-text-primary">
          <Bot className="mr-2 h-4 w-4 text-atlas-accent" />
          Agent Dock
        </div>
        <button
          onClick={() => setAgentDockOpen(false)}
          className="rounded-sm p-1 text-atlas-text-muted hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors"
          title="Close Agent Dock"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Dock Content */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        <div className="flex flex-col items-center justify-center h-full text-center text-sm text-atlas-text-muted">
          <Bot className="h-8 w-8 mb-3 opacity-20" />
          <p>Agent Dock</p>
          <p className="mt-1 text-xs">Agent activity will appear here when Agents are enabled.</p>
        </div>
      </div>
    </div>
  );
}
