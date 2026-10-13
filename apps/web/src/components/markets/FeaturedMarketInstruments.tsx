"use client";

import React from "react";
import { ArrowDownRight, ArrowUpRight, Minus, Star } from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import { MarketsOverviewItem } from "@/lib/markets/types";
import {
  formatAbsoluteChange,
  formatMarketPrice,
  formatPercentageChange,
  getChangeDirectionStyles,
  getDelayBadge,
  getFreshnessBadge,
} from "@/lib/markets/formatting";

export interface FeaturedMarketInstrumentsProps {
  items: MarketsOverviewItem[];
}

export function FeaturedMarketInstruments({ items }: FeaturedMarketInstrumentsProps) {
  const { selectEntity } = useSelectedEntity();

  if (!items || items.length === 0) return null;

  return (
    <section aria-label="Featured Market Instruments" className="mb-6">
      <div className="flex items-center gap-1.5 mb-2.5">
        <Star className="h-3.5 w-3.5 text-amber-400 fill-amber-400/30" aria-hidden="true" />
        <h2 className="text-xs font-semibold uppercase tracking-wider text-[var(--atlas-text-secondary)]">
          Featured Benchmarks & Markets
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {items.map((item) => {
          const { formattedValue, unitLabel } = formatMarketPrice(item);
          const absChangeStr = formatAbsoluteChange(item);
          const pctChangeStr = formatPercentageChange(item);
          const dirStyles = getChangeDirectionStyles(item.change_direction);
          const freshness = getFreshnessBadge(item.freshness_status);
          const delay = getDelayBadge(item.delivery_delay_status, item.delay_seconds);

          return (
            <div
              key={item.instrument_entity_id}
              role="button"
              tabIndex={0}
              onClick={() => selectEntity(item.instrument_entity_id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  selectEntity(item.instrument_entity_id);
                }
              }}
              className="flex flex-col justify-between p-3 rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:border-emerald-500/40 hover:bg-[var(--atlas-surface-hover)] transition-all cursor-pointer group text-left focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-xs text-[var(--atlas-text-primary)] truncate group-hover:text-emerald-400 transition-colors">
                      {item.display_name}
                    </span>
                    {item.display_symbol && (
                      <span className="font-mono text-[10px] text-[var(--atlas-text-tertiary)]">
                        {item.display_symbol}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] text-[var(--atlas-text-tertiary)] font-mono mt-0.5">
                    <span className="uppercase">{item.instrument_category.replace("_", " ")}</span>
                    {item.venue && <span>• {item.venue}</span>}
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1">
                  <span
                    className="inline-flex items-center gap-1 text-[10px] font-mono text-[var(--atlas-text-tertiary)]"
                    title={`Freshness: ${freshness.label}`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${freshness.dotColor}`} />
                    <span className="hidden xl:inline">{freshness.label}</span>
                  </span>
                  {delay.show && (
                    <span className="px-1 py-0.2 rounded text-[9px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {delay.label}
                    </span>
                  )}
                </div>
              </div>

              <div className="flex items-baseline justify-between gap-2 pt-1 border-t border-[var(--atlas-border-subtle)]/50">
                <div className="flex items-baseline gap-1 font-mono">
                  <span className="text-base font-bold text-[var(--atlas-text-primary)]">
                    {formattedValue}
                  </span>
                  {unitLabel && (
                    <span className="text-[10px] text-[var(--atlas-text-tertiary)]">
                      {unitLabel}
                    </span>
                  )}
                </div>

                {pctChangeStr ? (
                  <div
                    className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] font-mono font-medium ${dirStyles.textColor} ${dirStyles.badgeBg} border ${dirStyles.badgeBorder}`}
                  >
                    {item.change_direction === "up" && (
                      <ArrowUpRight className="h-3 w-3" aria-hidden="true" />
                    )}
                    {item.change_direction === "down" && (
                      <ArrowDownRight className="h-3 w-3" aria-hidden="true" />
                    )}
                    {item.change_direction === "flat" && (
                      <Minus className="h-3 w-3" aria-hidden="true" />
                    )}
                    <span>{pctChangeStr}</span>
                  </div>
                ) : (
                  <span className="text-[11px] font-mono text-zinc-500">—</span>
                )}
              </div>

              {absChangeStr && (
                <div className="flex justify-end text-[10px] font-mono text-[var(--atlas-text-tertiary)] mt-0.5">
                  <span>{absChangeStr}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
