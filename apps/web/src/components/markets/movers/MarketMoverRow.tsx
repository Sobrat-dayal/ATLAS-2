"use client";

import React from "react";
import {
  formatActivityVolume,
  formatPrice,
  formatRank,
  formatSignedAbsoluteChange,
  formatSignedPercent,
  MoverCategory,
  MoverRankedItem,
} from "@/lib/markets/movers";

export interface MarketMoverRowProps {
  item: MoverRankedItem;
  category?: MoverCategory;
  isSelected: boolean;
  onSelect: (item: MoverRankedItem) => void;
}

export function MarketMoverRow({
  item,
  isSelected,
  onSelect,
}: MarketMoverRowProps) {
  const pctNum = item.percent_change ? parseFloat(String(item.percent_change)) : 0;
  const isPositive = pctNum > 0;
  const isNegative = pctNum < 0;

  let changeColor = "text-[var(--atlas-text-secondary)]";
  if (isPositive) {
    changeColor = "text-emerald-400 font-semibold";
  } else if (isNegative) {
    changeColor = "text-rose-400 font-semibold";
  }

  return (
    <tr
      tabIndex={0}
      aria-selected={isSelected}
      onClick={() => onSelect(item)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(item);
        }
      }}
      className={`border-b border-[var(--atlas-border-subtle)] cursor-pointer transition-colors text-xs select-none focus:outline-none focus:bg-zinc-800/60 ${
        isSelected
          ? "bg-emerald-950/20 border-l-2 border-l-emerald-500"
          : "hover:bg-zinc-900/60"
      }`}
    >
      {/* Rank */}
      <td className="py-2.5 px-3 font-mono text-zinc-400 font-semibold w-12 text-center">
        {formatRank(item.rank)}
      </td>

      {/* Symbol & Name */}
      <td className="py-2.5 px-3">
        <div className="flex flex-col">
          <span className="font-mono font-bold text-[var(--atlas-text-primary)]">
            {item.symbol}
          </span>
          <span className="text-[11px] text-[var(--atlas-text-tertiary)] truncate max-w-[180px]">
            {item.display_name}
          </span>
        </div>
      </td>

      {/* Venue */}
      <td className="py-2.5 px-3 font-mono text-zinc-400">
        <span className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-900 border border-zinc-800">
          {item.exchange_or_venue}
        </span>
      </td>

      {/* Current Traded Price */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-primary)]">
        {formatPrice(item.current_observation, item.ranking_unit === "USDT" ? "USDT" : "USD")}
      </td>

      {/* Prior Reference Observation */}
      <td className="py-2.5 px-3 text-right font-mono text-zinc-400">
        {formatPrice(item.reference_observation, item.ranking_unit === "USDT" ? "USDT" : "USD")}
      </td>

      {/* Absolute Change */}
      <td className={`py-2.5 px-3 text-right font-mono ${changeColor}`}>
        {formatSignedAbsoluteChange(item.absolute_change, item.ranking_unit === "USDT" ? "USDT" : "USD")}
      </td>

      {/* Percentage Change */}
      <td className={`py-2.5 px-3 text-right font-mono ${changeColor}`}>
        {formatSignedPercent(item.percent_change)}
      </td>

      {/* Activity Volume */}
      <td className="py-2.5 px-3 text-right font-mono text-[var(--atlas-text-primary)]">
        {formatActivityVolume(item.activity_observation, item.activity_unit)}
      </td>

      {/* Freshness / Status */}
      <td className="py-2.5 px-3 text-center">
        <span
          className={`px-1.5 py-0.5 rounded text-[10px] font-mono uppercase ${
            item.delay_status === "realtime"
              ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/40"
              : "bg-amber-950/60 text-amber-400 border border-amber-800/40"
          }`}
        >
          {item.delay_status}
        </span>
      </td>
    </tr>
  );
}
