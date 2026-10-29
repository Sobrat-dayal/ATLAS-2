"use client";

import React, { useState } from "react";
import { Badge, Button } from "@/design-system";
import { ResearchUpdateItemResponse } from "@/lib/research/types";
import {
  getUpdateItemPriorityDisplay,
  getUpdateItemStatusDisplay,
  formatResearchDate,
} from "@/lib/research/formatting";

interface ResearchUpdateQueueProps {
  items: ResearchUpdateItemResponse[];
  isLoading: boolean;
  onAcknowledge: (id: string) => Promise<unknown>;
  onResolve: (id: string, note: string) => Promise<unknown>;
  onDismiss: (id: string) => Promise<unknown>;
  onReopen: (id: string) => Promise<unknown>;
  onSelectEvent?: (eventId: string) => void;
  onNewRevalidation?: (targetType: string, targetId: string) => void;
}

export function ResearchUpdateQueue({
  items,
  isLoading,
  onAcknowledge,
  onResolve,
  onDismiss,
  onReopen,
  onSelectEvent,
  onNewRevalidation,
}: ResearchUpdateQueueProps) {
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [resolutionNote, setResolutionNote] = useState<string>("");
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const filteredItems = items.filter((item) => {
    if (statusFilter === "ALL") return true;
    if (statusFilter === "ACTIVE") {
      return item.status === "OPEN" || item.status === "ACKNOWLEDGED" || item.status === "IN_PROGRESS";
    }
    return item.status === statusFilter;
  });

  const handleResolveSubmit = async (id: string) => {
    if (!resolutionNote.trim()) return;
    setActionLoadingId(id);
    try {
      await onResolve(id, resolutionNote.trim());
      setResolvingId(null);
      setResolutionNote("");
    } finally {
      setActionLoadingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-atlas-surface-0 border border-atlas-border-default rounded-sm overflow-hidden">
      {/* Filter Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default px-4 py-2.5 bg-atlas-surface-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
            Research Update Queue
          </span>
          <Badge variant="outline" className="font-mono text-[10px]">
            {filteredItems.length} of {items.length} Tasks
          </Badge>
        </div>

        <div className="flex items-center gap-1.5">
          <span className="text-[10px] uppercase text-atlas-text-muted">Filter:</span>
          {["ALL", "ACTIVE", "OPEN", "ACKNOWLEDGED", "RESOLVED", "DISMISSED"].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`rounded-xs px-2 py-0.5 text-[11px] font-medium transition-colors ${
                statusFilter === status
                  ? "bg-atlas-accent text-white"
                  : "bg-atlas-surface-0 text-atlas-text-secondary hover:text-atlas-text-primary border border-atlas-border-default"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Item List */}
      <div className="flex-1 overflow-y-auto divide-y divide-atlas-border-default">
        {isLoading && items.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-xs text-atlas-text-muted">
            Loading research update tasks...
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="p-8 text-center text-xs text-atlas-text-muted">
            No update queue items found matching filter &quot;{statusFilter}&quot;.
          </div>
        ) : (
          filteredItems.map((item) => {
            const priorityDisplay = getUpdateItemPriorityDisplay(item.priority);
            const statusDisplay = getUpdateItemStatusDisplay(item.status);
            const isResolving = resolvingId === item.update_item_id;
            const isBusy = actionLoadingId === item.update_item_id;

            return (
              <div
                key={item.update_item_id}
                className="p-3.5 space-y-2 hover:bg-atlas-surface-hover/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={priorityDisplay.variant} className="text-[9px] font-bold">
                        {priorityDisplay.label}
                      </Badge>
                      <Badge variant={statusDisplay.variant} className="text-[9px]">
                        {statusDisplay.label}
                      </Badge>
                      <Badge variant="outline" className="font-mono text-[9px]">
                        {item.update_type.replace(/_/g, " ")}
                      </Badge>
                      <span className="font-mono text-[10px] text-atlas-text-muted">
                        Target: {item.target_resource_type}/{item.target_resource_id}
                      </span>
                    </div>

                    <h4 className="text-xs font-semibold text-atlas-text-primary">
                      {item.title}
                    </h4>

                    {item.description && (
                      <p className="text-[11px] text-atlas-text-secondary leading-relaxed">
                        {item.description}
                      </p>
                    )}

                    {/* Metadata line */}
                    <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] text-atlas-text-muted pt-1">
                      <span>Created: {formatResearchDate(item.created_at)}</span>
                      {item.acknowledged_at && (
                        <span>Ack: {formatResearchDate(item.acknowledged_at)}</span>
                      )}
                      {item.resolved_at && (
                        <span className="text-atlas-positive">Resolved: {formatResearchDate(item.resolved_at)}</span>
                      )}
                      {item.source_change_event_id && (
                        <button
                          onClick={() => onSelectEvent?.(item.source_change_event_id!)}
                          className="text-atlas-accent hover:underline flex items-center gap-1"
                        >
                          Source Event: {item.source_change_event_id} ➔
                        </button>
                      )}
                    </div>

                    {item.resolution_note && (
                      <div className="mt-2 p-2 bg-atlas-surface-1 rounded-xs border border-atlas-border-default text-[11px] text-atlas-text-primary">
                        <span className="font-bold text-atlas-positive">Resolution Note:</span> {item.resolution_note}
                      </div>
                    )}
                  </div>

                  {/* Actions Column */}
                  <div className="flex flex-col sm:flex-row items-end sm:items-center gap-1.5 shrink-0">
                    {item.status === "OPEN" && (
                      <Button
                        variant="secondary"
                        size="xs"
                        disabled={isBusy}
                        onClick={async () => {
                          setActionLoadingId(item.update_item_id);
                          try {
                            await onAcknowledge(item.update_item_id);
                          } finally {
                            setActionLoadingId(null);
                          }
                        }}
                      >
                        Acknowledge
                      </Button>
                    )}

                    {(item.status === "OPEN" || item.status === "ACKNOWLEDGED" || item.status === "IN_PROGRESS") && (
                      <Button
                        variant="primary"
                        size="xs"
                        disabled={isBusy}
                        onClick={() => {
                          setResolvingId(item.update_item_id);
                          setResolutionNote("");
                        }}
                      >
                        Resolve
                      </Button>
                    )}

                    {(item.status === "RESOLVED" || item.status === "DISMISSED") && (
                      <Button
                        variant="secondary"
                        size="xs"
                        disabled={isBusy}
                        onClick={async () => {
                          setActionLoadingId(item.update_item_id);
                          try {
                            await onReopen(item.update_item_id);
                          } finally {
                            setActionLoadingId(null);
                          }
                        }}
                      >
                        Reopen
                      </Button>
                    )}

                    {item.status !== "DISMISSED" && item.status !== "RESOLVED" && (
                      <Button
                        variant="ghost"
                        size="xs"
                        disabled={isBusy}
                        onClick={async () => {
                          setActionLoadingId(item.update_item_id);
                          try {
                            await onDismiss(item.update_item_id);
                          } finally {
                            setActionLoadingId(null);
                          }
                        }}
                      >
                        Dismiss
                      </Button>
                    )}

                    {onNewRevalidation && (
                      <Button
                        variant="secondary"
                        size="xs"
                        onClick={() => onNewRevalidation(item.target_resource_type, item.target_resource_id)}
                      >
                        Revalidate
                      </Button>
                    )}
                  </div>
                </div>

                {/* Inline Resolve Form */}
                {isResolving && (
                  <div className="mt-2 p-2.5 bg-atlas-surface-1 border border-atlas-border-default rounded-xs space-y-2">
                    <label className="text-[10px] uppercase font-bold text-atlas-text-muted block">
                      Resolution Note / Analyst Rationale:
                    </label>
                    <textarea
                      value={resolutionNote}
                      onChange={(e) => setResolutionNote(e.target.value)}
                      rows={2}
                      placeholder="Detail analyst verification, citation confirmation, or adjustments made..."
                      className="w-full rounded-xs border border-atlas-border-default bg-atlas-surface-0 px-2 py-1 text-xs text-atlas-text-primary focus:outline-hidden focus:border-atlas-accent"
                    />
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => setResolvingId(null)}
                      >
                        Cancel
                      </Button>
                      <Button
                        variant="primary"
                        size="xs"
                        disabled={!resolutionNote.trim() || isBusy}
                        onClick={() => handleResolveSubmit(item.update_item_id)}
                      >
                        Confirm Resolution
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
