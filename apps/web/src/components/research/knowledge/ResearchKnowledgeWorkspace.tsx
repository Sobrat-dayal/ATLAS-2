"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchKnowledgeEntryResponse,
  ResearchDependencyLineageResponse,
  KnowledgeEntryType,
} from "@/lib/research/types";
import {
  getKnowledgeEntryTypeDisplay,
  getKnowledgeStatusDisplay,
  getKnowledgeSourceAvailabilityDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";
import { ResearchKnowledgeInspector } from "./ResearchKnowledgeInspector";
import { ResearchDependencyLineageViewer } from "../updates/ResearchDependencyLineageViewer";

interface ResearchKnowledgeWorkspaceProps {
  entries: ResearchKnowledgeEntryResponse[];
  totalCount: number;
  isLoading: boolean;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearchSubmit: (types?: KnowledgeEntryType[]) => void;
  selectedEntryId: string | null;
  selectedEntry: ResearchKnowledgeEntryResponse | null;
  onSelectEntry: (id: string) => void;
  lineage: ResearchDependencyLineageResponse | null;
  isLineageLoading: boolean;
  onInspectLineage: (type: string, id: string) => void;
  onNavigateToResource?: (type: string, id: string) => void;
}

export function ResearchKnowledgeWorkspace({
  entries,
  totalCount,
  isLoading,
  searchQuery,
  onSearchChange,
  onSearchSubmit,
  selectedEntryId,
  selectedEntry,
  onSelectEntry,
  lineage,
  isLineageLoading,
  onInspectLineage,
  onNavigateToResource,
}: ResearchKnowledgeWorkspaceProps) {
  const [selectedType, setSelectedType] = useState<string>("ALL");
  const [activeRightPane, setActiveRightPane] = useState<"INSPECTOR" | "LINEAGE">("INSPECTOR");

  const entryTypes: Array<{ key: string; label: string; type?: KnowledgeEntryType }> = [
    { key: "ALL", label: "All Types" },
    { key: "INVESTIGATION", label: "Investigations", type: "RESEARCH_INVESTIGATION" },
    { key: "REPORT", label: "Reports", type: "RESEARCH_REPORT" },
    { key: "THESIS", label: "Theses", type: "RESEARCH_THESIS" },
    { key: "ANALYSIS", label: "Analyses", type: "RESEARCH_ANALYSIS" },
    { key: "FINDING", label: "Findings", type: "RESEARCH_FINDING" },
    { key: "EVIDENCE", label: "Evidence", type: "RESEARCH_EVIDENCE" },
    { key: "CLAIM", label: "Claims", type: "RESEARCH_CLAIM" },
    { key: "SOURCE", label: "Sources", type: "RESEARCH_SOURCE_REFERENCE" },
  ];

  const handleTypeSelect = (key: string, type?: KnowledgeEntryType) => {
    setSelectedType(key);
    onSearchSubmit(type ? [type] : undefined);
  };

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Top Search & Filter Bar */}
      <div className="border-b border-atlas-border-default bg-atlas-surface-1 p-3 shrink-0 space-y-2.5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-1 max-w-xl">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  const curr = entryTypes.find((t) => t.key === selectedType)?.type;
                  onSearchSubmit(curr ? [curr] : undefined);
                }
              }}
              placeholder="Search cross-module research knowledge (investigations, theses, claims, filings)..."
              className="w-full rounded-sm border border-atlas-border-default bg-atlas-surface-0 px-3 py-1.5 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
            />
            <Button
              variant="secondary"
              size="xs"
              onClick={() => {
                const curr = entryTypes.find((t) => t.key === selectedType)?.type;
                onSearchSubmit(curr ? [curr] : undefined);
              }}
              disabled={isLoading}
            >
              {isLoading ? "Searching..." : "Search"}
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <Badge variant="outline" className="font-mono text-[10px]">
              {totalCount} Knowledge Entries
            </Badge>
          </div>
        </div>

        {/* Type Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 overflow-x-auto">
          {entryTypes.map((item) => (
            <button
              key={item.key}
              onClick={() => handleTypeSelect(item.key, item.type)}
              className={`rounded-xs px-2.5 py-1 text-xs font-medium transition-colors ${
                selectedType === item.key
                  ? "bg-atlas-accent text-white"
                  : "bg-atlas-surface-0 text-atlas-text-secondary hover:text-atlas-text-primary border border-atlas-border-default"
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Split Layout: Left Table / Right Inspector & Lineage */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Entries List */}
        <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default">
          {isLoading && entries.length === 0 ? (
            <div className="flex h-48 items-center justify-center text-xs text-atlas-text-muted">
              Loading research knowledge entries...
            </div>
          ) : entries.length === 0 ? (
            <div className="p-8 text-center text-xs text-atlas-text-muted">
              No research knowledge entries found for query &quot;{searchQuery}&quot;.
            </div>
          ) : (
            entries.map((entry) => {
              const typeDisplay = getKnowledgeEntryTypeDisplay(entry.entry_type);
              const statusDisplay = getKnowledgeStatusDisplay(entry.knowledge_status);
              const availDisplay = getKnowledgeSourceAvailabilityDisplay(entry.source_status);
              const isSelected = selectedEntryId === entry.knowledge_entry_id;

              return (
                <div
                  key={entry.knowledge_entry_id}
                  onClick={() => onSelectEntry(entry.knowledge_entry_id)}
                  className={`p-3.5 space-y-1.5 cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-atlas-surface-hover/80 border-l-2 border-atlas-accent"
                      : "hover:bg-atlas-surface-hover/40"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={typeDisplay.variant} className="text-[10px]">
                        {typeDisplay.label}
                      </Badge>
                      <Badge variant={statusDisplay.variant} className="text-[9px]">
                        {statusDisplay.label}
                      </Badge>
                      <Badge variant={availDisplay.variant} className="text-[9px]">
                        {availDisplay.label}
                      </Badge>
                      <span className="font-mono text-[10px] text-atlas-text-muted">
                        Ref: {entry.referenced_resource_type}/{entry.referenced_resource_id}
                      </span>
                    </div>

                    <span className="font-mono text-[10px] text-atlas-text-muted shrink-0">
                      {formatResearchDate(entry.updated_at)}
                    </span>
                  </div>

                  <h4 className="text-xs font-bold text-atlas-text-primary leading-snug">
                    {entry.title}
                  </h4>

                  {entry.description && (
                    <p className="line-clamp-2 text-[11px] text-atlas-text-secondary leading-relaxed">
                      {entry.description}
                    </p>
                  )}

                  <div className="flex flex-wrap items-center gap-2 pt-0.5">
                    {entry.subject_entity_ids.map((entityId) => (
                      <Badge key={entityId} variant="primary" className="font-mono text-[9px]">
                        {entityId}
                      </Badge>
                    ))}
                    {entry.investigation_id && (
                      <span className="font-mono text-[10px] text-atlas-text-muted">
                        Inv: {entry.investigation_id}
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Panel: Tabbed Inspector or Lineage Graph */}
        <div className="w-96 md:w-[480px] lg:w-[540px] shrink-0 border-l border-atlas-border-default flex flex-col bg-atlas-surface-1">
          {/* Subheader Switch */}
          <div className="flex items-center justify-between border-b border-atlas-border-default px-3 py-2 bg-atlas-surface-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-atlas-text-primary">
              Artifact Detail & Lineage
            </span>
            <div className="flex items-center rounded-xs border border-atlas-border-default bg-atlas-surface-0 p-0.5">
              <button
                onClick={() => setActiveRightPane("INSPECTOR")}
                className={`rounded-2xs px-2.5 py-0.5 text-[11px] font-medium transition-colors ${
                  activeRightPane === "INSPECTOR"
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                Inspector
              </button>
              <button
                onClick={() => setActiveRightPane("LINEAGE")}
                className={`rounded-2xs px-2.5 py-0.5 text-[11px] font-medium transition-colors ${
                  activeRightPane === "LINEAGE"
                    ? "bg-atlas-accent text-white"
                    : "text-atlas-text-secondary hover:text-atlas-text-primary"
                }`}
              >
                Lineage Graph
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-hidden">
            {activeRightPane === "INSPECTOR" ? (
              <ResearchKnowledgeInspector
                entry={selectedEntry}
                lineage={lineage}
                isLineageLoading={isLineageLoading}
                onInspectLineage={(type, id) => {
                  onInspectLineage(type, id);
                  setActiveRightPane("LINEAGE");
                }}
                onNavigateToResource={onNavigateToResource}
              />
            ) : (
              <ResearchDependencyLineageViewer
                lineage={lineage}
                isLoading={isLineageLoading}
                onRefresh={() => {
                  if (selectedEntry?.referenced_resource_type && selectedEntry?.referenced_resource_id) {
                    onInspectLineage(selectedEntry.referenced_resource_type, selectedEntry.referenced_resource_id);
                  }
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

