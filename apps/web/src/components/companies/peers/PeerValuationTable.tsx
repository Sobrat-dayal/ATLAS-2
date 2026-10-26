"use client";

import React from "react";
import {
  PeerComparisonResponseDTO,
  PeerMetricDefinitionDTO,
  ComparableObservationDTO,
} from "@/lib/companies/peers";
import { DollarSign, ShieldAlert, TrendingDown, TrendingUp, Info } from "lucide-react";

interface PeerValuationTableProps {
  comparison: PeerComparisonResponseDTO | null;
  metricCatalog: PeerMetricDefinitionDTO[];
  onSelectObservation: (obs: ComparableObservationDTO) => void;
  isLoading: boolean;
}

export function PeerValuationTable({
  comparison,
  metricCatalog,
  onSelectObservation,
  isLoading,
}: PeerValuationTableProps) {
  if (isLoading || !comparison) {
    return (
      <div className="p-8 text-center bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-muted">
        Loading relative valuation multiples and statistical benchmarks...
      </div>
    );
  }

  const { companies, observations, statistics } = comparison;
  const valuationMetrics = metricCatalog.filter((m) => m.category === "VALUATION");

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col overflow-hidden">
      {/* Valuation Methodology Notice Banner */}
      <div className="p-3 bg-atlas-surface-subtle border-b border-atlas-border-subtle flex items-start gap-2 text-xs text-atlas-text-muted">
        <DollarSign className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-atlas-text-primary">Institutional Relative Valuation:</span>{" "}
          Market Capitalization is computed on consolidated issuer equity as of the latest official close. Enterprise Value accounts for debt obligations, minority interests, and cash equivalents. Non-meaningful (N/M) metrics are excluded from statistical medians without silent deletion.
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-subtle bg-atlas-surface-subtle text-[11px] font-semibold">
              <th className="py-2.5 px-3 sticky left-0 z-20 bg-atlas-surface-subtle border-r border-atlas-border-subtle min-w-[200px] text-atlas-text-primary">
                Valuation Multiple
              </th>

              {companies.map((comp) => {
                const isSub = comp.is_subject;
                return (
                  <th
                    key={comp.company_id}
                    className={`py-2.5 px-3 text-right min-w-[110px] ${
                      isSub
                        ? "bg-atlas-accent/10 border-l border-r border-atlas-accent/30 text-atlas-accent font-bold"
                        : "text-atlas-text-secondary border-r border-atlas-border-subtle/50"
                    }`}
                  >
                    <div className="truncate text-xs">{comp.display_name}</div>
                    <div className="text-[10px] font-mono mt-0.5 opacity-80">
                      {comp.ticker} {isSub ? "(Subject)" : ""}
                    </div>
                  </th>
                );
              })}

              <th className="py-2.5 px-3 text-right bg-emerald-500/5 text-emerald-400 font-semibold border-l border-atlas-border-subtle min-w-[95px]">
                Peer Median
              </th>
              <th className="py-2.5 px-3 text-right bg-atlas-surface-subtle text-atlas-text-muted min-w-[95px]">
                Subject Spread
              </th>
              <th className="py-2.5 px-3 text-right bg-atlas-surface-subtle text-atlas-text-muted min-w-[95px]">
                Percentile Rank
              </th>
              <th className="py-2.5 px-3 text-center bg-atlas-surface-subtle text-atlas-text-muted min-w-[75px]">
                Eligible
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-atlas-border-subtle font-mono text-[11px]">
            {valuationMetrics.map((metric) => {
              const rowObs = observations[metric.metric_id] || {};
              const stat = statistics[metric.metric_id];

              return (
                <tr
                  key={metric.metric_id}
                  className="hover:bg-atlas-surface-subtle/50 transition-colors group"
                >
                  {/* Multiple Name & Formula */}
                  <td className="py-2.5 px-3 sticky left-0 z-10 bg-atlas-surface group-hover:bg-atlas-surface-subtle border-r border-atlas-border-subtle font-sans text-atlas-text-primary">
                    <div className="font-medium text-xs text-atlas-text-primary">{metric.name}</div>
                    <div className="text-[10px] text-atlas-text-muted font-mono truncate max-w-[190px]">
                      {metric.formula_display}
                    </div>
                  </td>

                  {/* Company Observation Multiples */}
                  {companies.map((comp) => {
                    const obs = rowObs[comp.company_id];
                    const isSub = comp.is_subject;
                    const isNM = obs?.status === "NOT_MEANINGFUL";

                    return (
                      <td
                        key={comp.company_id}
                        onClick={() => obs && onSelectObservation(obs)}
                        className={`py-2.5 px-3 text-right cursor-pointer transition-colors ${
                          isSub
                            ? "bg-atlas-accent/5 font-semibold text-atlas-text-primary border-l border-r border-atlas-accent/20 hover:bg-atlas-accent/15"
                            : "text-atlas-text-secondary border-r border-atlas-border-subtle/50 hover:bg-atlas-surface-subtle"
                        }`}
                        title={obs ? `Status: ${obs.status}` : "Observation unavailable"}
                      >
                        {obs ? (
                          isNM ? (
                            <span className="text-atlas-text-muted italic font-sans text-[10px]">
                              N/M
                            </span>
                          ) : (
                            <span className="text-xs">{obs.formatted_value}</span>
                          )
                        ) : (
                          <span className="text-atlas-text-muted">—</span>
                        )}
                      </td>
                    );
                  })}

                  {/* Peer Median */}
                  <td className="py-2.5 px-3 text-right bg-emerald-500/5 text-emerald-400 font-semibold border-l border-atlas-border-subtle text-xs">
                    {stat?.median !== undefined && stat.median !== null
                      ? `${stat.median.toFixed(1)}${metric.unit}`
                      : "—"}
                  </td>

                  {/* Subject Spread vs Median */}
                  <td className="py-2.5 px-3 text-right">
                    {stat?.subject_diff_vs_median_pct !== undefined &&
                    stat.subject_diff_vs_median_pct !== null ? (
                      <span
                        className={`inline-flex items-center gap-0.5 font-medium ${
                          stat.subject_diff_vs_median_pct > 0
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {stat.subject_diff_vs_median_pct > 0 ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : (
                          <TrendingDown className="w-3 h-3" />
                        )}
                        {stat.subject_diff_vs_median_pct >= 0 ? "+" : ""}
                        {stat.subject_diff_vs_median_pct.toFixed(1)}%
                      </span>
                    ) : (
                      <span className="text-atlas-text-muted">—</span>
                    )}
                  </td>

                  {/* Percentile Rank */}
                  <td className="py-2.5 px-3 text-right font-medium">
                    {stat?.subject_percentile !== undefined &&
                    stat.subject_percentile !== null ? (
                      <span className="text-atlas-text-secondary">
                        {stat.subject_percentile.toFixed(0)}th
                      </span>
                    ) : (
                      <span className="text-atlas-text-muted">—</span>
                    )}
                  </td>

                  {/* Sample count */}
                  <td className="py-2.5 px-3 text-center text-atlas-text-muted text-[10px]">
                    <span className="text-emerald-400 font-medium">
                      {stat ? `${stat.sample_count}/${stat.total_count}` : "0/0"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="p-2 border-t border-atlas-border-subtle bg-atlas-surface-subtle text-[11px] text-atlas-text-muted flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-atlas-accent" />
          Multiples are computed using clean trailing twelve months financials and current share class quotes.
        </span>
        <span className="font-mono text-[10px]">Valuation Date: 2024-09-28 (Market Close)</span>
      </div>
    </div>
  );
}
