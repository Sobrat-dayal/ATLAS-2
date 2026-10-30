"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/design-system";

interface Props {
  children: ReactNode;
  panelId: string;
  panelTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class WorkspacePanelErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`Workspace panel [${this.props.panelId}] crashed:`, error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full p-4 bg-atlas-surface-0 text-center font-mono text-xs">
          <AlertTriangle className="w-8 h-8 text-rose-500 mb-2" />
          <h4 className="font-semibold text-atlas-text-primary text-xs mb-1">
            Panel Runtime Error
          </h4>
          <p className="text-[11px] text-atlas-text-muted max-w-[280px] mb-3 font-sans">
            {this.state.error?.message || "An unexpected error occurred inside this panel."}
          </p>
          <Button variant="secondary" size="xs" onClick={this.handleReset} className="flex items-center gap-1">
            <RefreshCw className="w-3 h-3" />
            <span>Reload Panel</span>
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}

