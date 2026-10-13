"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { ArrowDownRight, ArrowUpRight, ExternalLink } from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import {
  HomeMarketSummaryItem,
} from "@/lib/home/market-summary-types";
import {
  formatAbsoluteChange,
  formatMarketPrice,
  formatPercentageChange,
  getChangeDirectionStyles,
  getDelayBadge,
  getFreshnessBadge,
} from "@/lib/home/market-summary-format";

interface MarketSummaryInstrumentCardProps {
  item: HomeMarketSummaryItem;
}

export function MarketSummaryInstrumentCard({ item }: MarketSummaryInstrumentCardProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();

  const handleOpenInstrument = (e: React.MouseEvent | React.KeyboardEvent) => {
    // Only proceed on click or Enter/Space keys
    if ("key" in e && e.key !== "Enter" && e.key !== " ") {
      return;
    }
    e.preventDefault();

    // 1. Set global selected Entity context
    selectEntity(item.instrument_entity_id);

    // 2. Navigate internally to canonical Markets workspace
    router.push("/markets");
  };

  const { formattedValue, unitLabel } = formatMarketPrice(item);
  const formattedAbsChange = formatAbsoluteChange(item);
  const formattedPctChange = formatPercentageChange(item);
  const dirStyles = getChangeDirectionStyles(item.change_direction);
  const freshness = getFreshnessBadge(item.freshness_status);
  const delay = getDelayBadge(item.delivery_delay_status, item.delay_seconds);

  const isAvailable = item.data_status === "available" && Boolean(item.last_price || item.bid_price || item.ask_price);

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleOpenInstrument}
      onKeyDown={handleOpenInstrument}
      aria-label={`Open ${item.display_name} in Markets`}
      className="group relative flex flex-col justify-between p-3.5 rounded-lg border border-zinc-800/80 bg-zinc-900/50 hover:bg-zinc-800/60 hover:border-zinc-700/80 transition-all cursor-pointer text-left focus:outline-none focus:ring-1 focus:ring-emerald-500/50 shadow-xs"
    >
      {/* 1. Header: Display Symbol, Name, Category */}
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="font-semibold text-zinc-100 text-sm tracking-tight truncate">
              {item.display_name}
            </span>
            {item.display_symbol && (
              <span className="font-mono text-xs text-zinc-400 bg-zinc-800/80 px-1.5 py-0.5 rounded">
                {item.display_symbol}
              </span>
            )}
          </div>
          <span className="text-[11px] font-medium tracking-wide uppercase text-zinc-400 block mt-0.5">
            {item.instrument_category.replace("_", " ")}
          </span>
        </div>

        <ExternalLink
          className="h-3.5 w-3.5 text-zinc-400 group-hover:text-zinc-300 transition-colors shrink-0 mt-0.5"
          aria-hidden="true"
        />
      </div>

      {/* 2. Price & Units */}
      <div className="my-3">
        <div className="flex items-baseline gap-1.5">
          <span
            className={`font-mono tabular-nums text-lg font-semibold tracking-tight ${
              isAvailable ? "text-zinc-100" : "text-zinc-400 italic text-base"
            }`}
          >
            {formattedValue}
          </span>
          {isAvailable && unitLabel && (
            <span className="text-xs text-zinc-400 font-mono">
              {unitLabel}
            </span>
          )}
        </div>

        {/* Change Indicators */}
        <div className="mt-1 flex items-center gap-2 flex-wrap">
          {formattedPctChange ? (
            <div
              className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs font-mono font-medium border ${dirStyles.textColor} ${dirStyles.badgeBg} ${dirStyles.badgeBorder}`}
            >
              {item.change_direction === "up" && (
                <ArrowUpRight className="h-3 w-3 shrink-0" aria-hidden="true" />
              )}
              {item.change_direction === "down" && (
                <ArrowDownRight className="h-3 w-3 shrink-0" aria-hidden="true" />
              )}
              <span>{formattedPctChange}</span>
              {formattedAbsChange && (
                <span className="text-[11px] opacity-80 ml-1">
                  ({formattedAbsChange})
                </span>
              )}
            </div>
          ) : (
            <span className="text-xs font-mono text-zinc-400 italic">
              {isAvailable ? "Change unavailable" : "No active quote"}
            </span>
          )}
        </div>
      </div>

      {/* 3. Footer: Freshness, Delay & Provenance */}
      <div className="pt-2.5 border-t border-zinc-800/60 flex items-center justify-between text-[11px] text-zinc-400 flex-wrap gap-1">
        {/* Freshness Badge */}
        <div className="flex items-center gap-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${freshness.dotColor}`} aria-hidden="true" />
          <span className="font-medium text-zinc-400">{freshness.label}</span>
          {delay.show && (
            <span className="text-amber-400/90 font-mono text-[10px] bg-amber-500/10 px-1 rounded">
              {delay.label}
            </span>
          )}
        </div>

        {/* Source Provider */}
        {item.provider_display_name && (
          <span className="text-zinc-400 font-mono text-[10px] truncate max-w-[110px]" title={item.provider_display_name}>
            {item.provider_display_name}
          </span>
        )}
      </div>
    </div>
  );
}
