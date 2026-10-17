"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  BarChart3,
  Check,
  Copy,
  ExternalLink,
  X,
} from "lucide-react";
import {
  formatActivityVolume,
  formatPrice,
  formatRank,
  formatSignedAbsoluteChange,
  formatSignedPercent,
  formatTimestamp,
  MoverRankedItem,
} from "@/lib/markets/movers";

export interface MarketMoverInspectorProps {
  item: MoverRankedItem | null;
  onClose: () => void;
}

export function MarketMoverInspector({ item, onClose }: MarketMoverInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (!item) return null;

  const handleCopyUuid = () => {
    if (item.instrument_entity_id) {
      navigator.clipboard.writeText(item.instrument_entity_id);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const pctNum = item.percent_change ? parseFloat(String(item.percent_change)) : 0;
  const isPositive = pctNum > 0;
  const isNegative = pctNum < 0;

  let changeColor = "text-[var(--atlas-text-secondary)]";
  if (isPositive) {
    changeColor = "text-emerald-400 font-semibold";
  } else if (isNegative) {
    changeColor = "text-rose-400 font-semibold";
  }

  // Determine destination asset class directory
  let assetClassHref = "/markets";
  if (item.asset_class === "equity") assetClassHref = "/markets/equities";
  else if (item.asset_class === "crypto") assetClassHref = "/markets/crypto";
  else if (item.asset_class === "futures") assetClassHref = "/markets/futures";
  else if (item.asset_class === "fx") assetClassHref = "/markets/fx";
  else if (item.asset_class === "bond") assetClassHref = "/markets/bonds";

  return (
    <aside
      aria-label="Selected market mover inspector"
      className="w-full lg:w-80 xl:w-96 bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg p-4 flex flex-col gap-4 text-xs h-fit"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 border-b border-[var(--atlas-border-subtle)] pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-300 font-bold border border-zinc-700/60">
              {formatRank(item.rank)}
            </span>
            <span className="font-mono text-base font-bold text-[var(--atlas-text-primary)]">
              {item.symbol}
            </span>
            <span className="px-1.5 py-0.5 rounded text-[10px] font-mono uppercase bg-zinc-900 border border-zinc-800 text-zinc-400">
              {item.exchange_or_venue}
            </span>
          </div>
          <h2 className="text-xs text-[var(--atlas-text-secondary)] mt-1 font-medium">
            {item.display_name}
          </h2>
        </div>

        <button
          type="button"
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-300 p-1 rounded hover:bg-zinc-800/60 transition-colors"
          title="Close Inspector"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Primary Ranking Metric Banner */}
      <div className="p-3 bg-zinc-950/60 rounded border border-zinc-800/80">
        <span className="text-[11px] text-zinc-400 uppercase tracking-wider block font-medium">
          Ranking Metric Value
        </span>
        <div className="flex items-baseline gap-2 mt-1">
          <span className={`text-xl font-mono font-bold ${changeColor}`}>
            {formatSignedPercent(item.percent_change)}
          </span>
          {item.activity_observation && (
            <span className="text-[11px] text-zinc-400 font-mono">
              ({formatActivityVolume(item.activity_observation, item.activity_unit)})
            </span>
          )}
        </div>
      </div>

      {/* Observation Comparison */}
      <div className="flex flex-col gap-2 border-b border-[var(--atlas-border-subtle)] pb-3">
        <span className="text-[11px] font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
          Market Observations
        </span>

        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 rounded bg-zinc-900/40 border border-zinc-800/60">
            <span className="text-[10px] text-zinc-400 block">Current Traded</span>
            <span className="font-mono font-bold text-sm text-[var(--atlas-text-primary)]">
              {formatPrice(item.current_observation, item.ranking_unit === "USDT" ? "USDT" : "USD")}
            </span>
          </div>

          <div className="p-2 rounded bg-zinc-900/40 border border-zinc-800/60">
            <span className="text-[10px] text-zinc-400 block">Prior Reference</span>
            <span className="font-mono font-bold text-sm text-zinc-300">
              {formatPrice(item.reference_observation, item.ranking_unit === "USDT" ? "USDT" : "USD")}
            </span>
          </div>

          <div className="p-2 rounded bg-zinc-900/40 border border-zinc-800/60">
            <span className="text-[10px] text-zinc-400 block">Absolute Change</span>
            <span className={`font-mono font-semibold text-xs ${changeColor}`}>
              {formatSignedAbsoluteChange(item.absolute_change, item.ranking_unit === "USDT" ? "USDT" : "USD")}
            </span>
          </div>

          <div className="p-2 rounded bg-zinc-900/40 border border-zinc-800/60">
            <span className="text-[10px] text-zinc-400 block">Activity Volume</span>
            <span className="font-mono font-semibold text-xs text-[var(--atlas-text-primary)]">
              {formatActivityVolume(item.activity_observation, item.activity_unit)}
            </span>
          </div>
        </div>
      </div>

      {/* Reference Context */}
      <div className="flex flex-col gap-1.5 border-b border-[var(--atlas-border-subtle)] pb-3 text-[11px]">
        <span className="font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
          Reference Context
        </span>

        {item.reference_period_label && (
          <div className="flex items-center justify-between text-zinc-300">
            <span className="text-zinc-500">Period:</span>
            <span className="font-mono">{item.reference_period_label}</span>
          </div>
        )}

        <div className="flex items-center justify-between text-zinc-300">
          <span className="text-zinc-500">As-Of Timestamp:</span>
          <span className="font-mono">{formatTimestamp(item.source_timestamp)}</span>
        </div>

        <div className="flex items-center justify-between text-zinc-300">
          <span className="text-zinc-500">Data Delay:</span>
          <span className="font-mono uppercase text-emerald-400">{item.delay_status}</span>
        </div>

        <div className="flex items-center justify-between text-zinc-300">
          <span className="text-zinc-500">Provider:</span>
          <span className="font-mono uppercase">{item.provider}</span>
        </div>
      </div>

      {/* Canonical Identity */}
      <div className="flex flex-col gap-1.5 border-b border-[var(--atlas-border-subtle)] pb-3 text-[11px]">
        <span className="font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
          Canonical Identity (Stage 17)
        </span>

        <div className="flex items-center justify-between gap-1 p-1.5 rounded bg-zinc-950/80 border border-zinc-800">
          <span className="font-mono text-[10px] text-zinc-400 truncate max-w-[200px]">
            {item.instrument_entity_id}
          </span>
          <button
            type="button"
            onClick={handleCopyUuid}
            className="p-1 text-zinc-400 hover:text-zinc-200 transition-colors"
            title="Copy Instrument UUID"
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </button>
        </div>

        <span className="text-[10px] font-mono text-zinc-500">
          Series: {item.market_series_identity}
        </span>
      </div>

      {/* Navigation Actions */}
      <div className="flex flex-col gap-2 pt-1">
        <Link
          href={`/charts?instrument_id=${item.instrument_entity_id}`}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-zinc-800 hover:bg-zinc-700 text-[var(--atlas-text-primary)] font-medium transition-colors"
        >
          <BarChart3 className="h-3.5 w-3.5 text-emerald-400" />
          <span>Open in Charts</span>
        </Link>

        <Link
          href={assetClassHref}
          className="inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-zinc-900 hover:bg-zinc-800 text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] font-medium border border-zinc-800 transition-colors"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          <span>View in {item.asset_class.toUpperCase()} Directory</span>
        </Link>
      </div>
    </aside>
  );
}
