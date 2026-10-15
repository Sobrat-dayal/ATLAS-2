"use client";

import React from "react";
import {
  formatFxChange,
  formatFxFreshnessBadge,
  formatFxRate,
  formatFxSpread,
  formatFxSpreadBps,
  formatObservedTimestamp,
  formatRateKind,
  FxPairDirectoryItem,
} from "@/lib/markets/fx";

export interface FxPairDirectoryRowProps {
  item: FxPairDirectoryItem;
  isSelected: boolean;
  onSelect: (instrumentEntityId: string) => void;
}

export function FxPairDirectoryRow({
  item,
  isSelected,
  onSelect,
}: FxPairDirectoryRowProps) {
  const quote = item.quote;
  const precision = item.rate_precision || 4;

  const bidFormatted = formatFxRate(quote?.bid, precision);
  const askFormatted = formatFxRate(quote?.ask, precision);
  const midpointFormatted = formatFxRate(quote?.midpoint, precision);
  const spreadAbsFormatted = formatFxSpread(quote?.spread_absolute, precision);
  const spreadBpsFormatted = formatFxSpreadBps(quote?.spread_bps);
  const changeFormatted = formatFxChange(quote?.change_24h_percent);
  const freshness = formatFxFreshnessBadge(quote?.freshness_status || "UNKNOWN");
  const observedTime = formatObservedTimestamp(quote?.observed_at);
  const rateKindLabel = formatRateKind(quote?.rate_kind || "UNKNOWN");

  return (
    <tr
      onClick={() => onSelect(item.instrument_entity_id)}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(item.instrument_entity_id);
        }
      }}
      className={`border-b border-[var(--atlas-border-subtle)] text-xs cursor-pointer transition-colors focus:outline-none focus:bg-[var(--atlas-surface-hover)] ${
        isSelected
          ? "bg-emerald-500/10 hover:bg-emerald-500/15"
          : "hover:bg-[var(--atlas-surface-hover)]"
      }`}
      aria-selected={isSelected}
    >
      {/* 1. Pair Name / Notation */}
      <td className="py-2.5 px-3 font-semibold text-[var(--atlas-text-primary)] whitespace-nowrap">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-sm tracking-tight">{item.display_pair}</span>
          <span className="px-1.5 py-0.2 rounded text-[10px] font-mono text-[var(--atlas-text-tertiary)] bg-zinc-800/60 border border-zinc-700/50">
            {item.instrument_kind}
          </span>
        </div>
        <div className="text-[10px] text-[var(--atlas-text-tertiary)] font-normal mt-0.5">
          Base: {item.base_currency} · Quote: {item.quote_currency}
        </div>
      </td>

      {/* 2. Rate Kind */}
      <td className="py-2.5 px-3 text-[var(--atlas-text-secondary)] whitespace-nowrap">
        <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)]">
          {rateKindLabel}
        </span>
      </td>

      {/* 3. Bid */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-secondary)] tabular-nums whitespace-nowrap">
        {bidFormatted}
      </td>

      {/* 4. Ask */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-secondary)] tabular-nums whitespace-nowrap">
        {askFormatted}
      </td>

      {/* 5. Midpoint */}
      <td className="py-2.5 px-3 text-right font-mono font-bold text-[var(--atlas-text-primary)] tabular-nums whitespace-nowrap">
        {midpointFormatted}
      </td>

      {/* 6. Spread */}
      <td className="py-2.5 px-3 text-right font-mono tabular-nums whitespace-nowrap">
        <span className="text-[var(--atlas-text-secondary)]">{spreadAbsFormatted}</span>
        {quote?.spread_bps !== null && quote?.spread_bps !== undefined && (
          <span className="block text-[10px] text-[var(--atlas-text-tertiary)]">
            {spreadBpsFormatted}
          </span>
        )}
      </td>

      {/* 7. 24h Change */}
      <td className={`py-2.5 px-3 text-right font-mono tabular-nums whitespace-nowrap ${changeFormatted.colorClass}`}>
        {changeFormatted.text}
      </td>

      {/* 8. Status / Freshness */}
      <td className="py-2.5 px-3 text-center whitespace-nowrap">
        <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${freshness.badgeClass}`}>
          {freshness.label}
        </span>
      </td>

      {/* 9. Provider Source */}
      <td className="py-2.5 px-3 text-center font-mono text-[11px] text-[var(--atlas-text-tertiary)] whitespace-nowrap">
        {quote?.provider || "OPENBB"}
      </td>

      {/* 10. Observed Time */}
      <td className="py-2.5 px-3 text-right font-mono text-[11px] text-[var(--atlas-text-tertiary)] whitespace-nowrap">
        {observedTime}
      </td>
    </tr>
  );
}
