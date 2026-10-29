"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchSourceChangeEventResponse,
  ResearchImpactAssessmentResponse,
} from "@/lib/research/types";
import {
  getSourceChangeTypeDisplay,
  getImpactCategoryDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchImpactInspectorProps {
  changeEvent: ResearchSourceChangeEventResponse | null;
  impacts: ResearchImpactAssessmentResponse[];
  isLoading: boolean;
  onRunRevalidation?: (targetType: string, targetId: string) => void;
  onClose?: () => void;
}

export function ResearchImpactInspector({
  changeEvent,
  impacts,
  isLoading,
  onRunRevalidation,
  onClose,
}: ResearchImpactInspectorProps) {
  if (!changeEvent) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-center text-xs text-atlas-text-muted">
        Select a canonical source change event to inspect detected revisions and downstream impact assessments.
      </div>
    );
  }

  const changeDisplay = getSourceChangeTypeDisplay(changeEvent.change_type);

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0 border-l border-atlas-border-default">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default px-4 py-3 shrink-0 bg-atlas-surface-1">
        <div className="flex items-center gap-2">
          <Badge variant={changeDisplay.variant} className="text-[10px]">
            {changeDisplay.label}
          </Badge>
          <span className="font-mono text-xs text-atlas-text-muted">
            {changeEvent.change_event_id}
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
        {/* Source Change Event Overview */}
        <div className="space-y-2 bg-atlas-surface-1 p-3 rounded-sm border border-atlas-border-default text-xs">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase text-atlas-text-muted">Canonical Source</span>
            <span className="font-mono font-medium text-atlas-accent">{changeEvent.canonical_source_id}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase text-atlas-text-muted">Revision Transition</span>
            <span className="font-mono text-atlas-text-primary">
              {changeEvent.old_revision_id || "(initial)"} ➔ {changeEvent.new_revision_id}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase text-atlas-text-muted">Provider</span>
            <span className="font-mono text-atlas-text-secondary">{changeEvent.provider_id || "EDGAR"}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase text-atlas-text-muted">Detected At</span>
            <span className="font-mono text-atlas-text-secondary">{formatResearchDate(changeEvent.detected_at)}</span>
          </div>
          {changeEvent.changed_fields.length > 0 && (
            <div className="pt-2 border-t border-atlas-border-default">
              <span className="text-[10px] uppercase text-atlas-text-muted block mb-1">Changed Sections / Fields</span>
              <div className="flex flex-wrap gap-1">
                {changeEvent.changed_fields.map((f, i) => (
                  <Badge key={i} variant="outline" className="text-[10px]">
                    {f}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Impacts List */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Downstream Impacts ({impacts.length})
            </span>
            {isLoading && <span className="text-xs text-atlas-text-muted">Loading...</span>}
          </div>

          {impacts.length === 0 ? (
            <div className="p-4 text-center text-xs text-atlas-text-muted bg-atlas-surface-1 rounded-sm border border-atlas-border-default">
              No downstream deliverables currently impacted by this source revision.
            </div>
          ) : (
            <div className="space-y-3">
              {impacts.map((imp) => {
                const impactDisplay = getImpactCategoryDisplay(imp.impact_category);
                return (
                  <div
                    key={imp.impact_id}
                    className="p-3 rounded-sm border border-atlas-border-default bg-atlas-surface-1 space-y-2.5 text-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant={impactDisplay.variant} className="text-[10px]">
                        {impactDisplay.label}
                      </Badge>
                      {imp.direct_dependency && (
                        <Badge variant="warning" className="text-[9px]">
                          Direct Link
                        </Badge>
                      )}
                    </div>

                    <div className="font-mono font-medium text-atlas-text-primary">
                      Target: <span className="text-atlas-accent">{imp.target_resource_type}/{imp.target_resource_id}</span>
                      {imp.target_revision_id && <span className="text-atlas-text-muted"> ({imp.target_revision_id})</span>}
                    </div>

                    <p className="text-atlas-text-secondary text-[11px] leading-relaxed">
                      {imp.summary}
                    </p>

                    {/* Dependency Path Chain */}
                    {imp.dependency_path.length > 0 && (
                      <div className="bg-atlas-surface-0 p-2 rounded-xs border border-atlas-border-default font-mono text-[10px] text-atlas-text-muted">
                        <span className="font-bold text-atlas-text-secondary block mb-1">Impact Path:</span>
                        <div className="flex flex-wrap items-center gap-1">
                          {imp.dependency_path.map((segment, idx) => (
                            <React.Fragment key={idx}>
                              <span className="text-atlas-text-primary">{segment}</span>
                              {idx < imp.dependency_path.length - 1 && (
                                <span className="text-atlas-accent">➔</span>
                              )}
                            </React.Fragment>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Revalidation Action Button */}
                    {onRunRevalidation && (
                      <div className="pt-2 flex justify-end">
                        <Button
                          variant="secondary"
                          size="xs"
                          onClick={() => onRunRevalidation(imp.target_resource_type, imp.target_resource_id)}
                        >
                          Run Revalidation ➔
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

