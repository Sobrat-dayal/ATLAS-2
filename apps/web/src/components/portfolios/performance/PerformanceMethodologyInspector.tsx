"use client";

import React from "react";
import { formatCurrency, formatRate } from "@/lib/portfolios/performance/formatting";
import { PerformanceResponse } from "@/lib/portfolios/performance/types";
import { CheckCircle2, Code2, Hash, Layers, ShieldCheck, X } from "lucide-react";

interface PerformanceMethodologyInspectorProps {
  summary: PerformanceResponse;
  isOpen: boolean;
  onClose: () => void;
}

export function PerformanceMethodologyInspector({
  summary,
  isOpen,
  onClose,
}: PerformanceMethodologyInspectorProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-xs">
      <div className="relative max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-sm border border-atlas-border-default bg-atlas-surface-1 p-5 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-atlas-border-default/60 pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-atlas-accent" />
            <div>
              <h3 className="text-sm font-semibold text-atlas-text-primary">
                Institutional Performance Methodology & Audit Inspector
              </h3>
              <p className="text-[11px] text-atlas-text-secondary">
                Mathematical specifications, day-count conventions, and cryptographic input provenance.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xs p-1 text-atlas-text-tertiary hover:bg-atlas-surface-2 hover:text-atlas-text-primary"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content */}
        <div className="mt-4 space-y-4 text-xs">
          {/* Section 1: Cryptographic Provenance */}
          <div className="rounded-sm border border-atlas-border-default/60 bg-atlas-surface-2/40 p-3">
            <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary">
              <Hash className="h-4 w-4 text-atlas-accent" />
              Calculation Run Provenance & Integrity
            </div>
            <div className="mt-2 grid grid-cols-2 gap-2 font-mono text-[11px]">
              <div>
                <span className="text-atlas-text-tertiary">Run ID:</span>{" "}
                <span className="text-atlas-text-primary">{summary.run_id}</span>
              </div>
              <div>
                <span className="text-atlas-text-tertiary">Version:</span>{" "}
                <span className="text-atlas-text-primary">v{summary.calculation_version}</span>
              </div>
              <div className="col-span-2">
                <span className="text-atlas-text-tertiary">Input SHA-256 Hash:</span>{" "}
                <span className="text-atlas-accent break-all">{summary.input_hash}</span>
              </div>
            </div>
          </div>

          {/* Section 2: Mathematical Formulations */}
          <div className="space-y-2">
            <h4 className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
              <Code2 className="h-4 w-4 text-atlas-accent" />
              Exact Formulations Used
            </h4>

            <div className="space-y-2 rounded-sm border border-atlas-border-default/50 bg-atlas-surface-2/30 p-3">
              <div>
                <div className="font-semibold text-atlas-text-primary">
                  1. Time-Weighted Return (Exact Daily / Subperiod Geometric Compounding)
                </div>
                <div className="mt-1 font-mono text-[11px] text-atlas-text-secondary bg-atlas-surface-3/50 p-2 rounded-xs">
                  R_twr = &prod; (1 + R_i) - 1 &nbsp;&nbsp;|&nbsp;&nbsp; R_i = (V_end,pre - V_start) / V_start
                </div>
                <p className="mt-1 text-[11px] text-atlas-text-tertiary">
                  Portfolio is segmented strictly at external cash flow boundaries. Internal trades, cash dividends, and interest do not break subperiods.
                </p>
              </div>

              <div className="border-t border-atlas-border-default/30 pt-2">
                <div className="font-semibold text-atlas-text-primary">
                  2. Money-Weighted Return (MWR / XIRR)
                </div>
                <div className="mt-1 font-mono text-[11px] text-atlas-text-secondary bg-atlas-surface-3/50 p-2 rounded-xs">
                  &sum; [ C_t / (1 + r)^((d_t - d_0) / 365) ] = 0
                </div>
                <p className="mt-1 text-[11px] text-atlas-text-tertiary">
                  Solved using bounded Newton-Raphson iteration with bisection fallback under ACT/365 day-count convention.
                </p>
              </div>

              <div className="border-t border-atlas-border-default/30 pt-2">
                <div className="font-semibold text-atlas-text-primary">
                  3. Geometric Annualization (CAGR)
                </div>
                <div className="mt-1 font-mono text-[11px] text-atlas-text-secondary bg-atlas-surface-3/50 p-2 rounded-xs">
                  R_ann = (1 + R_cum)^(365.25 / D) - 1 &nbsp;&nbsp;(for D &ge; 365 days)
                </div>
                <p className="mt-1 text-[11px] text-atlas-text-tertiary">
                  Periods under 365 days suppress annualization to prevent false volatility extrapolation.
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Subperiod Breakdown Table */}
          {summary.subperiods.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-semibold text-atlas-text-primary flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-atlas-accent" />
                Subperiod Segmentation Audit ({summary.subperiods.length} subperiods)
              </h4>

              <div className="max-h-48 overflow-y-auto overflow-x-auto rounded-sm border border-atlas-border-default/50">
                <table className="w-full text-left font-mono text-[11px]">
                  <thead className="bg-atlas-surface-2 text-atlas-text-tertiary">
                    <tr>
                      <th className="p-2">#</th>
                      <th className="p-2">Start Time</th>
                      <th className="p-2">End Time</th>
                      <th className="p-2 text-right">Start Val</th>
                      <th className="p-2 text-right">Pre-flow Val</th>
                      <th className="p-2 text-right">Flow</th>
                      <th className="p-2 text-right">Subperiod R</th>
                      <th className="p-2 text-right">Linked TWR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-atlas-border-default/30">
                    {summary.subperiods.map((s) => (
                      <tr key={s.subperiod_index} className="hover:bg-atlas-surface-2/40">
                        <td className="p-2 font-semibold text-atlas-text-primary">{s.subperiod_index}</td>
                        <td className="p-2 text-atlas-text-secondary whitespace-nowrap">
                          {new Date(s.start_time).toLocaleDateString()}
                        </td>
                        <td className="p-2 text-atlas-text-secondary whitespace-nowrap">
                          {new Date(s.end_time).toLocaleDateString()}
                        </td>
                        <td className="p-2 text-right">{formatCurrency(s.start_value, summary.base_currency)}</td>
                        <td className="p-2 text-right">{formatCurrency(s.end_value_pre_flow, summary.base_currency)}</td>
                        <td className="p-2 text-right font-medium">
                          {parseFloat(s.net_external_flow) !== 0 ? formatCurrency(s.net_external_flow, summary.base_currency) : "--"}
                        </td>
                        <td className="p-2 text-right font-semibold text-atlas-accent">
                          {formatRate(s.subperiod_return)}
                        </td>
                        <td className="p-2 text-right font-semibold text-emerald-400">
                          {formatRate(s.cumulative_twr_linked)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-5 flex justify-end border-t border-atlas-border-default/60 pt-3">
          <button
            onClick={onClose}
            className="rounded-sm bg-atlas-surface-2 px-3 py-1.5 text-xs font-medium text-atlas-text-primary hover:bg-atlas-surface-3"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}

