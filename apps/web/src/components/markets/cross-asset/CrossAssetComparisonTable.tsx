"use client";

import React from "react";
import Link from "next/link";
import {
  CrossAssetMember,
  CrossAssetMode,
  formatIndexedValue,
  formatIsoTime,
  formatNativeChange,
  formatNumber,
  formatPercentChange,
  getAssetClassColor,
} from "@/lib/markets/cross-asset";
import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Table as TableIcon,
} from "lucide-react";

interface CrossAssetComparisonTableProps {
  members: CrossAssetMember[];
  mode: CrossAssetMode;
  selectedMember: CrossAssetMember | null;
  onSelectMember: (member: CrossAssetMember) => void;
}

export function CrossAssetComparisonTable({
  members,
  mode,
  selectedMember,
  onSelectMember,
}: CrossAssetComparisonTableProps) {
  const isAligned = mode === "aligned_performance";

  if (members.length === 0) {
    return (
      <div className="p-8 text-center rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-xs text-[var(--atlas-text-tertiary)]">
        No instruments available in this universe selection.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <TableIcon className="w-4 h-4 text-emerald-400" />
          <h2 className="text-sm font-semibold tracking-tight text-[var(--atlas-text-primary)]">
            {isAligned
              ? "Aligned Price Performance Comparison (Common UTC Window)"
              : "Cross-Asset Market Comparison Table (Native Conventions)"}
          </h2>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-400 border border-zinc-700/50">
            {members.length} items
          </span>
        </div>

        <div className="text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
          {isAligned
            ? "Returns: ((End - Start) / Start) × 100 • Zero look-ahead • Tolerance ≤ 7200s"
            : "Native quotation units preserved • Bond yields displayed in bps"}
        </div>
      </div>

      <div className="overflow-x-auto rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-elevated)] text-[11px] font-mono text-[var(--atlas-text-secondary)] uppercase tracking-wider">
              <th className="py-2.5 px-3">Asset Class</th>
              <th className="py-2.5 px-3">Instrument</th>
              <th className="py-2.5 px-3">Market / Venue</th>
              {isAligned ? (
                <>
                  <th className="py-2.5 px-3 text-right">Aligned Return %</th>
                  <th className="py-2.5 px-3 text-right">Indexed (100)</th>
                  <th className="py-2.5 px-3 text-right">Start Price</th>
                  <th className="py-2.5 px-3 text-right">End Price</th>
                  <th className="py-2.5 px-3">Currency / Unit</th>
                  <th className="py-2.5 px-3">Eligibility</th>
                </>
              ) : (
                <>
                  <th className="py-2.5 px-3">Metric Kind</th>
                  <th className="py-2.5 px-3 text-right">Current Obs</th>
                  <th className="py-2.5 px-3 text-right">Reference Obs</th>
                  <th className="py-2.5 px-3 text-right">Native Change</th>
                  <th className="py-2.5 px-3">Quotation Unit</th>
                  <th className="py-2.5 px-3">As Of (UTC)</th>
                  <th className="py-2.5 px-3">Freshness</th>
                </>
              )}
              <th className="py-2.5 px-3 text-center">Chart</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--atlas-border-subtle)] font-mono">
            {members.map((m) => {
              const isSelected = selectedMember?.symbol === m.symbol;
              const classColor = getAssetClassColor(m.asset_class);

              const nativeChangeStr = formatNativeChange(
                m.native_metric.change_value,
                m.native_metric.change_percent,
                m.native_metric.metric_kind,
                m.native_metric.unit
              );
              const isNativePositive =
                m.native_metric.change_value && Number(m.native_metric.change_value) > 0;
              const isNativeNegative =
                m.native_metric.change_value && Number(m.native_metric.change_value) < 0;

              const isAlignedEligible = m.aligned_performance.eligible;
              const alignedReturnNum = m.aligned_performance.price_return_percent
                ? Number(m.aligned_performance.price_return_percent)
                : null;
              const isAlignedPositive = alignedReturnNum !== null && alignedReturnNum > 0;
              const isAlignedNegative = alignedReturnNum !== null && alignedReturnNum < 0;

              return (
                <tr
                  key={m.symbol}
                  onClick={() => onSelectMember(m)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-[var(--atlas-surface-elevated)] border-l-2 border-l-[var(--atlas-accent-primary)]"
                      : "hover:bg-[var(--atlas-surface-base)]"
                  }`}
                >
                  {/* Asset Class */}
                  <td className="py-2 px-3 whitespace-nowrap">
                    <span
                      className={`inline-block px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold border ${classColor.bg} ${classColor.text} ${classColor.border}`}
                    >
                      {m.asset_class}
                    </span>
                  </td>

                  {/* Instrument / Symbol */}
                  <td className="py-2 px-3 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                      <span className="font-bold text-[var(--atlas-text-primary)]">
                        {m.symbol}
                      </span>
                      {m.is_proxy && (
                        <span
                          className="px-1 py-0.2 rounded text-[9px] bg-amber-950/70 text-amber-300 border border-amber-800/40"
                          title={`Proxy for ${m.proxy_benchmark_target || "Benchmark Index"}`}
                        >
                          {m.proxy_kind}
                        </span>
                      )}
                      {m.is_benchmark && (
                        <span
                          className="px-1 py-0.2 rounded text-[9px] bg-blue-950/70 text-blue-300 border border-blue-800/40"
                          title="Canonical Benchmark Index"
                        >
                          Index
                        </span>
                      )}
                    </div>
                    <div className="text-[10px] text-[var(--atlas-text-tertiary)] font-sans truncate max-w-[140px]">
                      {m.display_name}
                    </div>
                  </td>

                  {/* Market / Venue */}
                  <td className="py-2 px-3 whitespace-nowrap text-[11px] text-[var(--atlas-text-secondary)]">
                    {m.market_or_venue}
                  </td>

                  {isAligned ? (
                    <>
                      {/* Aligned Return % */}
                      <td className="py-2 px-3 text-right whitespace-nowrap">
                        {isAlignedEligible ? (
                          <span
                            className={`font-bold ${
                              isAlignedPositive
                                ? "text-emerald-400"
                                : isAlignedNegative
                                ? "text-rose-400"
                                : "text-[var(--atlas-text-tertiary)]"
                            }`}
                          >
                            {formatPercentChange(m.aligned_performance.price_return_percent)}
                          </span>
                        ) : (
                          <span className="text-[11px] text-amber-400 font-normal">
                            Not Comparable
                          </span>
                        )}
                      </td>

                      {/* Indexed Level (Base 100) */}
                      <td className="py-2 px-3 text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
                        {isAlignedEligible
                          ? formatIndexedValue(m.aligned_performance.indexed_value)
                          : "—"}
                      </td>

                      {/* Start Price */}
                      <td className="py-2 px-3 text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
                        {isAlignedEligible
                          ? formatNumber(
                              m.aligned_performance.start_price,
                              m.asset_class === "fx" ? 4 : 2
                            )
                          : "—"}
                      </td>

                      {/* End Price */}
                      <td className="py-2 px-3 text-right whitespace-nowrap text-[var(--atlas-text-primary)]">
                        {isAlignedEligible
                          ? formatNumber(
                              m.aligned_performance.end_price,
                              m.asset_class === "fx" ? 4 : 2
                            )
                          : "—"}
                      </td>

                      {/* Currency / Unit */}
                      <td className="py-2 px-3 whitespace-nowrap text-[11px] text-[var(--atlas-text-tertiary)]">
                        {m.aligned_performance.quote_currency} ({m.aligned_performance.quote_unit})
                      </td>

                      {/* Eligibility Status */}
                      <td className="py-2 px-3 whitespace-nowrap">
                        {isAlignedEligible ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Qualified</span>
                          </span>
                        ) : (
                          <span
                            className="inline-flex items-center gap-1 text-[10px] text-amber-400"
                            title={m.aligned_performance.exclusion_detail || "Excluded"}
                          >
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>{m.aligned_performance.exclusion_reason}</span>
                          </span>
                        )}
                      </td>
                    </>
                  ) : (
                    <>
                      {/* Metric Kind */}
                      <td className="py-2 px-3 whitespace-nowrap text-[11px] text-[var(--atlas-text-secondary)]">
                        {m.native_metric.display_label}
                      </td>

                      {/* Current Observation */}
                      <td className="py-2 px-3 text-right whitespace-nowrap font-bold text-[var(--atlas-text-primary)]">
                        {m.asset_class === "bonds"
                          ? `${formatNumber(m.native_metric.current_value, 3)}%`
                          : formatNumber(
                              m.native_metric.current_value,
                              m.asset_class === "fx" ? 4 : 2
                            )}
                      </td>

                      {/* Reference Observation */}
                      <td className="py-2 px-3 text-right whitespace-nowrap text-[var(--atlas-text-secondary)]">
                        {m.native_metric.reference_value
                          ? m.asset_class === "bonds"
                            ? `${formatNumber(m.native_metric.reference_value, 3)}%`
                            : formatNumber(
                                m.native_metric.reference_value,
                                m.asset_class === "fx" ? 4 : 2
                              )
                          : "—"}
                      </td>

                      {/* Native Change */}
                      <td className="py-2 px-3 text-right whitespace-nowrap font-semibold">
                        <span
                          className={
                            isNativePositive
                              ? "text-emerald-400"
                              : isNativeNegative
                              ? "text-rose-400"
                              : "text-[var(--atlas-text-tertiary)]"
                          }
                        >
                          {nativeChangeStr}
                        </span>
                      </td>

                      {/* Quotation Unit */}
                      <td className="py-2 px-3 whitespace-nowrap text-[11px] text-[var(--atlas-text-tertiary)]">
                        {m.native_metric.unit}
                      </td>

                      {/* As Of (UTC) */}
                      <td className="py-2 px-3 whitespace-nowrap text-[11px] text-[var(--atlas-text-secondary)]">
                        {formatIsoTime(m.native_metric.as_of_time)}
                      </td>

                      {/* Freshness */}
                      <td className="py-2 px-3 whitespace-nowrap">
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
                          {m.freshness_status}
                        </span>
                      </td>
                    </>
                  )}

                  {/* Chart Link */}
                  <td className="py-2 px-3 text-center whitespace-nowrap">
                    <Link
                      href={`/charts?symbol=${m.symbol}&instrument=${m.instrument_entity_id}`}
                      className="inline-flex items-center justify-center p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-emerald-400 hover:bg-[var(--atlas-surface-card)] transition-colors"
                      title={`Open ${m.symbol} in Charts`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
