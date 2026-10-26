"use client";

import React from "react";
import {
  ShieldCheck,
  Building2,
  DollarSign,
  FileText,
  Clock,
  AlertTriangle,
  HelpCircle,
  ExternalLink,
  ArrowRight,
  History,
  CheckCircle2,
} from "lucide-react";
import {
  NewsFinancialEventDTO,
  NewsEventEvidenceDTO,
  EventParticipantRole,
} from "@/lib/news/types";
import { formatUtcDateTime } from "@/lib/news/formatting";

interface NewsEventInspectorProps {
  event: NewsFinancialEventDTO | null;
  evidence: NewsEventEvidenceDTO[];
  isLoading: boolean;
  onNavigateEntity?: (entityId: string, entityType: string, ticker?: string | null) => void;
  onNavigateStory?: (storyId: string) => void;
}

export function NewsEventInspector({
  event,
  evidence,
  isLoading,
  onNavigateEntity,
  onNavigateStory,
}: NewsEventInspectorProps) {
  if (!event) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-center h-full min-h-[400px]">
        <ShieldCheck className="w-10 h-10 text-zinc-300 dark:text-zinc-700 mb-3" />
        <h3 className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
          No Financial Event Selected
        </h3>
        <p className="text-xs text-zinc-500 max-w-xs mt-1">
          Select an evidenced corporate or macro event to inspect participants, reported transaction amounts, and structured source citations.
        </p>
      </div>
    );
  }

  const getRoleLabel = (role: EventParticipantRole) => {
    switch (role) {
      case "PRIMARY_SUBJECT":
        return "Primary Subject";
      case "ACQUIRER":
        return "Acquiring Party";
      case "TARGET":
        return "Target Company";
      case "REGULATOR":
        return "Regulatory Authority";
      case "ISSUER":
        return "Security Issuer";
      case "INVESTOR":
        return "Lead Investor";
      case "UNDERWRITER":
        return "Underwriting Syndicate";
      default:
        return role.replace(/_/g, " ");
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded shadow-sm overflow-hidden font-sans">
      {/* Header */}
      <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/60 dark:bg-zinc-950/40">
        <div className="flex items-center justify-between text-[11px] font-mono text-zinc-500 mb-1.5">
          <span className="flex items-center space-x-1.5 text-amber-600 dark:text-amber-400 font-semibold">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{event.event_id}</span>
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
            {event.event_type.replace(/_/g, " ")}
          </span>
        </div>

        <h2 className="text-base font-bold text-zinc-900 dark:text-zinc-100 leading-snug">
          {event.event_title}
        </h2>

        {/* Primary Subject */}
        <div className="mt-2.5 flex items-center justify-between pt-2 border-t border-zinc-200/60 dark:border-zinc-800/60">
          <div className="flex items-center space-x-1.5">
            <Building2 className="w-4 h-4 text-zinc-400" />
            <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
              {event.primary_entity_name}
            </span>
          </div>
          {event.primary_entity_id && onNavigateEntity && (
            <button
              type="button"
              onClick={() => onNavigateEntity(event.primary_entity_id, "COMPANY")}
              className="text-[11px] font-mono text-cyan-600 dark:text-cyan-400 hover:underline inline-flex items-center space-x-1"
            >
              <span>View Entity</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Assertion & Lifecycle Qualification Banner */}
      <div className="p-3 bg-zinc-50 dark:bg-zinc-950 border-b border-zinc-200 dark:border-zinc-800 flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
        <div className="flex items-center space-x-2">
          <span className="text-zinc-500 text-[11px]">ASSERTION:</span>
          <span
            className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
              event.assertion_status === "OFFICIALLY_REPORTED"
                ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30"
                : event.assertion_status === "RUMORED"
                ? "bg-purple-500/15 text-purple-700 dark:text-purple-300 border border-purple-500/30"
                : "bg-amber-500/15 text-amber-700 dark:text-amber-300 border border-amber-500/30"
            }`}
          >
            {event.assertion_status}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-zinc-500 text-[11px]">LIFECYCLE:</span>
          <span
            className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
              event.lifecycle_status === "COMPLETED"
                ? "bg-emerald-600 text-white"
                : event.lifecycle_status === "ANNOUNCED"
                ? "bg-blue-600 text-white"
                : "bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200"
            }`}
          >
            {event.lifecycle_status}
          </span>
        </div>
      </div>

      {/* Uncertainty Notice for Rumors / Allegations */}
      {event.assertion_status === "RUMORED" && (
        <div className="p-3 bg-purple-50 dark:bg-purple-950/20 border-b border-purple-200 dark:border-purple-900/30 flex items-start space-x-2 text-xs text-purple-900 dark:text-purple-200 font-sans">
          <HelpCircle className="w-4 h-4 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
          <p className="leading-snug">
            <strong>Unverified Reporting:</strong> This event is reported by journalistic sources citing unnamed persons or preliminary talks. It does not establish that a binding corporate agreement has been executed.
          </p>
        </div>
      )}

      {/* Main Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Reported Amounts */}
        {event.amounts.length > 0 && (
          <div>
            <h4 className="text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wide mb-2 flex items-center space-x-1.5">
              <DollarSign className="w-3.5 h-3.5 text-emerald-500" />
              <span>Source-Evidenced Financial Magnitude</span>
            </h4>
            <div className="p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/60 dark:bg-zinc-900/60 space-y-1.5">
              {event.amounts.map((amt, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="text-zinc-600 dark:text-zinc-400 font-mono text-[11px]">
                    {amt.amount_type.replace(/_/g, " ")}:
                  </span>
                  <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">
                    {amt.currency === "PERCENT"
                      ? `${amt.amount_value}%`
                      : `$${amt.amount_value.toLocaleString()} ${amt.currency}`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Verified Event Participants */}
        <div>
          <h4 className="text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wide mb-2 flex items-center space-x-1.5">
            <Building2 className="w-3.5 h-3.5 text-zinc-400" />
            <span>Participating Entities ({event.participants.length})</span>
          </h4>
          <div className="border border-zinc-200 dark:border-zinc-800 rounded divide-y divide-zinc-200 dark:divide-zinc-800/60 text-xs">
            {event.participants.map((p, idx) => (
              <div key={idx} className="p-2.5 flex items-center justify-between hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                <div>
                  <span className="font-semibold text-zinc-900 dark:text-zinc-100 block">
                    {p.canonical_name}
                  </span>
                  <span className="text-[10px] font-mono text-zinc-500">
                    {p.entity_id}
                  </span>
                </div>
                <div className="text-right">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300">
                    {getRoleLabel(p.role)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Structured Evidence Records */}
        <div>
          <h4 className="text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wide mb-2 flex items-center space-x-1.5">
            <FileText className="w-3.5 h-3.5 text-zinc-400" />
            <span>Supporting Source Evidence ({evidence.length} Citations)</span>
          </h4>

          {isLoading ? (
            <div className="py-4 text-center text-xs font-mono text-zinc-400">
              Loading source citations...
            </div>
          ) : evidence.length === 0 ? (
            <div className="py-4 text-center text-xs text-zinc-500">
              No evidence records found.
            </div>
          ) : (
            <div className="space-y-2.5">
              {evidence.map((evd) => {
                return (
                  <div
                    key={evd.evidence_id}
                    className="p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                      <span className="font-semibold text-zinc-800 dark:text-zinc-200">
                        {evd.publisher_name}
                      </span>
                      <span>{formatUtcDateTime(evd.source_published_at)}</span>
                    </div>

                    <p className="font-medium text-zinc-900 dark:text-zinc-100">
                      {evd.headline}
                    </p>

                    {evd.permitted_excerpt && (
                      <p className="text-[11px] text-zinc-600 dark:text-zinc-400 italic bg-white dark:bg-zinc-950 p-2 rounded border border-zinc-200/60 dark:border-zinc-800/60">
                        &ldquo;{evd.permitted_excerpt}&rdquo;
                      </p>
                    )}

                    <div className="flex items-center justify-between pt-1 border-t border-zinc-200/60 dark:border-zinc-800/60 text-[10px] font-mono text-zinc-500">
                      <span>Doc Type: {evd.evidence_type}</span>
                      <span className="text-zinc-400">{evd.evidence_id}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Lifecycle Revisions Audit Trail */}
        {event.revisions.length > 0 && (
          <div>
            <h4 className="text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wide mb-2 flex items-center space-x-1.5">
              <History className="w-3.5 h-3.5 text-zinc-400" />
              <span>Lifecycle Audit Trail ({event.revisions.length})</span>
            </h4>
            <div className="space-y-2 border-l-2 border-zinc-200 dark:border-zinc-800 pl-3">
              {event.revisions.map((rev) => (
                <div key={rev.revision_id} className="text-xs space-y-0.5">
                  <div className="flex items-center space-x-2 text-[10px] font-mono text-zinc-500">
                    <span>{formatUtcDateTime(rev.timestamp)}</span>
                    <span>•</span>
                    <span className="text-zinc-700 dark:text-zinc-300 font-semibold">{rev.change_reason}</span>
                  </div>
                  <div className="text-[11px] text-zinc-700 dark:text-zinc-300">
                    Status: <span className="font-semibold">{rev.new_lifecycle_status}</span> ({rev.new_assertion_status})
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
