"use client";

import React from "react";
import { ResearchAnalysis, ResearchAnalysisType } from "@/lib/research/types";
import {
  getAnalysisStatusDisplay,
  getAnalysisTypeLabel,
} from "@/lib/research/formatting";
import { Badge, Button } from "@/design-system";

interface ResearchAnalysisListProps {
  analyses: ResearchAnalysis[];
  isLoading: boolean;
  selectedAnalysisId?: string | null;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  typeFilter?: ResearchAnalysisType;
  onTypeFilterChange: (type?: ResearchAnalysisType) => void;
  entityFilter: string;
  onEntityFilterChange: (entity: string) => void;
  onSelectAnalysis: (analysisId: string) => void;
  onNewAnalysis: () => void;
}

export function ResearchAnalysisList({
  analyses,
  isLoading,
  selectedAnalysisId,
  searchQuery,
  onSearchChange,
  typeFilter,
  onTypeFilterChange,
  entityFilter,
  onEntityFilterChange,
  onSelectAnalysis,
  onNewAnalysis,
}: ResearchAnalysisListProps) {
  return (
    <div className="flex h-full flex-col border-r border-atlas-border-default bg-atlas-surface-0 w-80 shrink-0">
      {/* Header & Filter Controls */}
      <div className="border-b border-atlas-border-subtle p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
            Analyses ({analyses.length})
          </span>
          <Button variant="primary" size="sm" onClick={onNewAnalysis}>
            + New
          </Button>
        </div>

        {/* Search */}
        <input
          type="text"
          placeholder="Filter analyses..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2.5 py-1 text-xs text-atlas-text-primary placeholder:text-atlas-text-muted"
        />

        {/* Type Filter */}
        <div className="grid grid-cols-2 gap-1.5">
          <select
            value={typeFilter || ""}
            onChange={(e) => onTypeFilterChange((e.target.value as ResearchAnalysisType) || undefined)}
            className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-1 text-[11px] text-atlas-text-secondary"
          >
            <option value="">All Types</option>
            <option value="COMPANY_FINANCIAL_TREND">Company Trend</option>
            <option value="COMPANY_RATIO_ANALYSIS">Ratio Analysis</option>
            <option value="PEER_BENCHMARKING">Peer Benchmark</option>
            <option value="MACROECONOMIC_TIME_SERIES">Macro Series</option>
            <option value="HYPOTHESIS_EVALUATION">Hypothesis Test</option>
          </select>

          <input
            type="text"
            placeholder="Entity (AAPL)"
            value={entityFilter}
            onChange={(e) => onEntityFilterChange(e.target.value)}
            className="rounded-xs border border-atlas-border-default bg-atlas-surface-1 px-2 py-1 text-[11px] font-mono uppercase text-atlas-text-primary placeholder:text-atlas-text-muted"
          />
        </div>
      </div>

      {/* List items */}
      <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-subtle">
        {isLoading ? (
          <div className="p-4 text-center text-xs text-atlas-text-muted">Loading analyses...</div>
        ) : analyses.length === 0 ? (
          <div className="p-4 text-center text-xs text-atlas-text-muted italic">
            No analyses found matching filter criteria.
          </div>
        ) : (
          analyses.map((an) => {
            const isSelected = an.analysis_id === selectedAnalysisId;
            const status = getAnalysisStatusDisplay(an.status);

            return (
              <button
                key={an.analysis_id}
                type="button"
                onClick={() => onSelectAnalysis(an.analysis_id)}
                className={`w-full text-left p-3 transition-colors ${
                  isSelected
                    ? "bg-atlas-surface-2 border-l-2 border-atlas-accent"
                    : "hover:bg-atlas-surface-1/50"
                }`}
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span className="font-semibold text-xs text-atlas-text-primary line-clamp-1">
                    {an.title}
                  </span>
                  <Badge variant={status.variant} className="text-[9px] shrink-0">
                    {status.label}
                  </Badge>
                </div>

                <div className="flex items-center gap-1.5 text-[10px] text-atlas-text-muted font-mono mb-1">
                  <span className="font-semibold text-atlas-text-secondary">
                    {an.primary_subject_entity_id || "ALL"}
                  </span>
                  <span>•</span>
                  <span className="truncate">{getAnalysisTypeLabel(an.analysis_type)}</span>
                </div>

                <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono">
                  <span>Rev {an.current_revision}</span>
                  <span>Runs: {an.runs_count}</span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
