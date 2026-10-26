"use client";

import React from "react";
import {
  EconomicCalendarEventDetailDTO,
  EconomicCalendarEventDTO,
} from "@/lib/economics/calendar";
import { EconomicSurpriseBadge } from "./EconomicSurpriseBadge";
import {
  X,
  ExternalLink,
  ShieldCheck,
  Clock,
  Calendar,
  Layers,
  FileText,
  AlertTriangle,
  Bell,
  CheckCircle2,
  Info,
} from "lucide-react";

interface EconomicEventDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  detail: EconomicCalendarEventDetailDTO | null;
  isLoading: boolean;
  onToggleAlert: (event: EconomicCalendarEventDTO) => void;
  hasAlert: boolean;
}

export function EconomicEventDetailModal({
  isOpen,
  onClose,
  detail,
  isLoading,
  onToggleAlert,
  hasAlert,
}: EconomicEventDetailModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div
        className="bg-atlas-background border border-atlas-border-subtle rounded-lg max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-atlas-border-subtle bg-atlas-surface/80">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-atlas-accent/15 text-atlas-accent">
              <Calendar className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-atlas-text-primary tracking-tight">
                {detail?.event.title || "Economic Release Event Details"}
              </h2>
              <div className="flex items-center gap-2 text-[10px] font-mono text-atlas-text-muted mt-0.5">
                <span>{detail?.event.official_event_identifier}</span>
                <span>•</span>
                <span>{detail?.event.official_source_name}</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-atlas-text-muted hover:text-atlas-text-primary hover:bg-atlas-surface transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-5 text-xs text-atlas-text-secondary">
          {isLoading || !detail ? (
            <div className="py-12 flex flex-col items-center justify-center gap-2 text-atlas-text-muted">
              <div className="w-6 h-6 border-2 border-atlas-accent border-t-transparent rounded-full animate-spin" />
              <p className="font-mono text-xs">Retrieving official release metadata...</p>
            </div>
          ) : (
            <>
              {/* Event Metadata Banner */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded bg-atlas-surface border border-atlas-border-subtle">
                <div>
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Scheduled Time
                  </span>
                  <span className="font-mono font-semibold text-atlas-text-primary">
                    {detail.event.scheduled_start_display}
                  </span>
                  <span className="text-[10px] text-atlas-text-muted block">
                    {detail.event.display_timezone}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Source Jurisdiction
                  </span>
                  <span className="font-mono font-semibold text-atlas-text-primary">
                    {detail.event.geographic_entity_ids.join(", ")}
                  </span>
                  <span className="text-[10px] text-atlas-text-muted block">
                    TZ: {detail.event.source_timezone}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Reference Period
                  </span>
                  <span className="font-mono font-semibold text-atlas-text-primary">
                    {detail.event.reference_period}
                  </span>
                  <span className="text-[10px] text-atlas-text-muted block">
                    Stage: {detail.event.release_stage}
                  </span>
                </div>

                <div>
                  <span className="text-[10px] uppercase font-mono text-atlas-text-muted block">
                    Publication Status
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 font-mono font-bold text-[11px] ${
                      detail.event.is_verified ? "text-emerald-400" : "text-blue-400"
                    }`}
                  >
                    {detail.event.is_verified && <CheckCircle2 className="w-3 h-3" />}
                    {detail.event.event_status}
                  </span>
                  <span className="text-[10px] text-atlas-text-muted block">
                    {detail.event.is_verified ? "Official source verified" : "Schedule confirmed"}
                  </span>
                </div>
              </div>

              {/* Published Observations Section */}
              <div>
                <h3 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-atlas-accent" />
                  <span>Published Statistical Observations ({detail.observations.length})</span>
                </h3>
                {detail.observations.length > 0 ? (
                  <div className="border border-atlas-border-subtle rounded overflow-hidden">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-atlas-surface border-b border-atlas-border-subtle text-[10px] font-mono text-atlas-text-muted uppercase">
                          <th className="py-2 px-3">Series / Indicator</th>
                          <th className="py-2 px-2">Ref Period</th>
                          <th className="py-2 px-3 text-right">Actual</th>
                          <th className="py-2 px-3 text-right">Previous</th>
                          <th className="py-2 px-3 text-right">Rev Previous</th>
                          <th className="py-2 px-2 text-right">Unit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-atlas-border-subtle/60">
                        {detail.observations.map((obs) => (
                          <tr key={obs.observation_id} className="hover:bg-atlas-surface/40 font-mono">
                            <td className="py-2 px-3 font-medium text-atlas-text-primary">
                              {obs.indicator_name}
                            </td>
                            <td className="py-2 px-2 text-atlas-text-muted">{obs.reference_period}</td>
                            <td className="py-2 px-3 text-right font-bold text-atlas-text-primary">
                              {obs.actual_value !== null && obs.actual_value !== undefined
                                ? obs.actual_value.toLocaleString()
                                : "—"}
                            </td>
                            <td className="py-2 px-3 text-right text-atlas-text-secondary">
                              {obs.previous_value !== null && obs.previous_value !== undefined
                                ? obs.previous_value.toLocaleString()
                                : "—"}
                            </td>
                            <td className="py-2 px-3 text-right text-amber-400">
                              {obs.revised_previous_value !== null &&
                              obs.revised_previous_value !== undefined &&
                              obs.revised_previous_value !== obs.previous_value
                                ? obs.revised_previous_value.toLocaleString()
                                : "—"}
                            </td>
                            <td className="py-2 px-2 text-right text-atlas-text-muted text-[11px]">
                              {obs.unit}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-atlas-text-muted italic">
                    No individual series observations attached to this release yet.
                  </p>
                )}
              </div>

              {/* Consensus Forecasts Section */}
              <div>
                <h3 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-blue-400" />
                  <span>Pre-Release Consensus Forecasts ({detail.consensus_snapshots.length})</span>
                </h3>
                {detail.consensus_snapshots.length > 0 ? (
                  <div className="border border-atlas-border-subtle rounded overflow-hidden">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-atlas-surface border-b border-atlas-border-subtle text-[10px] font-mono text-atlas-text-muted uppercase">
                          <th className="py-2 px-3">Provider</th>
                          <th className="py-2 px-2">Method</th>
                          <th className="py-2 px-2 text-center">Contributors</th>
                          <th className="py-2 px-3 text-right">Consensus</th>
                          <th className="py-2 px-2 text-right">Unit</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-atlas-border-subtle/60">
                        {detail.consensus_snapshots.map((snap) => (
                          <tr key={snap.snapshot_id} className="hover:bg-atlas-surface/40 font-mono">
                            <td className="py-2 px-3 font-medium text-atlas-text-primary">
                              {snap.provider_name}
                            </td>
                            <td className="py-2 px-2 text-atlas-text-muted text-[11px]">
                              {snap.aggregation_method}
                            </td>
                            <td className="py-2 px-2 text-center text-atlas-text-secondary">
                              {snap.contributor_count || "—"}
                            </td>
                            <td className="py-2 px-3 text-right font-bold text-atlas-text-primary">
                              {snap.consensus_value.toLocaleString()}
                            </td>
                            <td className="py-2 px-2 text-right text-atlas-text-muted text-[11px]">
                              {snap.unit}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="text-xs text-atlas-text-muted italic">
                    No licensed consensus forecast snapshot available for this release.
                  </p>
                )}
              </div>

              {/* Statistical Surprises Breakdown */}
              {detail.surprises.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-atlas-text-primary uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Verified Economic Surprises</span>
                  </h3>
                  <div className="space-y-2">
                    {detail.surprises.map((s, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-atlas-text-primary font-mono">
                              Series: {s.economic_series_id}
                            </span>
                            <EconomicSurpriseBadge surprise={s} />
                          </div>
                          <div className="text-[11px] text-atlas-text-muted mt-1 font-mono">
                            Actual: {s.actual_value.toLocaleString()} {s.unit} vs Consensus:{" "}
                            {s.consensus_value.toLocaleString()} {s.unit}
                          </div>
                        </div>
                        <span className="text-[10px] font-mono text-atlas-text-muted">
                          Algorithm: {s.methodology_version}
                        </span>
                      </div>
                    ))}
                    <div className="p-2.5 rounded bg-blue-500/10 border border-blue-500/20 text-[11px] text-blue-300 flex items-start gap-2">
                      <Info className="w-4 h-4 shrink-0 text-blue-400 mt-0.5" />
                      <span>
                        Economic surprises measure statistical divergence from pre-release consensus forecasts. Numerical surprise sign does not dictate mechanical financial asset price direction.
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Schedule Revision History (if rescheduled) */}
              {detail.schedule_revisions.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Official Schedule Revision History</span>
                  </h3>
                  <div className="space-y-1.5">
                    {detail.schedule_revisions.map((rev) => (
                      <div
                        key={rev.revision_id}
                        className="p-2.5 rounded bg-amber-500/10 border border-amber-500/20 text-xs font-mono"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-amber-300">
                            Rescheduled: {new Date(rev.previous_scheduled_time).toLocaleString()} →{" "}
                            {new Date(rev.new_scheduled_time).toLocaleString()}
                          </span>
                          <span className="text-[10px] text-atlas-text-muted">
                            Recorded {new Date(rev.revised_at).toLocaleDateString()}
                          </span>
                        </div>
                        {rev.reason && (
                          <p className="text-[11px] text-atlas-text-secondary mt-1">
                            Reason: {rev.reason}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Official Source & Provenance */}
              <div className="p-3 bg-atlas-surface/60 border border-atlas-border-subtle rounded flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                  <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>Official Agency: {detail.event.official_source_name}</span>
                  </div>
                  <div className="text-[10px] font-mono text-atlas-text-muted mt-0.5">
                    Provenance ID: {detail.provenance_id} • Source Revision: {detail.source_revision}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href={detail.event.official_source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-text-primary hover:border-atlas-accent text-xs font-medium transition-colors"
                  >
                    <span>Source Release URL</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-3 border-t border-atlas-border-subtle bg-atlas-surface/80 flex items-center justify-between">
          {detail && (
            <button
              onClick={() => onToggleAlert(detail.event)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                hasAlert
                  ? "bg-amber-500/15 border border-amber-500/30 text-amber-400 hover:bg-amber-500/25"
                  : "bg-atlas-accent text-white hover:bg-atlas-accent/90"
              }`}
            >
              <Bell className={`w-3.5 h-3.5 ${hasAlert ? "fill-current" : ""}`} />
              <span>{hasAlert ? "Manage Active Alert" : "Set Release Reminder"}</span>
            </button>
          )}
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded bg-atlas-surface border border-atlas-border-subtle text-atlas-text-secondary hover:text-atlas-text-primary text-xs font-medium transition-colors ml-auto"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
