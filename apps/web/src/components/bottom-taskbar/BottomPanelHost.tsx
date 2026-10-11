"use client";

import React, { Component, ErrorInfo, ReactNode, useEffect, useRef } from "react";
import { useBottomPanel } from "@/hooks/bottom-taskbar";
import { getPanelDefinition, DEFAULT_BOTTOM_PANEL_HEIGHT } from "@/lib/bottom-taskbar";
import { BottomPanelResizeHandle } from "./BottomPanelResizeHandle";
import { BottomPanelHeader } from "./BottomPanelHeader";
import { AlertTriangle } from "lucide-react";

/**
 * Lightweight local error boundary to isolate future panel component failures
 * without taking down the authenticated AppShell.
 */
class PanelErrorBoundary extends Component<{ children: ReactNode; panelId: string }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: ReactNode; panelId: string }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`[BottomPanelHost] Error rendering panel ${this.props.panelId}:`, error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-6 text-center text-atlas-negative">
          <AlertTriangle className="h-6 w-6 mb-2" />
          <h4 className="text-xs font-semibold uppercase">Failed to load panel content</h4>
          <p className="text-[11px] text-atlas-text-muted mt-1 max-w-sm">
            {this.state.error?.message || "An unexpected error occurred."}
          </p>
        </div>
      );
    }
    return this.props.children;
  }
}

export function BottomPanelHost() {
  const { activePanelId, isOpen, panelHeight, closePanel, setPanelHeight } = useBottomPanel();
  const hostRef = useRef<HTMLDivElement>(null);

  // Keyboard Escape listener: only closes if focus is inside or no modal is active
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        // Do not intercept if command palette, search modal, or other dialog is open
        const openDialog = document.querySelector('[role="dialog"][data-state="open"]');
        if (openDialog) return;

        closePanel();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closePanel]);

  if (!isOpen || !activePanelId) {
    return null;
  }

  const panelDef = getPanelDefinition(activePanelId);
  if (!panelDef) {
    return null;
  }

  const PanelComponent = panelDef.component;

  return (
    <div
      ref={hostRef}
      id={`bottom-panel-${panelDef.id}`}
      role="region"
      aria-label={`${panelDef.label} Panel`}
      style={{ height: `${panelHeight}px` }}
      className="relative flex flex-col border-t border-atlas-border-default bg-atlas-surface-1 shrink-0 z-10 w-full overflow-hidden"
    >
      {/* Top Drag Resize Handle */}
      <BottomPanelResizeHandle
        panelHeight={panelHeight}
        onHeightChange={setPanelHeight}
        onResetHeight={() => setPanelHeight(DEFAULT_BOTTOM_PANEL_HEIGHT)}
      />

      {/* Panel Header */}
      <BottomPanelHeader
        panel={panelDef}
        onClose={closePanel}
        onResetHeight={() => setPanelHeight(DEFAULT_BOTTOM_PANEL_HEIGHT)}
      />

      {/* Scrollable Content Region */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar bg-atlas-surface-1 relative">
        <PanelErrorBoundary panelId={panelDef.id}>
          <PanelComponent />
        </PanelErrorBoundary>
      </div>
    </div>
  );
}
