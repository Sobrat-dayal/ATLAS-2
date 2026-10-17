"use client";

import React from "react";
import {
  AssetClassSummarySection,
  CrossAssetMember,
  formatNativeChange,
  formatNumber,
  getAssetClassColor,
} from "@/lib/markets/cross-asset";
import { Layers } from "lucide-react";

interface AssetClassOverviewGridProps {
  sections: AssetClassSummarySection[];
  selectedMember: CrossAssetMember | null;
  onSelectMember: (member: CrossAssetMember) => void;
}

export function AssetClassOverviewGrid({
  sections,
  selectedMember,
  onSelectMember,
}: AssetClassOverviewGridProps) {
  if (sections.length === 0) return null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-tight text-[var(--atlas-text-primary)] flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>Multi-Asset Market Overview (Native Conventions)</span>
        </h2>
        <span className="text-[11px] text-[var(--atlas-text-tertiary)]">
          Click an instrument to inspect canonical series & alignment details
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        {sections.map((sec) => {
          const classColors = getAssetClassColor(sec.asset_class);

          return (
            <div
              key={sec.asset_class}
              className="p-3.5 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] hover:border-[var(--atlas-border-base)] transition-colors flex flex-col justify-between gap-3"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase border ${classColors.bg} ${classColors.text} ${classColors.border}`}
                    >
                      {sec.asset_class}
                    </span>
                    <h3 className="text-xs font-bold text-[var(--atlas-text-primary)]">
                      {sec.display_title}
                    </h3>
                  </div>
                  <span className="text-[10px] font-mono text-[var(--atlas-text-tertiary)]">
                    {sec.total_members} series
                  </span>
                </div>

                <p className="text-[11px] text-[var(--atlas-text-tertiary)] mb-3 leading-relaxed">
                  {sec.native_metric_description}
                </p>

                <div className="space-y-2">
                  {sec.representative_members.map((m) => {
                    const isSelected = selectedMember?.symbol === m.symbol;
                    const nativeChangeStr = formatNativeChange(
                      m.native_metric.change_value,
                      m.native_metric.change_percent,
                      m.native_metric.metric_kind,
                      m.native_metric.unit
                    );
                    const isPositive =
                      m.native_metric.change_value &&
                      Number(m.native_metric.change_value) > 0;
                    const isNegative =
                      m.native_metric.change_value &&
                      Number(m.native_metric.change_value) < 0;

                    return (
                      <button
                        key={m.symbol}
                        type="button"
                        onClick={() => onSelectMember(m)}
                        className={`w-full text-left p-2 rounded transition-all flex items-center justify-between gap-2 border ${
                          isSelected
                            ? "bg-[var(--atlas-surface-elevated)] border-[var(--atlas-border-focus)] shadow-sm"
                            : "bg-[var(--atlas-surface-base)] border-[var(--atlas-border-subtle)] hover:bg-[var(--atlas-surface-elevated)]"
                        }`}
                      >
                        <div className="flex flex-col min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-xs font-bold text-[var(--atlas-text-primary)]">
                              {m.symbol}
                            </span>
                            {m.is_proxy && (
                              <span
                                className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-amber-950/70 text-amber-300 border border-amber-800/40"
                                title={`Proxy for ${m.proxy_benchmark_target || "Benchmark Index"}`}
                              >
                                {m.proxy_kind}
                              </span>
                            )}
                            {m.is_benchmark && (
                              <span
                                className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-blue-950/70 text-blue-300 border border-blue-800/40"
                                title="Canonical Benchmark Series"
                              >
                                Benchmark
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] text-[var(--atlas-text-tertiary)] truncate">
                            {m.display_name} • {m.market_or_venue}
                          </span>
                        </div>

                        <div className="flex flex-col items-end text-right shrink-0">
                          <span className="font-mono text-xs font-semibold text-[var(--atlas-text-primary)]">
                            {m.asset_class === "bonds"
                              ? `${formatNumber(m.native_metric.current_value, 3)}%`
                              : formatNumber(
                                  m.native_metric.current_value,
                                  m.asset_class === "fx" ? 4 : 2
                                )}
                          </span>
                          <span
                            className={`font-mono text-[11px] font-medium ${
                              isPositive
                                ? "text-emerald-400"
                                : isNegative
                                ? "text-rose-400"
                                : "text-[var(--atlas-text-tertiary)]"
                            }`}
                          >
                            {nativeChangeStr}
                          </span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="pt-2 border-t border-[var(--atlas-border-subtle)] flex items-center justify-between text-[10px] text-[var(--atlas-text-tertiary)] font-mono">
                <span>Venue scope verified</span>
                <span className="text-emerald-400">Canonical Feed</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
