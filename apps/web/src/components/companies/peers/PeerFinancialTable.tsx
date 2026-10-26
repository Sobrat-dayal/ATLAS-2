"use client";

import React from "react";
import {
  PeerComparisonResponseDTO,
  PeerMetricDefinitionDTO,
  ComparableObservationDTO,
  ComparisonMetricCategory,
} from "@/lib/companies/peers";
import { Info, HelpCircle } from "lucide-react";

interface PeerFinancialTableProps {
  comparison: PeerComparisonResponseDTO | null;
  metricCatalog: PeerMetricDefinitionDTO[];
  onSelectObservation: (obs: ComparableObservationDTO) => void;
  isLoading: boolean;
}

export function PeerFinancialTable({
  comparison,
  metricCatalog,
  onSelectObservation,
  isLoading,
}: PeerFinancialTableProps) {
  if (isLoading || !comparison) {
    return (
      <div className="p-8 text-center bg-atlas-surface border border-atlas-border-subtle rounded text-xs text-atlas-text-muted">
        Loading institutional comparable financial observations...
      </div>
    );
  }

  const { companies, observations, statistics } = comparison;

  // Group metrics by category
  const categories: { category: ComparisonMetricCategory; label: string }[] = [
    { category: "SCALE", label: "Business Scale & Capital Structure" },
    { category: "GROWTH", label: "Growth Benchmarking" },
    { category: "PROFITABILITY", label: "Profitability & Capital Efficiency" },
    { category: "LIQUIDITY", label: "Liquidity Benchmarking" },
    { category: "SOLVENCY", label: "Leverage & Solvency" },
    { category: "CASH_FLOW", label: "Cash Generation & FCF" },
  ];

  return (
    <div className="bg-atlas-surface border border-atlas-border-subtle rounded flex flex-col overflow-hidden">
      {/* Table Container with Horizontal Scroll */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            {/* Header row 1: Companies */}
            <tr className="border-b border-atlas-border-subtle bg-atlas-surface-subtle text-[11px] font-semibold">
              <th className="py-2 px-3 sticky left-0 z-20 bg-atlas-surface-subtle border-r border-atlas-border-subtle min-w-[200px] text-atlas-text-primary">
                Financial Metric
              </th>

              {companies.map((comp) => {
                const isSub = comp.is_subject;
                return (
                  <th
                    key={comp.company_id}
                    className={`py-2 px-3 text-right min-w-[110px] ${
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

              {/* Statistical Benchmark Columns */}
              <th className="py-2 px-3 text-right bg-emerald-500/5 text-emerald-400 font-semibold border-l border-atlas-border-subtle min-w-[95px]">
                Peer Median
              </th>
              <th className="py-2 px-3 text-right bg-atlas-surface-subtle text-atlas-text-muted min-w-[90px]">
                Peer Mean
              </th>
              <th className="py-2 px-3 text-right bg-atlas-surface-subtle text-atlas-text-muted min-w-[120px]">
                Range [Min - Max]
              </th>
              <th className="py-2 px-3 text-center bg-atlas-surface-subtle text-atlas-text-muted min-w-[75px]">
                Coverage
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-atlas-border-subtle font-mono text-[11px]">
            {categories.map((cat) => {
              const catMetrics = metricCatalog.filter((m) => m.category === cat.category);
              if (catMetrics.length === 0) return null;

              return (
                <React.Fragment key={cat.category}>
                  {/* Category Header Row */}
                  <tr className="bg-atlas-surface-subtle/70 font-sans font-semibold text-[11px] text-atlas-text-primary">
                    <td
                      colSpan={companies.length + 5}
                      className="py-1.5 px-3 uppercase tracking-wider text-atlas-accent text-[10px]"
                    >
                      {cat.label}
                    </td>
                  </tr>

                  {/* Metric Rows */}
                  {catMetrics.map((metric) => {
                    const rowObs = observations[metric.metric_id] || {};
                    const stat = statistics[metric.metric_id];

                    return (
                      <tr
                        key={metric.metric_id}
                        className="hover:bg-atlas-surface-subtle/50 transition-colors group"
                      >
                        {/* Metric Name */}
                        <td className="py-2 px-3 sticky left-0 z-10 bg-atlas-surface group-hover:bg-atlas-surface-subtle border-r border-atlas-border-subtle font-sans text-atlas-text-primary flex items-center justify-between">
                          <span className="truncate">{metric.name}</span>
                          <span className="text-[10px] text-atlas-text-muted font-mono ml-1 shrink-0">
                            ({metric.unit})
                          </span>
                        </td>

                        {/* Company Observations */}
                        {companies.map((comp) => {
                          const obs = rowObs[comp.company_id];
                          const isSub = comp.is_subject;
                          const isNM = obs?.status === "NOT_MEANINGFUL";

                          return (
                            <td
                              key={comp.company_id}
                              onClick={() => obs && onSelectObservation(obs)}
                              className={`py-2 px-3 text-right cursor-pointer transition-colors ${
                                isSub
                                  ? "bg-atlas-accent/5 font-semibold text-atlas-text-primary border-l border-r border-atlas-accent/20 hover:bg-atlas-accent/15"
                                  : "text-atlas-text-secondary border-r border-atlas-border-subtle/50 hover:bg-atlas-surface-subtle"
                              }`}
                              title={
                                obs
                                  ? `Click to inspect source fact: ${obs.source_filing_ref || "10-K Filing"}`
                                  : "Observation unavailable"
                              }
                            >
                              {obs ? (
                                isNM ? (
                                  <span className="text-atlas-text-muted italic font-sans text-[10px]">
                                    N/M
                                  </span>
                                ) : (
                                  <span>{obs.formatted_value}</span>
                                )
                              ) : (
                                <span className="text-atlas-text-muted">—</span>
                              )}
                            </td>
                          );
                        })}

                        {/* Peer Median */}
                        <td className="py-2 px-3 text-right bg-emerald-500/5 text-emerald-400 font-semibold border-l border-atlas-border-subtle">
                          {stat?.median !== undefined && stat.median !== null
                            ? metric.unit === "%"
                              ? `${stat.median.toFixed(1)}%`
                              : metric.unit === "x"
                              ? `${stat.median.toFixed(1)}x`
                              : metric.unit === "$"
                              ? `$${(stat.median / 1e9).toFixed(1)}B`
                              : stat.median.toFixed(2)
                            : "—"}
                        </td>

                        {/* Peer Mean */}
                        <td className="py-2 px-3 text-right text-atlas-text-muted">
                          {stat?.mean !== undefined && stat.mean !== null
                            ? metric.unit === "%"
                              ? `${stat.mean.toFixed(1)}%`
                              : metric.unit === "x"
                              ? `${stat.mean.toFixed(1)}x`
                              : metric.unit === "$"
                              ? `$${(stat.mean / 1e9).toFixed(1)}B`
                              : stat.mean.toFixed(2)
                            : "—"}
                        </td>

                        {/* Range [Min - Max] */}
                        <td className="py-2 px-3 text-right text-atlas-text-muted text-[10px]">
                          {stat?.min_value !== undefined &&
                          stat?.max_value !== undefined &&
                          stat.min_value !== null &&
                          stat.max_value !== null ? (
                            <span>
                              {metric.unit === "%"
                                ? `${stat.min_value.toFixed(1)}% - ${stat.max_value.toFixed(1)}%`
                                : metric.unit === "x"
                                ? `${stat.min_value.toFixed(1)}x - ${stat.max_value.toFixed(1)}x`
                                : metric.unit === "$"
                                ? `$${(stat.min_value / 1e9).toFixed(0)}B - $${(stat.max_value / 1e9).toFixed(0)}B`
                                : `${stat.min_value.toFixed(1)} - ${stat.max_value.toFixed(1)}`}
                            </span>
                          ) : (
                            "—"
                          )}
                        </td>

                        {/* Coverage */}
                        <td className="py-2 px-3 text-center text-atlas-text-muted text-[10px]">
                          <span
                            className={
                              stat && stat.coverage_ratio >= 0.8
                                ? "text-emerald-400 font-medium"
                                : "text-amber-400 font-medium"
                            }
                          >
                            {stat ? `${stat.sample_count}/${stat.total_count}` : "0/0"}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Provenance note */}
      <div className="p-2 border-t border-atlas-border-subtle bg-atlas-surface-subtle text-[11px] text-atlas-text-muted flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-atlas-accent" />
          Click any table cell to inspect the canonical XBRL source filing facts, accounting framework, and calculation lineage.
        </span>
        <span className="font-mono text-[10px]">Reporting Period: FY2024 / Standardized Common Alignment</span>
      </div>
    </div>
  );
}
