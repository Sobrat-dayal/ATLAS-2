"use client";

import React from "react";
import {
  Calendar,
  Clock,
  FileText,
  History,
  Info,
  ShieldCheck,
  Building2,
} from "lucide-react";
import { HistoricalTimelineResponseDTO } from "@/lib/companies/supply-chain";

interface RelationshipTimelineProps {
  history: HistoricalTimelineResponseDTO | null;
}

export function RelationshipTimeline({ history }: RelationshipTimelineProps) {
  if (!history || history.events.length === 0) {
    return (
      <div className="p-8 text-center text-atlas-text-muted bg-atlas-surface border border-atlas-border-subtle rounded-md">
        No historical relationship events or timeline milestones recorded.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Temporal Standard Info */}
      <div className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded-md flex items-start gap-3">
        <Info className="w-4 h-4 text-blue-400 mt-0.5 shrink-0" />
        <div className="text-xs text-atlas-text-secondary leading-relaxed">
          <span className="font-semibold text-atlas-text-primary">Temporal Lineage Standard:</span>{" "}
          Timeline records reflect genuine public disclosure milestones (SEC 10-K, 8-K, and authorized corporate releases).
          ATLAS enforces strict point-in-time validity: disclosures are never back-projected before their verified
          publication timestamp. First observation does not imply inception date.
        </div>
      </div>

      {/* Timeline List */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-md p-4">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle mb-4">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-xs font-semibold text-atlas-text-primary">
              Commercial Relationship Timeline & Disclosed Milestones ({history.total_events})
            </h3>
          </div>
          <div className="text-[11px] font-mono text-atlas-text-muted">
            Range: {history.first_observation_date} → {history.latest_observation_date}
          </div>
        </div>

        <div className="relative border-l border-atlas-border-subtle ml-3.5 space-y-6 py-2">
          {history.events.map((evt) => (
            <div key={evt.event_id} className="relative pl-6 group">
              {/* Dot */}
              <div className="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full bg-atlas-accent border-2 border-atlas-surface group-hover:scale-125 transition-transform" />

              <div className="p-3 bg-atlas-surface-subtle/70 border border-atlas-border-subtle rounded-md text-xs hover:border-atlas-accent/50 transition-colors">
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5 pb-1 border-b border-atlas-border-subtle/50">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-[10px] bg-blue-500/10 text-blue-400 px-1.5 py-0.5 rounded font-semibold border border-blue-500/20">
                      {evt.event_type.replace(/_/g, " ")}
                    </span>
                    <span className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                      <Building2 className="w-3.5 h-3.5 text-atlas-text-muted" />
                      {evt.counterparty_name}
                    </span>
                  </div>

                  <span className="font-mono text-[11px] text-atlas-text-muted flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {evt.event_date}
                  </span>
                </div>

                <div className="text-atlas-text-secondary leading-relaxed mb-2">
                  {evt.description}
                </div>

                <div className="flex items-center justify-between text-[10px] text-atlas-text-muted font-mono pt-1 border-t border-atlas-border-subtle/40">
                  <span className="flex items-center gap-1">
                    <FileText className="w-3 h-3 text-atlas-text-muted" />
                    Reference: {evt.source_reference}
                  </span>
                  <span className="text-emerald-400 flex items-center gap-1">
                    <ShieldCheck className="w-2.5 h-2.5" />
                    {evt.verification_status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
