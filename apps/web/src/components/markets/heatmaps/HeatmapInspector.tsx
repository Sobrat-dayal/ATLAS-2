"use client";

import React from "react";
import Link from "next/link";
import {
  HeatmapLeafNode,
  describeExclusionReason,
  formatMarketCap,
  formatPrice,
  formatSignedPercent,
  formatTimestamp,
} from "@/lib/markets/heatmaps";
import { X, ExternalLink, LineChart, Building, Globe, AlertCircle } from "lucide-react";

interface HeatmapInspectorProps {
  node: HeatmapLeafNode | null;
  onClose: () => void;
  weightLabel?: string | null;
  weightUnit?: string | null;
}

export function HeatmapInspector({
  node,
  onClose,
  weightLabel = "Market Cap",
  weightUnit = "USD",
}: HeatmapInspectorProps) {
  if (!node) return null;

  const isPos = (Number(node.percent_change) || 0) >= 0;

  return (
    <div className="flex flex-col h-full rounded-lg bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] overflow-hidden shadow-xl animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="flex items-center justify-between p-3.5 border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-elevated)]/60">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-base text-[var(--atlas-text-primary)]">
              {node.symbol}
            </span>
            <span className="px-1.5 py-0.2 text-[10px] font-mono rounded bg-zinc-800 text-zinc-300 border border-zinc-700">
              {node.exchange_or_venue}
            </span>
          </div>
          <span className="text-xs text-[var(--atlas-text-secondary)] block truncate max-w-[200px]">
            {node.display_name}
          </span>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-elevated)] transition-colors"
          title="Close Inspector"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Body Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {/* Performance Overview Banner */}
        <div className="p-3 rounded-md bg-[var(--atlas-surface-base)] border border-[var(--atlas-border-subtle)] flex items-center justify-between">
          <div>
            <span className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] block">
              Observed Price
            </span>
            <span className="font-mono text-base font-bold text-[var(--atlas-text-primary)]">
              {formatPrice(node.current_price, node.currency)}
            </span>
          </div>

          <div className="text-right">
            <span className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] block">
              Return
            </span>
            <span
              className={`font-mono text-base font-bold ${
                node.percent_change !== null && node.percent_change !== undefined
                  ? isPos
                    ? "text-emerald-400"
                    : "text-red-400"
                  : "text-zinc-500"
              }`}
            >
              {formatSignedPercent(node.percent_change)}
            </span>
          </div>
        </div>

        {/* Observation Details */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)] block">
            Market Observations
          </span>
          <div className="grid grid-cols-2 gap-2 p-2.5 rounded bg-[var(--atlas-surface-base)]/50 border border-[var(--atlas-border-subtle)]">
            <div>
              <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Reference Price</span>
              <span className="font-mono text-[var(--atlas-text-secondary)] font-medium">
                {formatPrice(node.reference_price, node.currency)}
              </span>
            </div>
            <div>
              <span className="text-[10px] text-[var(--atlas-text-tertiary)] block">Absolute Change</span>
              <span className={`font-mono font-medium ${isPos ? "text-emerald-400" : "text-red-400"}`}>
                {node.absolute_change ? formatPrice(node.absolute_change, node.currency) : "—"}
              </span>
            </div>
            {node.reference_period_label && (
              <div className="col-span-2 pt-1 border-t border-[var(--atlas-border-subtle)]/50 text-[10px] text-[var(--atlas-text-tertiary)]">
                {node.reference_period_label}
              </div>
            )}
          </div>
        </div>

        {/* Capitalization & Weight */}
        {node.weight_value && (
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)] block">
              {weightLabel} & Weighting
            </span>
            <div className="p-2.5 rounded bg-[var(--atlas-surface-base)]/50 border border-[var(--atlas-border-subtle)] space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[var(--atlas-text-secondary)]">Verified Market Cap</span>
                <span className="font-mono font-bold text-[var(--atlas-text-primary)]">
                  {formatMarketCap(node.weight_value, weightUnit || "USD")}
                </span>
              </div>
              {node.normalized_weight && (
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-[var(--atlas-text-tertiary)]">Universe Area Share</span>
                  <span className="font-mono text-emerald-400 font-semibold">
                    {(Number(node.normalized_weight) * 100).toFixed(2)}%
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Classification */}
        {(node.sector || node.industry) && (
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)] block">
              Taxonomy Classification
            </span>
            <div className="p-2.5 rounded bg-[var(--atlas-surface-base)]/50 border border-[var(--atlas-border-subtle)] space-y-1">
              {node.sector && (
                <div className="flex items-center justify-between">
                  <span className="text-[var(--atlas-text-tertiary)]">Sector</span>
                  <span className="font-medium text-[var(--atlas-text-secondary)]">{node.sector}</span>
                </div>
              )}
              {node.industry && (
                <div className="flex items-center justify-between">
                  <span className="text-[var(--atlas-text-tertiary)]">Industry</span>
                  <span className="font-medium text-[var(--atlas-text-secondary)]">{node.industry}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Canonical Identity */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)] block">
            Identity Authority
          </span>
          <div className="p-2.5 rounded bg-[var(--atlas-surface-base)]/50 border border-[var(--atlas-border-subtle)] space-y-1 text-[10px] font-mono">
            <div>
              <span className="text-[var(--atlas-text-tertiary)] block">Instrument UUID (Stage 17)</span>
              <span className="text-[var(--atlas-text-secondary)] break-all select-all">
                {node.instrument_entity_id}
              </span>
            </div>
            <div>
              <span className="text-[var(--atlas-text-tertiary)] block">Series Key</span>
              <span className="text-[var(--atlas-text-secondary)] break-all select-all">
                {node.market_series_identity}
              </span>
            </div>
          </div>
        </div>

        {/* Provenance & Freshness */}
        <div className="space-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)] block">
            Data Quality & Provenance
          </span>
          <div className="p-2.5 rounded bg-[var(--atlas-surface-base)]/50 border border-[var(--atlas-border-subtle)] space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-[var(--atlas-text-tertiary)]">Provider</span>
              <span className="font-medium text-[var(--atlas-text-secondary)] uppercase">
                {node.provider}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[var(--atlas-text-tertiary)]">Freshness / Delay</span>
              <span className="font-medium text-[var(--atlas-text-secondary)]">
                {node.freshness_status} ({node.delay_status})
              </span>
            </div>
            {node.source_timestamp && (
              <div className="flex items-center justify-between text-[10px]">
                <span className="text-[var(--atlas-text-tertiary)]">Quote Time</span>
                <span className="font-mono text-[var(--atlas-text-tertiary)]">
                  {formatTimestamp(node.source_timestamp)}
                </span>
              </div>
            )}
            {!node.is_qualified && node.exclusion_reason && (
              <div className="pt-1.5 border-t border-[var(--atlas-border-subtle)] flex items-start gap-1.5 text-amber-400">
                <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                <span>{describeExclusionReason(node.exclusion_reason)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Quick Cross-Module Actions */}
        <div className="pt-2 border-t border-[var(--atlas-border-subtle)] flex flex-col gap-2">
          <Link
            href={`/charts?symbol=${node.symbol}`}
            className="flex items-center justify-between px-3 py-2 rounded bg-[var(--atlas-surface-elevated)] hover:bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] transition-colors"
          >
            <div className="flex items-center gap-2">
              <LineChart className="w-4 h-4 text-emerald-500" />
              <span>Open in Charts</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-[var(--atlas-text-tertiary)]" />
          </Link>

          <Link
            href={`/markets/${node.asset_class === "equity" ? "equities" : node.asset_class}`}
            className="flex items-center justify-between px-3 py-2 rounded bg-[var(--atlas-surface-elevated)] hover:bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] transition-colors"
          >
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-blue-400" />
              <span>Open Markets Directory</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-[var(--atlas-text-tertiary)]" />
          </Link>

          <Link
            href="/companies"
            className="flex items-center justify-between px-3 py-2 rounded bg-[var(--atlas-surface-elevated)] hover:bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)] transition-colors"
          >
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-amber-400" />
              <span>Open Company Intelligence</span>
            </div>
            <ExternalLink className="w-3.5 h-3.5 text-[var(--atlas-text-tertiary)]" />
          </Link>
        </div>
      </div>
    </div>
  );
}
