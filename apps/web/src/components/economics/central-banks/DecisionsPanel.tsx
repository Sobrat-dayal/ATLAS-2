"use client";

import React from "react";
import { Target, ExternalLink, Calendar, CheckCircle2 } from "lucide-react";
import { MonetaryPolicyDecisionDTO } from "@/lib/economics/central-banks";

interface DecisionsPanelProps {
  decisions: MonetaryPolicyDecisionDTO[];
  selectedDecisionId: string | null;
  onSelectDecision: (decisionId: string) => void;
}

export function DecisionsPanel({
  decisions,
  selectedDecisionId,
  onSelectDecision,
}: DecisionsPanelProps) {
  const selectedDecision = decisions.find((d) => d.decision_id === selectedDecisionId) || decisions[0];

  const getDecisionBadge = (kind: string) => {
    switch (kind) {
      case "RATE_DECREASE":
        return { label: "RATE CUT", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" };
      case "RATE_INCREASE":
        return { label: "RATE HIKE", color: "bg-rose-500/10 text-rose-400 border-rose-500/20" };
      case "RATE_HOLD":
        return { label: "RATE HOLD", color: "bg-blue-500/10 text-blue-400 border-blue-500/20" };
      default:
        return { label: kind, color: "bg-amber-500/10 text-amber-400 border-amber-500/20" };
    }
  };

  return (
    <div className="space-y-5">
      {/* Decisions Master Table */}
      <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
        <div className="flex items-center justify-between pb-3 border-b border-atlas-border-subtle">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-atlas-accent" />
            <h3 className="text-sm font-semibold text-atlas-text-primary">
              Monetary Policy Decision History
            </h3>
          </div>
          <span className="text-xs font-mono text-atlas-text-muted">
            {decisions.length} Officially Verified Decisions
          </span>
        </div>

        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-atlas-border-subtle bg-atlas-background/50 font-mono text-[11px] text-atlas-text-muted uppercase">
                <th className="py-2.5 px-3">Announced (UTC)</th>
                <th className="py-2.5 px-3">Effective Date</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Instrument</th>
                <th className="py-2.5 px-3 text-right">Change (bps)</th>
                <th className="py-2.5 px-3">Official Identifier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-subtle/50 font-mono">
              {decisions.map((dec) => {
                const isSelected = dec.decision_id === selectedDecision?.decision_id;
                const badge = getDecisionBadge(dec.decision_kind);
                const primaryChange = dec.rate_changes[0];

                return (
                  <tr
                    key={dec.decision_id}
                    onClick={() => onSelectDecision(dec.decision_id)}
                    className={`cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-atlas-accent/10 border-l-2 border-atlas-accent"
                        : "hover:bg-atlas-surface-elevated/40"
                    }`}
                  >
                    <td className="py-3 px-3 font-medium text-atlas-text-primary">
                      {new Date(dec.announced_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-atlas-text-muted">{dec.effective_at}</td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] border font-bold ${badge.color}`}>
                        {badge.label}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[11px] text-atlas-text-muted truncate max-w-[180px]">
                      {dec.affected_instruments.join(", ")}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-sm">
                      {primaryChange && primaryChange.change_bps != null ? (
                        <span
                          className={
                            primaryChange.change_bps < 0
                              ? "text-emerald-400"
                              : primaryChange.change_bps > 0
                              ? "text-rose-400"
                              : "text-blue-400"
                          }
                        >
                          {primaryChange.change_bps > 0 ? "+" : ""}
                          {primaryChange.change_bps} bps
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="py-3 px-3 text-[11px] text-atlas-text-muted">
                      {dec.official_identifier}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Decision Detail Inspector */}
      {selectedDecision && (
        <div className="bg-atlas-surface border border-atlas-border-subtle rounded-lg p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-atlas-border-subtle">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-semibold text-atlas-accent">
                {selectedDecision.official_identifier}
              </span>
              <span className="text-xs font-semibold text-atlas-text-primary">
                — Official Decision Statement Detail
              </span>
            </div>
            <div className="flex items-center gap-2 font-mono text-[11px] text-atlas-text-muted">
              <span>Status: {selectedDecision.publication_status}</span>
              <span>•</span>
              <span>Revision: {selectedDecision.source_revision}</span>
            </div>
          </div>

          <div className="mt-4 space-y-4">
            {/* Rate Changes Detail Table */}
            {selectedDecision.rate_changes.length > 0 && (
              <div className="bg-atlas-background rounded p-3 border border-atlas-border-subtle">
                <span className="text-[10px] font-mono uppercase text-atlas-text-muted block mb-2">
                  Instrument Rate Changes Calculated
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {selectedDecision.rate_changes.map((rc, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded bg-atlas-surface border border-atlas-border-subtle/80 flex items-center justify-between text-xs font-mono"
                    >
                      <div>
                        <span className="font-semibold text-atlas-text-primary block">
                          {rc.instrument_code}
                        </span>
                        <span className="text-[10px] text-atlas-text-muted mt-0.5 block">
                          {rc.previous_lower_bound != null && rc.previous_upper_bound != null
                            ? `${rc.previous_lower_bound}% - ${rc.previous_upper_bound}% → ${rc.new_lower_bound}% - ${rc.new_upper_bound}%`
                            : `${rc.previous_rate ?? "—"}% → ${rc.new_rate ?? "—"}%`}
                        </span>
                      </div>
                      <div className="text-right">
                        <span
                          className={`font-bold px-2 py-0.5 rounded text-xs inline-block ${
                            (rc.change_bps ?? 0) < 0
                              ? "bg-emerald-500/10 text-emerald-400"
                              : (rc.change_bps ?? 0) > 0
                              ? "bg-rose-500/10 text-rose-400"
                              : "bg-blue-500/10 text-blue-400"
                          }`}
                        >
                          {(rc.change_bps ?? 0) > 0 ? "+" : ""}
                          {rc.change_bps} bps
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Official Rationale */}
            <div className="bg-atlas-background rounded p-3 border border-atlas-border-subtle">
              <span className="text-[10px] font-mono uppercase text-atlas-text-muted block mb-1">
                Official Monetary Policy Rationale
              </span>
              <p className="text-xs text-atlas-text-primary leading-relaxed font-sans">
                "{selectedDecision.policy_rationale}"
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
