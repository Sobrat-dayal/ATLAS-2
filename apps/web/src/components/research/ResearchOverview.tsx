"use client";

import React from "react";
import { Badge, Button } from "@/design-system";
import { ResearchInvestigation, ResearchOverviewSummary } from "@/lib/research/types";

interface ResearchOverviewProps {
  overview: ResearchOverviewSummary | null;
  isLoading: boolean;
  onSelectInvestigation: (id: string) => void;
  onNewInvestigation: () => void;
  onViewAllInvestigations: () => void;
}

export function ResearchOverview({
  overview,
  isLoading,
  onSelectInvestigation,
  onNewInvestigation,
  onViewAllInvestigations,
}: ResearchOverviewProps) {
  if (isLoading && !overview) {
    return (
      <div className="flex h-64 items-center justify-center text-xs text-atlas-text-muted">
        Loading research workspace overview...
      </div>
    );
  }

  const active = overview?.active_investigations_count ?? 0;
  const draft = overview?.draft_investigations_count ?? 0;
  const completed = overview?.completed_investigations_count ?? 0;
  const notesCount = overview?.total_notes_count ?? 0;
  const sourcesCount = overview?.total_sources_count ?? 0;
  const evidenceCount = overview?.total_evidence_count ?? 0;
  const recentInvs = overview?.recent_investigations ?? [];
  const recentActs = overview?.recent_activities ?? [];

  return (
    <div className="space-y-4 p-4">
      {/* Metric Stat Cards */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Active</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-accent">{active}</div>
          <div className="text-[10px] text-atlas-text-muted">In-progress inquiries</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Drafts</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-text-secondary">{draft}</div>
          <div className="text-[10px] text-atlas-text-muted">Scoping in preparation</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Completed</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-positive">{completed}</div>
          <div className="text-[10px] text-atlas-text-muted">Concluded investigations</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Structured Notes</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-text-primary">{notesCount}</div>
          <div className="text-[10px] text-atlas-text-muted">Analyst thesis docs</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Linked Sources</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-text-primary">{sourcesCount}</div>
          <div className="text-[10px] text-atlas-text-muted">Filings, facts & news</div>
        </div>

        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-3">
          <div className="text-[11px] font-medium uppercase tracking-wider text-atlas-text-muted">Verified Evidence</div>
          <div className="mt-1 font-mono text-xl font-bold text-atlas-text-primary">{evidenceCount}</div>
          <div className="text-[10px] text-atlas-text-muted">Citable location links</div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Recent Investigations (2 cols) */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-atlas-border-default px-4 py-2.5">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
                Ongoing Investigations
              </h2>
              <p className="text-[11px] text-atlas-text-muted">Recent analyst workspaces and research projects</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="xs" onClick={onViewAllInvestigations}>
                View All →
              </Button>
              <Button variant="secondary" size="xs" onClick={onNewInvestigation}>
                + New
              </Button>
            </div>
          </div>

          <div className="divide-y divide-atlas-border-default">
            {recentInvs.length === 0 ? (
              <div className="p-8 text-center text-xs text-atlas-text-muted">
                No research investigations created yet. Click "+ New" to begin.
              </div>
            ) : (
              recentInvs.map((inv) => (
                <div
                  key={inv.investigation_id}
                  onClick={() => onSelectInvestigation(inv.investigation_id)}
                  className="group flex cursor-pointer items-center justify-between p-3.5 transition-colors hover:bg-atlas-surface-hover"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-atlas-text-primary group-hover:text-atlas-accent">
                        {inv.title}
                      </span>
                      {inv.primary_subject_entity_id && (
                        <Badge variant="primary" className="font-mono text-[10px]">
                          {inv.primary_subject_entity_id}
                        </Badge>
                      )}
                      <Badge
                        variant={
                          inv.status === "ACTIVE"
                            ? "positive"
                            : inv.status === "COMPLETED"
                            ? "default"
                            : "outline"
                        }
                        className="text-[10px]"
                      >
                        {inv.status}
                      </Badge>
                    </div>
                    {inv.research_objective && (
                      <p className="line-clamp-1 text-[11px] text-atlas-text-secondary">
                        {inv.research_objective}
                      </p>
                    )}
                    <div className="flex items-center gap-3 font-mono text-[10px] text-atlas-text-muted">
                      <span>{inv.research_type.replace(/_/g, " ")}</span>
                      <span>•</span>
                      <span>{inv.notes_count} Notes</span>
                      <span>•</span>
                      <span>{inv.sources_count} Sources</span>
                      <span>•</span>
                      <span>{inv.evidence_count} Evidence</span>
                      <span>•</span>
                      <span>Rev v{inv.revision}</span>
                    </div>
                  </div>

                  <div className="shrink-0 pl-3">
                    <Button variant="secondary" size="xs">
                      Open Console →
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Activity Timeline (1 col) */}
        <div className="rounded-sm border border-atlas-border-default bg-atlas-surface-1">
          <div className="border-b border-atlas-border-default px-4 py-2.5">
            <h2 className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
              Recent Activity Feed
            </h2>
            <p className="text-[11px] text-atlas-text-muted">Chronological record of research events</p>
          </div>

          <div className="max-h-[380px] overflow-y-auto divide-y divide-atlas-border-default/60 p-2">
            {recentActs.length === 0 ? (
              <div className="p-4 text-center text-xs text-atlas-text-muted">
                No activity recorded yet.
              </div>
            ) : (
              recentActs.map((act) => (
                <div key={act.activity_id} className="p-2 text-xs">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="font-mono text-[9px]">
                      {act.action_type.replace(/_/g, " ")}
                    </Badge>
                    <span className="font-mono text-[10px] text-atlas-text-muted">
                      {new Date(act.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  <div className="mt-1 text-[11px] text-atlas-text-primary">
                    <span className="font-mono text-atlas-text-secondary">[{act.object_type}]</span>{" "}
                    {act.details?.title || act.details?.statement || act.details?.location || act.object_id}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
