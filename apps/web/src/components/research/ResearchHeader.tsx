"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { ResearchTabMode } from "@/hooks/research/useResearchWorkspace";

interface ResearchHeaderProps {
  activeTab: ResearchTabMode;
  onTabChange: (tab: ResearchTabMode) => void;
  onNewInvestigation: () => void;
  activeCount?: number;
}

export function ResearchHeader({
  activeTab,
  onTabChange,
  onNewInvestigation,
  activeCount = 0,
}: ResearchHeaderProps) {
  return (
    <div className="border-b border-atlas-border-default bg-atlas-surface-0 px-4 py-3 shrink-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold tracking-tight text-atlas-text-primary">
                FINANCIAL RESEARCH PLATFORM
              </h1>
              <Badge variant="outline" className="font-mono text-[10px]">
                STAGE 105 DOCUMENT INTELLIGENCE
              </Badge>
              {activeCount > 0 && (
                <Badge variant="primary" className="text-[10px]">
                  {activeCount} Active
                </Badge>
              )}
            </div>
            <p className="text-xs text-atlas-text-muted">
              Source discovery, document intelligence, multi-document comparison, structured evidence extraction, and citation-anchored research.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <nav className="flex items-center rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-0.5">
            <button
              onClick={() => onTabChange("OVERVIEW")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "OVERVIEW"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => onTabChange("DISCOVERY")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "DISCOVERY"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Discovery
            </button>
            <button
              onClick={() => onTabChange("DOCUMENT_VIEWER")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "DOCUMENT_VIEWER"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Document Viewer
            </button>
            <button
              onClick={() => onTabChange("COMPARE")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "COMPARE"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Comparison
            </button>
            <button
              onClick={() => onTabChange("INVESTIGATIONS")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "INVESTIGATIONS"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Investigations
            </button>
            <button
              onClick={() => onTabChange("SOURCES")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "SOURCES"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Source Library
            </button>
            <button
              onClick={() => onTabChange("ACTIVITY")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeTab === "ACTIVITY"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Activity Timeline
            </button>
          </nav>

          <Button
            variant="primary"
            size="sm"
            onClick={onNewInvestigation}
            className="flex items-center gap-1.5 font-medium"
          >
            <span>+</span>
            <span>New Investigation</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
