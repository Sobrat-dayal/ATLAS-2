"use client";

import React from "react";
import {
  ShieldAlert,
  ShieldCheck,
  Building2,
  DollarSign,
  FileText,
  AlertTriangle,
  HelpCircle,
  Clock,
  Sparkles,
} from "lucide-react";
import {
  NewsFinancialEventDTO,
  FinancialEventType,
  NewsEventLifecycleStatus,
  NewsEventAssertionStatus,
} from "@/lib/news/types";
import { formatUtcDate } from "@/lib/news/formatting";

interface NewsFinancialEventTableProps {
  events: NewsFinancialEventDTO[];
  selectedEvent: NewsFinancialEventDTO | null;
  onSelectEvent: (event: NewsFinancialEventDTO) => void;
  isLoading: boolean;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
}

export function NewsFinancialEventTable({
  events,
  selectedEvent,
  onSelectEvent,
  isLoading,
  onNavigateEntity,
}: NewsFinancialEventTableProps) {
  if (isLoading && events.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center">
        <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mb-3" />
        <p className="text-xs font-mono text-zinc-500 dark:text-zinc-400">
          Extracting source-evidenced corporate and macro events...
        </p>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="p-8 text-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded">
        <ShieldCheck className="w-8 h-8 text-zinc-400 mx-auto mb-2" />
        <h3 className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">
          No Verified Financial Events Found
        </h3>
        <p className="text-xs text-zinc-500 mt-1">
          No financial events meet the strict evidence and taxonomy classification criteria for the current filter.
        </p>
      </div>
    );
  }

  const getAssertionBadge = (status: NewsEventAssertionStatus) => {
    switch (status) {
      case "OFFICIALLY_REPORTED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
            OFFICIAL
          </span>
        );
      case "THIRD_PARTY_REPORTED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
            REPORTED
          </span>
        );
      case "RUMORED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
            <HelpCircle className="w-2.5 h-2.5 mr-0.5" />
            RUMOR
          </span>
        );
      case "ALLEGED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            <AlertTriangle className="w-2.5 h-2.5 mr-0.5" />
            ALLEGED
          </span>
        );
      case "DISPUTED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20">
            <ShieldAlert className="w-2.5 h-2.5 mr-0.5" />
            DISPUTED
          </span>
        );
      case "CORRECTED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-orange-500/10 text-orange-600 dark:text-orange-400 border border-orange-500/20">
            CORRECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono bg-zinc-100 text-zinc-600">
            {status}
          </span>
        );
    }
  };

  const getLifecycleBadge = (status: NewsEventLifecycleStatus) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-500 text-white">
            COMPLETED
          </span>
        );
      case "ANNOUNCED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-500/15 text-blue-700 dark:text-blue-300 border border-blue-500/30">
            ANNOUNCED
          </span>
        );
      case "PROPOSED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
            PROPOSED
          </span>
        );
      case "PENDING":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30">
            PENDING
          </span>
        );
      case "CANCELLED":
        return (
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium bg-rose-500/10 text-rose-600 border border-rose-500/20">
            CANCELLED
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono text-zinc-500">
            {status}
          </span>
        );
    }
  };

  const formatAmount = (ev: NewsFinancialEventDTO) => {
    if (!ev.amounts || ev.amounts.length === 0) return null;
    const a = ev.amounts[0];
    if (a.currency === "PERCENT") {
      return `${a.amount_value}%`;
    }
    if (a.amount_value >= 1_000_000_000) {
      return `$${(a.amount_value / 1_000_000_000).toFixed(1)}B ${a.currency}`;
    }
    if (a.amount_value >= 1_000_000) {
      return `$${(a.amount_value / 1_000_000).toFixed(1)}M ${a.currency}`;
    }
    return `$${a.amount_value.toLocaleString()} ${a.currency}`;
  };

  return (
    <div className="overflow-x-auto bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/80 dark:bg-zinc-900/80 text-[11px] font-mono text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
            <th className="py-2.5 px-3 font-semibold w-28">Event Date</th>
            <th className="py-2.5 px-3 font-semibold">Financial Event / Title</th>
            <th className="py-2.5 px-3 font-semibold w-40">Primary Subject</th>
            <th className="py-2.5 px-3 font-semibold w-28">Assertion</th>
            <th className="py-2.5 px-3 font-semibold w-28">Lifecycle</th>
            <th className="py-2.5 px-3 font-semibold w-32 text-right">Amount</th>
            <th className="py-2.5 px-3 font-semibold w-20 text-center">Evidence</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/60 text-xs font-sans">
          {events.map((ev) => {
            const isSelected = selectedEvent?.event_id === ev.event_id;
            const amtStr = formatAmount(ev);

            return (
              <tr
                key={ev.event_id}
                onClick={() => onSelectEvent(ev)}
                className={`cursor-pointer transition-colors ${
                  isSelected
                    ? "bg-amber-50/70 dark:bg-amber-950/30 border-l-2 border-l-amber-500"
                    : "hover:bg-zinc-50/70 dark:hover:bg-zinc-800/40"
                }`}
              >
                {/* Event Date */}
                <td className="py-3 px-3 font-mono text-[11px] text-zinc-600 dark:text-zinc-400 whitespace-nowrap">
                  {formatUtcDate(ev.event_date)}
                </td>

                {/* Event Title & Type Badge */}
                <td className="py-3 px-3">
                  <div className="flex flex-col space-y-1">
                    <span className="font-medium text-zinc-900 dark:text-zinc-100 line-clamp-2 leading-snug">
                      {ev.event_title}
                    </span>
                    <div className="flex items-center space-x-2 text-[10px] font-mono">
                      <span className="text-zinc-400 dark:text-zinc-500">{ev.event_id}</span>
                      <span>•</span>
                      <span className="text-amber-700 dark:text-amber-400 font-semibold uppercase">
                        {ev.event_type.replace(/_/g, " ")}
                      </span>
                    </div>
                  </div>
                </td>

                {/* Primary Subject */}
                <td className="py-3 px-3">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (ev.primary_entity_id && onNavigateEntity) {
                        onNavigateEntity(ev.primary_entity_id, "COMPANY");
                      }
                    }}
                    className="inline-flex items-center space-x-1.5 text-zinc-800 dark:text-zinc-200 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors font-medium text-left"
                  >
                    <Building2 className="w-3.5 h-3.5 text-zinc-400 flex-shrink-0" />
                    <span className="truncate max-w-[140px]">{ev.primary_entity_name}</span>
                  </button>
                </td>

                {/* Assertion Level */}
                <td className="py-3 px-3">{getAssertionBadge(ev.assertion_status)}</td>

                {/* Lifecycle Status */}
                <td className="py-3 px-3">{getLifecycleBadge(ev.lifecycle_status)}</td>

                {/* Sourced Amount */}
                <td className="py-3 px-3 text-right font-mono text-[11px]">
                  {amtStr ? (
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">
                      {amtStr}
                    </span>
                  ) : (
                    <span className="text-zinc-400">—</span>
                  )}
                </td>

                {/* Evidence Count */}
                <td className="py-3 px-3 text-center">
                  <span
                    className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300"
                    title={`${ev.evidence_records.length} structured citation records`}
                  >
                    <FileText className="w-3 h-3 text-zinc-400" />
                    <span>{ev.evidence_records.length}</span>
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
