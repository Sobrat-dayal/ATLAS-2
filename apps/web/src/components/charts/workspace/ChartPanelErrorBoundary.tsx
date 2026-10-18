"use client";

/**
 * Chart Panel Error Boundary for Multi-Chart Workspaces (Stage 72).
 *
 * Catches rendering, canvas, and mathematical computation errors within an individual
 * chart panel, preventing sibling panels or the main AppShell from crashing.
 */

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

export interface ChartPanelErrorBoundaryProps {
  panelId: string;
  children: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ChartPanelErrorBoundary extends Component<ChartPanelErrorBoundaryProps, State> {
  constructor(props: ChartPanelErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error(`[ChartPanelErrorBoundary: ${this.props.panelId}] caught an error:`, error, errorInfo);
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full min-h-[220px] flex flex-col items-center justify-center p-4 bg-zinc-950 border border-rose-900/60 rounded text-center">
          <div className="w-10 h-10 rounded-full bg-rose-950/60 border border-rose-800/80 flex items-center justify-center mb-2">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
          </div>
          <h3 className="text-sm font-mono font-semibold text-zinc-100">Chart Panel Error</h3>
          <p className="text-xs font-mono text-zinc-400 mt-1 max-w-sm truncate">
            {this.state.error?.message || "An unexpected error occurred in this chart panel."}
          </p>
          <button
            type="button"
            onClick={this.handleRetry}
            className="mt-3 flex items-center gap-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 rounded text-xs font-mono text-zinc-200 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Retry Panel</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
