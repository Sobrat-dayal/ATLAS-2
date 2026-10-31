"use client";

import React from "react";
import {
  Radio,
  Building2,
  TrendingUp,
  ShieldAlert,
  Flame,
  CheckCircle2,
  Clock,
  ChevronRight,
  Sliders,
  AlertCircle,
} from "lucide-react";

interface GodsEyeEventFeedProps {
  events: Array<{
    event_id: string;
    category: string;
    title: string;
    occurred_at: string;
    published_at: string;
    ingested_at: string;
    verification_status: string;
    severity: string;
    priority_score?: number;
    priority_tier?: string;
    scoring_factors?: Array<{ name: string; contribution: number }>;
  }>;
  selectedEventId?: string | null;
  onSelectEvent: (eventId: string) => void;
  disclaimerText?: string;
}

export function GodsEyeEventFeed({
  events,
  selectedEventId,
  onSelectEvent,
  disclaimerText,
}: GodsEyeEventFeedProps) {
  const getCategoryIcon = (cat: string) => {
    switch (cat) {
      case "MONETARY_POLICY":
        return <Radio className="w-3.5 h-3.5 text-sky-400" />;
      case "CORPORATE":
      case "FINANCIAL":
        return <Building2 className="w-3.5 h-3.5 text-emerald-400" />;
      case "GEOPOLITICAL":
      case "SANCTIONS":
        return <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />;
      case "NATURAL_DISASTER":
      case "PHYSICAL_WORLD":
        return <Flame className="w-3.5 h-3.5 text-rose-500" />;
      default:
        return <TrendingUp className="w-3.5 h-3.5 text-amber-400" />;
    }
  };

  const getPriorityBadge = (score?: number, tier?: string) => {
    if (score === undefined) return null;
    let colorClass = "bg-zinc-800 text-zinc-300 border-zinc-700";
    if (score >= 80) {
      colorClass = "bg-rose-950/80 text-rose-300 border-rose-800 font-bold";
    } else if (score >= 60) {
      colorClass = "bg-amber-950/80 text-amber-300 border-amber-800 font-bold";
    } else if (score >= 40) {
      colorClass = "bg-sky-950/80 text-sky-300 border-sky-800";
    }

    return (
      <div className={`px-2 py-0.5 rounded border text-[10px] flex items-center gap-1 ${colorClass}`}>
        <Sliders className="w-2.5 h-2.5" />
        <span>{score.toFixed(0)}</span>
        {tier && <span className="opacity-80">({tier})</span>}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-l border-zinc-800 font-mono text-xs select-none">
      {/* Header */}
      <div className="px-3 py-2 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
          <span className="font-semibold text-zinc-200 uppercase tracking-wider text-[11px]">
            Prioritized Event Stream
          </span>
        </div>
        <span className="text-[10px] text-zinc-500 bg-zinc-900 px-1.5 py-0.5 rounded border border-zinc-800">
          {events.length} Events
        </span>
      </div>

      {/* Events List */}
      <div className="flex-1 overflow-y-auto divide-y divide-zinc-900 p-1">
        {events.length === 0 ? (
          <div className="p-6 text-center text-zinc-500 text-xs">
            No events matching the active lens and time filters.
          </div>
        ) : (
          events.map((ev) => {
            const isSelected = selectedEventId === ev.event_id;
            return (
              <div
                key={ev.event_id}
                onClick={() => onSelectEvent(ev.event_id)}
                className={`p-2.5 cursor-pointer rounded transition-all mb-1 ${
                  isSelected
                    ? "bg-zinc-900 border-l-2 border-amber-500 shadow"
                    : "hover:bg-zinc-900/50"
                }`}
              >
                {/* Meta Header */}
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <div className="flex items-center gap-1.5">
                    {getCategoryIcon(ev.category)}
                    <span className="text-[10px] font-semibold text-zinc-400">
                      {ev.category}
                    </span>
                  </div>
                  {getPriorityBadge(ev.priority_score, ev.priority_tier)}
                </div>

                {/* Title */}
                <div className="font-semibold text-zinc-200 text-xs mb-1.5 line-clamp-2">
                  {ev.title}
                </div>

                {/* Scoring Factor Chips */}
                {ev.scoring_factors && ev.scoring_factors.length > 0 && (
                  <div className="flex items-center gap-1 flex-wrap mb-1.5">
                    {ev.scoring_factors.map((f, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[9px] text-zinc-400"
                      >
                        {f.name.replace("_", " ")}: +{f.contribution.toFixed(1)}
                      </span>
                    ))}
                  </div>
                )}

                {/* Timestamp & Verification */}
                <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-1 border-t border-zinc-900">
                  <div className="flex items-center gap-1">
                    <Clock className="w-2.5 h-2.5" />
                    <span>{new Date(ev.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    <span className="text-[9px]">{ev.verification_status}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Bottom Priority Disclaimer */}
      <div className="p-2 border-t border-zinc-900 bg-zinc-950 text-[10px] text-zinc-500 leading-tight">
        {disclaimerText || "Priority scores reflect operational review prioritization, not stock return forecasts or trade signals."}
      </div>
    </div>
  );
}

