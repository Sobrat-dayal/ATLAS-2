"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useFxPair } from "@/hooks/markets/useFxPair";
import {
  formatFxChange,
  formatFxFreshnessBadge,
  formatFxRate,
  formatFxSpread,
  formatFxSpreadBps,
  formatFxSpreadPips,
  formatRateKind,
} from "@/lib/markets/fx";
import {
  ArrowUpRight,
  BarChart2,
  Check,
  Compass,
  Copy,
  Globe,
  X,
} from "lucide-react";

export interface FxPairInspectorProps {
  instrumentEntityId: string | null;
  onClose: () => void;
}

export function FxPairInspector({
  instrumentEntityId,
  onClose,
}: FxPairInspectorProps) {
  const { data, isLoading, isError, error } = useFxPair(instrumentEntityId);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!instrumentEntityId) return null;

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const pair = data?.pair;
  const quote = pair?.quote;
  const precision = pair?.rate_precision || 4;
  const baseInfo = data?.base_currency_info;
  const quoteInfo = data?.quote_currency_info;
  const orientation = data?.orientation_explanation;

  const bidFormatted = formatFxRate(quote?.bid, precision);
  const askFormatted = formatFxRate(quote?.ask, precision);
  const midpointFormatted = formatFxRate(quote?.midpoint, precision);
  const spreadAbsFormatted = formatFxSpread(quote?.spread_absolute, precision);
  const spreadBpsFormatted = formatFxSpreadBps(quote?.spread_bps);
  const spreadPipsFormatted = formatFxSpreadPips(quote?.spread_pips);
  const changeFormatted = formatFxChange(quote?.change_24h_percent);
  const freshness = formatFxFreshnessBadge(quote?.freshness_status || "UNKNOWN");
  const rateKindLabel = formatRateKind(quote?.rate_kind || "UNKNOWN");

  return (
    <aside
      aria-label="FX Pair Inspector"
      className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md flex flex-col h-full max-h-[85vh] overflow-hidden shadow-lg animate-in fade-in slide-in-from-right-2 duration-150"
    >
      {/* 1. Header Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/80">
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
            FX Pair Inspector
          </span>
          <span className="px-1.5 py-0.2 rounded text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {pair?.display_pair || "Loading..."}
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close inspector"
          className="p-1 rounded text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] hover:bg-[var(--atlas-surface-hover)] transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* 2. Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
        {isLoading && (
          <div className="py-12 text-center text-[var(--atlas-text-tertiary)] animate-pulse">
            Loading currency pair details...
          </div>
        )}

        {isError && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded text-rose-400 text-xs">
            {error?.message || "Failed to load currency pair overview."}
          </div>
        )}

        {!isLoading && !isError && pair && (
          <>
            {/* Identity & Canonical UUID */}
            <div className="bg-[var(--atlas-surface-card)]/50 border border-[var(--atlas-border-subtle)] rounded p-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] font-semibold text-[var(--atlas-text-primary)]">
                  {pair.display_pair} Spot Exchange Rate
                </span>
                <span className="text-[10px] font-mono text-[var(--atlas-text-tertiary)]">
                  {pair.instrument_kind}
                </span>
              </div>

              <div className="flex items-center justify-between text-[11px] text-[var(--atlas-text-secondary)] font-mono bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] px-2.5 py-1.5 rounded">
                <span className="truncate mr-2" title={pair.instrument_entity_id}>
                  UUID: {pair.instrument_entity_id}
                </span>
                <button
                  type="button"
                  onClick={() => handleCopy(pair.instrument_entity_id, "uuid")}
                  className="text-[var(--atlas-text-tertiary)] hover:text-[var(--atlas-text-primary)] flex-shrink-0"
                  title="Copy Canonical UUID"
                >
                  {copiedId === "uuid" ? (
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </button>
              </div>
            </div>

            {/* Orientation Explanation */}
            {orientation && (
              <div className="bg-emerald-500/5 border border-emerald-500/20 rounded p-3 text-[11px]">
                <div className="flex items-center gap-1.5 font-semibold text-emerald-400 mb-1">
                  <Compass className="h-3.5 w-3.5" />
                  <span>Quotation Orientation</span>
                </div>
                <p className="text-[var(--atlas-text-secondary)] leading-relaxed font-mono">
                  {orientation}
                </p>
              </div>
            )}

            {/* Latest Rate Observation */}
            <div className="border border-[var(--atlas-border-subtle)] rounded p-3 space-y-2.5">
              <div className="flex items-center justify-between border-b border-[var(--atlas-border-subtle)] pb-1.5">
                <span className="font-semibold text-[var(--atlas-text-secondary)]">
                  Spot Rate Observation
                </span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${freshness.badgeClass}`}>
                  {freshness.label}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Rate Kind
                  </span>
                  <span className="font-medium text-[var(--atlas-text-primary)]">
                    {rateKindLabel}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Midpoint
                  </span>
                  <span className="font-mono font-bold text-sm text-[var(--atlas-text-primary)] tabular-nums">
                    {midpointFormatted}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Dealer Bid
                  </span>
                  <span className="font-mono text-[var(--atlas-text-primary)] tabular-nums">
                    {bidFormatted}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Dealer Ask
                  </span>
                  <span className="font-mono text-[var(--atlas-text-primary)] tabular-nums">
                    {askFormatted}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Spread (Absolute)
                  </span>
                  <span className="font-mono text-[var(--atlas-text-primary)] tabular-nums">
                    {spreadAbsFormatted}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Spread (Bps / Pips)
                  </span>
                  <span className="font-mono text-[var(--atlas-text-primary)] tabular-nums">
                    {spreadBpsFormatted} · {spreadPipsFormatted}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    24h Change
                  </span>
                  <span className={`font-mono font-medium tabular-nums ${changeFormatted.colorClass}`}>
                    {changeFormatted.text}
                  </span>
                </div>
                <div>
                  <span className="text-[var(--atlas-text-tertiary)] block text-[10px]">
                    Provider
                  </span>
                  <span className="font-mono text-[var(--atlas-text-primary)]">
                    {quote?.provider || "OPENBB"}
                  </span>
                </div>
              </div>

              <div className="text-[10px] text-[var(--atlas-text-tertiary)] font-mono border-t border-[var(--atlas-border-subtle)] pt-1.5 space-y-0.5">
                <div>Observed at: {quote?.observed_at ? new Date(quote.observed_at).toUTCString() : "—"}</div>
                <div>Received at: {quote?.received_at ? new Date(quote.received_at).toUTCString() : "—"}</div>
              </div>
            </div>

            {/* Currency Entities */}
            <div className="grid grid-cols-2 gap-2.5">
              {/* Base Currency */}
              {baseInfo && (
                <div className="border border-[var(--atlas-border-subtle)] rounded p-2.5 bg-[var(--atlas-surface-card)]/40">
                  <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] mb-1">
                    Base Currency
                  </div>
                  <div className="font-bold text-sm text-[var(--atlas-text-primary)]">
                    {baseInfo.code} ({baseInfo.symbol})
                  </div>
                  <div className="text-[11px] text-[var(--atlas-text-secondary)] mt-0.5">
                    {baseInfo.name}
                  </div>
                  <div className="text-[10px] text-[var(--atlas-text-tertiary)] mt-1 font-mono">
                    Region: {baseInfo.country_or_region} · Minor: {baseInfo.minor_units}
                  </div>
                </div>
              )}

              {/* Quote Currency */}
              {quoteInfo && (
                <div className="border border-[var(--atlas-border-subtle)] rounded p-2.5 bg-[var(--atlas-surface-card)]/40">
                  <div className="text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] mb-1">
                    Quote Currency
                  </div>
                  <div className="font-bold text-sm text-[var(--atlas-text-primary)]">
                    {quoteInfo.code} ({quoteInfo.symbol})
                  </div>
                  <div className="text-[11px] text-[var(--atlas-text-secondary)] mt-0.5">
                    {quoteInfo.name}
                  </div>
                  <div className="text-[10px] text-[var(--atlas-text-tertiary)] mt-1 font-mono">
                    Region: {quoteInfo.country_or_region} · Minor: {quoteInfo.minor_units}
                  </div>
                </div>
              )}
            </div>

            {/* Cross-Module Navigation Links */}
            <div className="flex gap-2 pt-1">
              <Link
                href="/charts"
                className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded text-xs font-medium text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors"
              >
                <BarChart2 className="h-3.5 w-3.5 text-emerald-400" />
                <span>Open in Charts</span>
                <ArrowUpRight className="h-3 w-3 opacity-60" />
              </Link>
              <Link
                href="/economics"
                className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 px-3 rounded text-xs font-medium text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors"
              >
                <Globe className="h-3.5 w-3.5 text-amber-400" />
                <span>Economics</span>
                <ArrowUpRight className="h-3 w-3 opacity-60" />
              </Link>
            </div>

            {/* Disclaimer */}
            <div className="text-[10px] text-[var(--atlas-text-tertiary)] leading-normal border-t border-[var(--atlas-border-subtle)] pt-2.5">
              Spot rates shown are indicative over-the-counter market observations.
              They do not constitute guaranteed bank exchange rates, remittance prices, or tradable broker quotes.
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
