"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import {
  ResearchUpdateItemResponse,
  ResearchSourceChangeEventResponse,
  ResearchImpactAssessmentResponse,
  ResearchDependencyLineageResponse,
  CreateRevalidationRequest,
  ResearchRevalidationResultResponse,
} from "@/lib/research/types";
import { getSourceChangeTypeDisplay, formatResearchDate } from "@/lib/research/formatting";
import { ResearchUpdateQueue } from "./ResearchUpdateQueue";
import { ResearchImpactInspector } from "./ResearchImpactInspector";
import { ResearchDependencyLineageViewer } from "./ResearchDependencyLineageViewer";
import { ResearchRevalidationDialog } from "./ResearchRevalidationDialog";

interface ResearchUpdatesWorkspaceProps {
  updateItems: ResearchUpdateItemResponse[];
  updateItemsTotal: number;
  isUpdateItemsLoading: boolean;
  onAcknowledgeUpdate: (id: string) => Promise<unknown>;
  onResolveUpdate: (id: string, note: string) => Promise<unknown>;
  onDismissUpdate: (id: string) => Promise<unknown>;
  onReopenUpdate: (id: string) => Promise<unknown>;

  sourceChangeEvents: ResearchSourceChangeEventResponse[];
  isSourceChangesLoading: boolean;
  selectedSourceChangeEvent: ResearchSourceChangeEventResponse | null;
  onSelectSourceChangeEvent: (eventId: string) => void;
  impactAssessments: ResearchImpactAssessmentResponse[];
  isImpactsLoading: boolean;

  dependencyLineage: ResearchDependencyLineageResponse | null;
  isLineageLoading: boolean;
  onInspectLineage: (type: string, id: string) => void;

  onExecuteRevalidation: (req: CreateRevalidationRequest) => Promise<ResearchRevalidationResultResponse>;
}

