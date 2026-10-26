"use client";

import React from "react";
import { History, Calendar, Target, Mic, FileText } from "lucide-react";
import { PolicyTimelineEventDTO } from "@/lib/economics/central-banks";

interface PolicyTimelinePanelProps {
  timeline: PolicyTimelineEventDTO[];
}

export function PolicyTimelinePanel({ timeline }: PolicyTimelinePanelProps) {
  const getEventIcon = (kind: string) => {
    switch (kind) {
      case "RATE_DECISION":
        return <Target className="w-4 h-4 text-emerald-400" />;
      case "SPEECH":
        return <Mic className="w-4 h-4 text-indigo-400" />;
      default:
        return <FileText className="w-4 h-4 text-atlas-accent" />;
    }
  };

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-atlas-accent" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Official Monetary Policy Timeline
          </h3>
        </div>
        <span className="text-xs font-mono text-atlas-text-muted">
          {timeline.length} Chronological Policy Milestones
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-atlas-border-subtle">
        {timeline.map((event) => (
          <div key={event.event_id} className="relative group">
            <div className="absolute -left-6 top-1.5 w-5 h-5 rounded-full bg-atlas-surface border border-atlas-border-subtle flex items-center justify-center shrink-0">
              {getEventIcon(event.event_kind)}
            </div>

            <div className="bg-atlas-background p-4 rounded-lg border border-atlas-border-subtle space-y-1.5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <span className="text-xs font-bold text-atlas-text-primary">
                  {event.title}
                </span>
                <span className="text-[10px] font-mono text-atlas-text-muted">
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>

              <p className="text-xs text-atlas-text-muted leading-relaxed font-sans">
                {event.summary}
              </p>

              {event.rate_change_bps != null && (
                <div className="pt-2">
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border inline-block ${
                      event.rate_change_bps < 0
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : event.rate_change_bps > 0
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        : "bg-blue-500/10 text-blue-400 border-blue-500/20"
                    }`}
                  >
                    {event.rate_change_bps > 0 ? "+" : ""}
                    {event.rate_change_bps} bps
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
