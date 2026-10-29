"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchKnowledgeEntryResponse,
  ResearchDependencyLineageResponse,
} from "@/lib/research/types";
import {
  getKnowledgeEntryTypeDisplay,
  getKnowledgeStatusDisplay,
  getKnowledgeSourceAvailabilityDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchKnowledgeInspectorProps {
  entry: ResearchKnowledgeEntryResponse | null;
  lineage: ResearchDependencyLineageResponse | null;
  isLineageLoading: boolean;
  onInspectLineage: (type: string, id: string) => void;
  onNavigateToResource?: (type: string, id: string) => void;
  onClose?: () => void;
}

export function ResearchKnowledgeInspector({
  entry,
  lineage,
  isLineageLoading,
  onInspectLineage,
  onNavigateToResource,
  onClose,
}: ResearchKnowledgeInspectorProps) {
  if (!entry) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center text-xs text-atlas-text-muted">
        Select a knowledge library entry to view detailed provenance and lineage graph.
      </div>
    );
  }

  const typeDisplay = getKnowledgeEntryTypeDisplay(entry.entry_type);
  const statusDisplay = getKnowledgeStatusDisplay(entry.knowledge_status);
  const availDisplay = getKnowledgeSourceAvailabilityDisplay(entry.source_status);

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0 border-l border-atlas-border-default">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default px-4 py-3 shrink-0 bg-atlas-surface-1">
        <div className="flex items-center gap-2">
          <Badge variant={typeDisplay.variant} className="text-[10px]">
            {typeDisplay.label}
          </Badge>
          <span className="font-mono text-xs text-atlas-text-muted">
            {entry.knowledge_entry_id}
          </span>
        </div>
        {onClose && (
          <Button variant="ghost" size="xs" onClick={onClose}>
            ✕
          </Button>
        )}
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div>
          <h3 className="text-sm font-bold text-atlas-text-primary leading-snug">
            {entry.title}
          </h3>
          {entry.description && (
            <p className="mt-2 text-xs text-atlas-text-secondary leading-relaxed bg-atlas-surface-1 p-2.5 rounded-sm border border-atlas-border-default">
              {entry.description}
            </p>
          )}
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-2 text-xs bg-atlas-surface-1 p-3 rounded-sm border border-atlas-border-default">
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Resource Type</span>
            <div className="font-mono font-medium text-atlas-text-primary">{entry.referenced_resource_type}</div>
          </div>
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Resource ID</span>
            <div className="font-mono font-medium text-atlas-accent truncate" title={entry.referenced_resource_id}>
              {entry.referenced_resource_id}
            </div>
          </div>
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Status</span>
            <div>
              <Badge variant={statusDisplay.variant} className="text-[9px]">
                {statusDisplay.label}
              </Badge>
            </div>
          </div>
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Availability</span>
            <div>
              <Badge variant={availDisplay.variant} className="text-[9px]">
                {availDisplay.label}
              </Badge>
            </div>
          </div>
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Owner / Author</span>
            <div className="font-mono text-atlas-text-secondary">{entry.owner_user_id}</div>
          </div>
          <div>
            <span className="text-[10px] text-atlas-text-muted uppercase">Updated</span>
            <div className="font-mono text-atlas-text-secondary">{formatResearchDate(entry.updated_at)}</div>
          </div>
        </div>

        {/* Subject Entities */}
        {entry.subject_entity_ids.length > 0 && (
          <div>
            <div className="text-[10px] font-semibold text-atlas-text-muted uppercase tracking-wider mb-1.5">
              Subject Entities
            </div>
            <div className="flex flex-wrap gap-1">
              {entry.subject_entity_ids.map((entityId) => (
                <Badge key={entityId} variant="primary" className="font-mono text-[10px]">
                  {entityId}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Lineage Section */}
        <div className="pt-2 border-t border-atlas-border-default">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider">
              Dependency Lineage
            </span>
            <Button
              variant="secondary"
              size="xs"
              onClick={() => onInspectLineage(entry.referenced_resource_type, entry.referenced_resource_id)}
              disabled={isLineageLoading}
            >
              {isLineageLoading ? "Tracing..." : "Refresh Lineage"}
            </Button>
          </div>

          {lineage && lineage.root_resource_id === entry.referenced_resource_id ? (
            <div className="space-y-2 bg-atlas-surface-1 p-2.5 rounded-sm border border-atlas-border-default text-xs font-mono">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-atlas-text-muted">Discovered Nodes:</span>
                <span className="font-bold text-atlas-text-primary">{lineage.nodes.length}</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-atlas-text-muted">Dependency Edges:</span>
                <span className="font-bold text-atlas-text-primary">{lineage.edges.length}</span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-atlas-text-muted">Cycle Check:</span>
                <span className={lineage.has_cycle ? "text-atlas-negative font-bold" : "text-atlas-positive font-bold"}>
                  {lineage.has_cycle ? "Cycle Detected (Loop)" : "Acyclic (Safe)"}
                </span>
              </div>
              {lineage.max_depth_reached && (
                <div className="text-[10px] text-atlas-warning font-sans">
                  Lineage depth reached traversal limit (5 hops).
                </div>
              )}
            </div>
          ) : (
            <div className="p-3 text-center text-xs text-atlas-text-muted bg-atlas-surface-1 rounded-sm border border-atlas-border-default">
              Click &quot;Refresh Lineage&quot; to compute multi-hop provenance graph.
            </div>
          )}
        </div>
      </div>

      {/* Footer Navigation Action */}
      {onNavigateToResource && (
        <div className="p-3 border-t border-atlas-border-default bg-atlas-surface-1 shrink-0">
          <Button
            variant="primary"
            size="sm"
            className="w-full"
            onClick={() => onNavigateToResource(entry.referenced_resource_type, entry.referenced_resource_id)}
          >
            Open {typeDisplay.label} Console →
          </Button>
        </div>
      )}
    </div>
  );
}

