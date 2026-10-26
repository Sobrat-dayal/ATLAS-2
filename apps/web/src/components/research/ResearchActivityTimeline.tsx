"use client";

import React, { useState } from "react";
import { Badge, Input } from "@/design-system";
import { ResearchActivity } from "@/lib/research/types";

interface ResearchActivityTimelineProps {
  activities: ResearchActivity[];
  isLoading?: boolean;
}

export function ResearchActivityTimeline({
  activities,
  isLoading = false,
}: ResearchActivityTimelineProps) {
  const [filterQuery, setFilterQuery] = useState("");

  const filtered = activities.filter((act) => {
    if (!filterQuery) return true;
    const q = filterQuery.toLowerCase();
    const actionMatch = act.action_type.toLowerCase().includes(q);
    const objMatch = act.object_type.toLowerCase().includes(q);
    const detailMatch = JSON.stringify(act.details).toLowerCase().includes(q);
    return actionMatch || objMatch || detailMatch;
  });

  return (
    <div className="flex h-full flex-col p-4">
      <div className="mb-3 flex items-center justify-between rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-2.5">
        <div className="w-64">
          <Input
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            placeholder="Filter activity history..."
            className="h-8 text-xs"
          />
        </div>
        <div className="font-mono text-xs text-atlas-text-muted">
          {filtered.length} logged operations
        </div>
      </div>

      <div className="flex-1 overflow-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-xs text-atlas-text-muted">
            Loading activity timeline...
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-xs text-atlas-text-muted">
            No activity records match the filter.
          </div>
        ) : (
          <div className="relative border-l border-atlas-border-default pl-4 space-y-4">
            {filtered.map((act) => (
              <div key={act.activity_id} className="relative group">
                {/* Timeline node */}
                <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full border border-atlas-surface-1 bg-atlas-accent" />

                <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-0 p-3 text-xs transition-colors group-hover:border-atlas-border-strong">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {act.action_type.replace(/_/g, " ")}
                      </Badge>
                      <span className="font-mono text-[11px] text-atlas-text-secondary">
                        Object: {act.object_type} ({act.object_id})
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-atlas-text-muted">
                      {new Date(act.occurred_at).toLocaleString()}
                    </span>
                  </div>

                  {act.details && Object.keys(act.details).length > 0 && (
                    <div className="mt-2 rounded-xs bg-atlas-surface-1 p-2 font-mono text-[11px] text-atlas-text-primary">
                      {Object.entries(act.details).map(([k, v]) => (
                        <div key={k} className="flex gap-2">
                          <span className="text-atlas-text-muted">{k}:</span>
                          <span>{typeof v === "object" ? JSON.stringify(v) : String(v)}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-1 font-mono text-[10px] text-atlas-text-muted">
                    Actor: {act.actor_user_id}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
