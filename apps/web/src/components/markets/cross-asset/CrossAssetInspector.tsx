"use client";

import React from "react";
import Link from "next/link";
import {
  CrossAssetMember,
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
  Clock,
  ExternalLink,
  Layers,
  ShieldAlert,
  ShieldCheck,
  X,
} from "lucide-react";

interface CrossAssetInspectorProps {
  member: CrossAssetMember | null;
  onClose?: () => void;
}

export function CrossAssetInspector({
  member,
  onClose,
}: CrossAssetInspectorProps) {
  if (!member) {
    return (
      <div className="p-4 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-xs text-[var(--atlas-text-tertiary)] text-center">
        Select an instrument from the table or overview grid to inspect its canonical identity, benchmark classification, and temporal alignment.
      </div>
    );
  }

  const classColors = getAssetClassColor(member.asset_class);
  const isAlignedEligible = member.aligned_performance.eligible;

  // Determine asset-class hub route
  const getAssetClassHub = (ac: string): string => {
    switch (ac) {
      case "equities":
        return "/markets/equities";
      case "etfs":
        return "/markets/funds";
      case "fx":
        return "/markets/fx";
      case "crypto":
        return "/markets/crypto";
      case "bonds":
        return "/markets/bonds";
      case "futures":
        return "/markets/futures";
      default:
        return "/markets";
    }
  };

  return (
    <div className="p-4 rounded bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-3 pb-3 border-b border-[var(--atlas-border-subtle)]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`px-2 py-0.5 rounded text-[10px] uppercase font-mono font-semibold border ${classColors.bg} ${classColors.text} ${classColors.border}`}
            >
              {member.asset_class}
            </span>
            <h3 className="text-base font-bold text-[var(--atlas-text-primary)] font-mono">
              {member.symbol}
            </h3>
            {member.is_proxy && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-amber-950/70 text-amber-300 border border-amber-800/40">
                {member.proxy_kind}
              </span>
            )}
            {member.is_benchmark && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-blue-950/70 text-blue-300 border border-blue-800/40">
                Index Benchmark
              </span>
            )}
          </div>
          <div className="text-xs text-[var(--atlas-text-secondary)]">
            {member.display_name} • {member.market_or_venue}
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-elevated)]"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Benchmark vs Proxy Disclosures */}
      {member.is_proxy && (
        <div className="p-3 rounded bg-amber-950/20 border border-amber-800/30 text-xs text-amber-200/90 space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-amber-300 text-[11px] font-mono">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>PROXY INSTRUMENT DISCLOSURE</span>
          </div>
          <p className="text-[11px] leading-relaxed text-amber-200/80">
            This instrument is an exchange-traded proxy tracking{" "}
            <strong>{member.proxy_benchmark_target || "the target index"}</strong>. It is subject
            to tracking error, management fees, exchange trading hours, and contract rollover basis.
            It is not mathematically identical to the underlying cash index.
          </p>
        </div>
      )}

      {/* Canonical Metadata Grid */}
      <div className="grid grid-cols-2 gap-2 text-xs font-mono">
        <div className="p-2.5 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)]">
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] block uppercase">
            Canonical Instrument UUID
          </span>
          <span className="text-[11px] text-[var(--atlas-text-secondary)] break-all">
            {member.instrument_entity_id}
          </span>
        </div>

        <div className="p-2.5 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)]">
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] block uppercase">
            Market Series Identity
          </span>
          <span className="text-[11px] text-[var(--atlas-text-primary)]">
            {member.market_series_identity}
          </span>
        </div>
      </div>

      {/* Native Observation Card */}
      <div className="p-3 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase text-[var(--atlas-text-secondary)] font-semibold flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Native Asset-Class Observation</span>
          </span>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/50 px-1.5 py-0.5 rounded border border-emerald-800/40">
            {member.freshness_status}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 text-xs font-mono pt-1">
          <div>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Current Obs</span>
            <span className="font-bold text-sm text-[var(--atlas-text-primary)]">
              {member.asset_class === "bonds"
                ? `${formatNumber(member.native_metric.current_value, 3)}%`
                : formatNumber(
                    member.native_metric.current_value,
                    member.asset_class === "fx" ? 4 : 2
                  )}
            </span>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
              {member.native_metric.unit}
            </span>
          </div>

          <div>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Reference</span>
            <span className="text-sm text-[var(--atlas-text-secondary)]">
              {member.native_metric.reference_value
                ? member.asset_class === "bonds"
                  ? `${formatNumber(member.native_metric.reference_value, 3)}%`
                  : formatNumber(
                      member.native_metric.reference_value,
                      member.asset_class === "fx" ? 4 : 2
                    )
                : "—"}
            </span>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Prev Session</span>
          </div>

          <div>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Native Change</span>
            <span
              className={`font-bold text-sm ${
                member.native_metric.change_value && Number(member.native_metric.change_value) > 0
                  ? "text-emerald-400"
                  : member.native_metric.change_value &&
                    Number(member.native_metric.change_value) < 0
                  ? "text-rose-400"
                  : "text-[var(--atlas-text-tertiary)]"
              }`}
            >
              {formatNativeChange(
                member.native_metric.change_value,
                member.native_metric.change_percent,
                member.native_metric.metric_kind,
                member.native_metric.unit
              )}
            </span>
            <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
              {member.native_metric.display_label}
            </span>
          </div>
        </div>

        <div className="pt-2 border-t border-[var(--atlas-border-subtle)] text-[10px] font-mono text-[var(--atlas-text-tertiary)] flex items-center justify-between">
          <span>Obs Time: {formatIsoTime(member.native_metric.as_of_time)}</span>
          <span>Session: {member.native_metric.session_status}</span>
        </div>
      </div>

      {/* Aligned Price Performance Card */}
      <div className="p-3 rounded bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase text-[var(--atlas-text-secondary)] font-semibold flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-emerald-400" />
            <span>Aligned Performance Evaluation</span>
          </span>
          {isAlignedEligible ? (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400 bg-emerald-950/50 px-1.5 py-0.5 rounded border border-emerald-800/40">
              <CheckCircle2 className="w-3 h-3" />
              <span>Qualified</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[10px] font-mono text-amber-400 bg-amber-950/50 px-1.5 py-0.5 rounded border border-amber-800/40">
              <AlertTriangle className="w-3 h-3" />
              <span>Ineligible</span>
            </span>
          )}
        </div>

        {isAlignedEligible ? (
          <div className="space-y-2 font-mono text-xs pt-1">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
                  Aligned Price Return
                </span>
                <span
                  className={`text-base font-bold ${
                    member.aligned_performance.price_return_percent &&
                    Number(member.aligned_performance.price_return_percent) > 0
                      ? "text-emerald-400"
                      : "text-rose-400"
                  }`}
                >
                  {formatPercentChange(member.aligned_performance.price_return_percent)}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">
                  Indexed Level (Base 100)
                </span>
                <span className="text-base font-bold text-[var(--atlas-text-primary)]">
                  {formatIndexedValue(member.aligned_performance.indexed_value)}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-[var(--atlas-border-subtle)] text-[var(--atlas-text-tertiary)]">
              <div>
                <span>Start Price: </span>
                <strong className="text-[var(--atlas-text-secondary)]">
                  {formatNumber(member.aligned_performance.start_price, 2)}
                </strong>
                <span className="block text-[10px]">
                  Offset: {member.aligned_performance.start_time_offset_seconds}s (≤ 7200s tol)
                </span>
              </div>
              <div>
                <span>End Price: </span>
                <strong className="text-[var(--atlas-text-secondary)]">
                  {formatNumber(member.aligned_performance.end_price, 2)}
                </strong>
                <span className="block text-[10px]">
                  Eff Start: {formatIsoTime(member.aligned_performance.effective_start_time)}
                </span>
              </div>
            </div>

            <div className="text-[10px] text-emerald-400/90 pt-1 flex items-center gap-1 font-sans">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Zero look-ahead verified: observation occurred at/before window start.</span>
            </div>
          </div>
        ) : (
          <div className="p-2 rounded bg-amber-950/20 border border-amber-800/30 text-xs text-amber-300 space-y-1">
            <div className="font-semibold text-[11px] font-mono">
              REASON: {member.aligned_performance.exclusion_reason}
            </div>
            <p className="text-[11px] text-amber-200/80 leading-relaxed font-sans">
              {member.aligned_performance.exclusion_detail}
            </p>
          </div>
        )}
      </div>

      {/* Navigation Actions */}
      <div className="flex items-center gap-2 pt-2 border-t border-[var(--atlas-border-subtle)]">
        <Link
          href={`/charts?symbol=${member.symbol}&instrument=${member.instrument_entity_id}`}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-[var(--atlas-surface-elevated)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] hover:border-[var(--atlas-border-focus)] transition-colors text-xs font-medium"
        >
          <span>Open in Charts</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>

        <Link
          href={getAssetClassHub(member.asset_class)}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-[var(--atlas-surface-base)] text-[var(--atlas-text-secondary)] border border-[var(--atlas-border-subtle)] hover:text-[var(--atlas-text-primary)] transition-colors text-xs font-medium"
        >
          <span>Asset Class Hub</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