export function ResearchUpdatesWorkspace({
  updateItems,
  isUpdateItemsLoading,
  onAcknowledgeUpdate,
  onResolveUpdate,
  onDismissUpdate,
  onReopenUpdate,

  sourceChangeEvents,
  isSourceChangesLoading,
  selectedSourceChangeEvent,
  onSelectSourceChangeEvent,
  impactAssessments,
  isImpactsLoading,

  dependencyLineage,
  isLineageLoading,
  onInspectLineage,

  onExecuteRevalidation,
}: ResearchUpdatesWorkspaceProps) {
  const [activeSection, setActiveSection] = useState<"QUEUE" | "CHANGES" | "LINEAGE">("QUEUE");
  const [isRevalidationOpen, setIsRevalidationOpen] = useState<boolean>(false);
  const [revalidationTarget, setRevalidationTarget] = useState<{ type: string; id: string }>({
    type: "REPORT",
    id: "rep-apple-services-expansion-fy24",
  });

  const openRevalidationModal = (type: string, id: string) => {
    setRevalidationTarget({ type, id });
    setIsRevalidationOpen(true);
  };

  const openUpdatesCount = updateItems.filter(
    (u) => u.status === "OPEN" || u.status === "IN_PROGRESS"
  ).length;

  return (
    <div className="flex h-full flex-col overflow-hidden bg-atlas-surface-0">
      {/* Top Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default px-4 py-3 shrink-0 bg-atlas-surface-1">
        <div className="flex items-center gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
            Continuous Evidence Monitoring & Lifecycle
          </span>
          <div className="flex items-center rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-0.5">
            <button
              onClick={() => setActiveSection("QUEUE")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeSection === "QUEUE"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Update Queue ({openUpdatesCount})
            </button>
            <button
              onClick={() => setActiveSection("CHANGES")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeSection === "CHANGES"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Source Changes ({sourceChangeEvents.length})
            </button>
            <button
              onClick={() => setActiveSection("LINEAGE")}
              className={`rounded-xs px-3 py-1 text-xs font-medium transition-colors ${
                activeSection === "LINEAGE"
                  ? "bg-atlas-accent text-white"
                  : "text-atlas-text-secondary hover:text-atlas-text-primary"
              }`}
            >
              Dependency Lineage
            </button>
          </div>
        </div>

        <Button
          variant="primary"
          size="xs"
          onClick={() => setIsRevalidationOpen(true)}
          className="flex items-center gap-1.5"
        >
          <span>↻</span>
          <span>Run Automated Revalidation</span>
        </Button>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {activeSection === "QUEUE" && (
          <ResearchUpdateQueue
            items={updateItems}
            isLoading={isUpdateItemsLoading}
            onAcknowledge={onAcknowledgeUpdate}
            onResolve={onResolveUpdate}
            onDismiss={onDismissUpdate}
            onReopen={onReopenUpdate}
            onSelectEvent={(eventId) => {
              onSelectSourceChangeEvent(eventId);
              setActiveSection("CHANGES");
            }}
            onNewRevalidation={(type, id) => openRevalidationModal(type, id)}
          />
        )}

        {activeSection === "CHANGES" && (
          <div className="flex h-full">
            {/* Source Changes List */}
            <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default border-r border-atlas-border-default">
              <div className="p-3 bg-atlas-surface-1 border-b border-atlas-border-default flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                  Canonical Source Change Stream
                </span>
                <Badge variant="outline" className="font-mono text-[10px]">
                  {sourceChangeEvents.length} Events Detected
                </Badge>
              </div>

              {isSourceChangesLoading && sourceChangeEvents.length === 0 ? (
                <div className="p-8 text-center text-xs text-atlas-text-muted">
                  Loading source change events...
                </div>
              ) : sourceChangeEvents.length === 0 ? (
                <div className="p-8 text-center text-xs text-atlas-text-muted">
                  No canonical source changes detected.
                </div>
              ) : (
                sourceChangeEvents.map((ev) => {
                  const typeDisplay = getSourceChangeTypeDisplay(ev.change_type);
                  const isSelected = selectedSourceChangeEvent?.change_event_id === ev.change_event_id;

                  return (
                    <div
                      key={ev.change_event_id}
                      onClick={() => onSelectSourceChangeEvent(ev.change_event_id)}
                      className={`p-3.5 space-y-1.5 cursor-pointer transition-colors ${
                        isSelected
                          ? "bg-atlas-surface-hover/80 border-l-2 border-atlas-accent"
                          : "hover:bg-atlas-surface-hover/40"
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <Badge variant={typeDisplay.variant} className="text-[10px]">
                            {typeDisplay.label}
                          </Badge>
                          <span className="font-mono text-xs font-bold text-atlas-text-primary">
                            {ev.canonical_source_id}
                          </span>
                        </div>
                        <span className="font-mono text-[10px] text-atlas-text-muted">
                          {formatResearchDate(ev.detected_at)}
                        </span>
                      </div>

                      <div className="font-mono text-[11px] text-atlas-text-secondary">
                        Revision: {ev.old_revision_id || "(original)"} ➔ {ev.new_revision_id}
                      </div>

                      {ev.changed_fields.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-1">
                          {ev.changed_fields.map((f, i) => (
                            <Badge key={i} variant="outline" className="text-[9px]">
                              {f}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            {/* Impact Inspector Side Pane */}
            <div className="w-96 md:w-[480px] lg:w-[520px] shrink-0 bg-atlas-surface-1">
              <ResearchImpactInspector
                changeEvent={selectedSourceChangeEvent}
                impacts={impactAssessments}
                isLoading={isImpactsLoading}
                onRunRevalidation={(type, id) => openRevalidationModal(type, id)}
              />
            </div>
          </div>
        )}

        {activeSection === "LINEAGE" && (
          <div className="h-full p-4">
            <ResearchDependencyLineageViewer
              lineage={dependencyLineage}
              isLoading={isLineageLoading}
              onRefresh={() => {
                if (dependencyLineage) {
                  onInspectLineage(dependencyLineage.root_resource_type, dependencyLineage.root_resource_id);
                }
              }}
            />
          </div>
        )}
      </div>

      {/* Automated Revalidation Dialog */}
      <ResearchRevalidationDialog
        isOpen={isRevalidationOpen}
        onClose={() => setIsRevalidationOpen(false)}
        onSubmit={onExecuteRevalidation}
        defaultTargetType={revalidationTarget.type}
        defaultTargetId={revalidationTarget.id}
      />
    </div>
  );
}

