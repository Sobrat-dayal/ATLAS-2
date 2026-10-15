"use client";

import React from "react";
import {
  EquityDirectoryItem,
  formatEquityPrice,
  formatAbsoluteChange,
  formatPercentageChange,
  formatEquitySubtype,
  getFreshnessBadge,
  getDirectionColorClass,
  formatObservationTime,
} from "@/lib/markets/equities";
import { ArrowDown, ArrowUp, Minus } from "lucide-react";

export interface EquityDirectoryRowProps {
  item: EquityDirectoryItem;
  isSelected?: boolean;
  onSelect: (instrumentEntityId: string) => void;
}

export function EquityDirectoryRow({
  item,
  isSelected,
  onSelect,
}: EquityDirectoryRowProps) {
  const freshness = getFreshnessBadge(item.freshness_status);
  const colorClass = getDirectionColorClass(item.change_direction);

  const formattedPrice = formatEquityPrice(item.last_price, item.trading_currency);
  const formattedAbsChange = formatAbsoluteChange(
    item.absolute_change,
    item.trading_currency
  );
  const formattedPctChange = formatPercentageChange(item.percentage_change);

  return (
    <tr
      tabIndex={0}
      role="row"
      aria-selected={isSelected}
      onClick={() => onSelect(item.instrument_entity_id)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(item.instrument_entity_id);
        }
      }}
      className={`group cursor-pointer transition-colors border-b border-[var(--atlas-border-subtle)] hover:bg-[var(--atlas-surface-hover)] focus:outline-none focus:bg-[var(--atlas-surface-hover)] ${
        isSelected
          ? "bg-emerald-500/10 hover:bg-emerald-500/15"
          : "even:bg-[var(--atlas-surface-card)]/30"
      }`}
    >
      {/* 1. Security Name & Subtype */}
      <td className="py-2.5 px-3 text-left">
        <div className="flex flex-col">
          <span className="font-medium text-xs text-[var(--atlas-text-primary)] group-hover:text-emerald-400 transition-colors">
            {item.display_name}
          </span>
          <span className="text-[10px] text-[var(--atlas-text-tertiary)]">
            {formatEquitySubtype(item.equity_subtype)}
          </span>
        </div>
      </td>

      {/* 2. Ticker Symbol */}
      <td className="py-2.5 px-3 text-left">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-mono font-semibold bg-[var(--atlas-surface-card)] text-[var(--atlas-text-primary)] border border-[var(--atlas-border-subtle)]">
          {item.display_symbol}
        </span>
      </td>

      {/* 3. Exchange Venue */}
      <td className="py-2.5 px-3 text-left">
        <div className="flex flex-col">
          <span className="text-xs font-mono font-medium text-[var(--atlas-text-secondary)]">
            {item.exchange_mic}
          </span>
          <span className="text-[10px] text-[var(--atlas-text-tertiary)] truncate max-w-[130px]">
            {item.exchange_display_name}
          </span>
        </div>
      </td>

      {/* 4. Listing Market Country */}
      <td className="py-2.5 px-3 text-left">
        <span className="text-xs text-[var(--atlas-text-secondary)]">
          {item.listing_market_country}
        </span>
      </td>

      {/* 5. Currency */}
      <td className="py-2.5 px-3 text-left">
        <span className="text-xs font-mono text-[var(--atlas-text-tertiary)]">
          {item.trading_currency}
        </span>
      </td>

      {/* 6. Last Price */}
      <td className="py-2.5 px-3 text-right">
        <span className="text-xs font-mono font-semibold text-[var(--atlas-text-primary)]">
          {formattedPrice}
        </span>
      </td>

      {/* 7. Qualified Absolute Change */}
      <td className={`py-2.5 px-3 text-right font-mono text-xs ${colorClass}`}>
        <div className="inline-flex items-center gap-0.5 justify-end">
          {item.change_direction === "up" && (
            <ArrowUp className="h-3 w-3" aria-hidden="true" />
          )}
          {item.change_direction === "down" && (
            <ArrowDown className="h-3 w-3" aria-hidden="true" />
          )}
          {item.change_direction === "flat" && (
            <Minus className="h-3 w-3 opacity-40" aria-hidden="true" />
          )}
          <span>{formattedAbsChange}</span>
        </div>
      </td>

      {/* 8. Percentage Change */}
      <td className={`py-2.5 px-3 text-right font-mono text-xs font-medium ${colorClass}`}>
        <span>{formattedPctChange}</span>
      </td>

      {/* 9. Data Status & Freshness */}
      <td className="py-2.5 px-3 text-center">
        <span
          className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${freshness.className}`}
        >
          {freshness.label}
        </span>
      </td>

      {/* 10. Observation Time */}
      <td className="py-2.5 px-3 text-right text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
        {formatObservationTime(item.source_timestamp || item.received_at)}
      </td>
    </tr>
  );
}
