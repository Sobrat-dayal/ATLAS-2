"use client";

import React, { useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpDown,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Minus,
} from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import {
  MarketsOverviewItem,
  MarketTableSortField,
  SortDirection,
} from "@/lib/markets/types";
import {
  formatAbsoluteChange,
  formatMarketPrice,
  formatMarketTimestamp,
  formatPercentageChange,
  getChangeDirectionStyles,
  getDelayBadge,
  getFreshnessBadge,
} from "@/lib/markets/formatting";

export interface MarketsInstrumentTableProps {
  items: MarketsOverviewItem[];
  isLoading: boolean;
  hasMore: boolean;
  nextCursor?: string | null;
  cursor: string | null;
  onPageChange: (newCursor: string | null) => void;
}

export function MarketsInstrumentTable({
  items,
  isLoading,
  hasMore,
  nextCursor,
  cursor,
  onPageChange,
}: MarketsInstrumentTableProps) {
  const { selectEntity } = useSelectedEntity();
  const [sortField, setSortField] = useState<MarketTableSortField>("order");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");

  const handleSortToggle = (field: MarketTableSortField) => {
    if (sortField === field) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const sortedItems = useMemo(() => {
    if (!items || items.length === 0) return [];
    const copy = [...items];

    copy.sort((a, b) => {
      let comp = 0;
      switch (sortField) {
        case "name":
          comp = a.display_name.localeCompare(b.display_name);
          break;
        case "category":
          comp = a.instrument_category.localeCompare(b.instrument_category);
          break;
        case "price": {
          const numA = a.last_price ? Number(a.last_price) : -Infinity;
          const numB = b.last_price ? Number(b.last_price) : -Infinity;
          comp = numA - numB;
          break;
        }
        case "change": {
          const chgA = a.percentage_change ? Number(a.percentage_change) : -Infinity;
          const chgB = b.percentage_change ? Number(b.percentage_change) : -Infinity;
          comp = chgA - chgB;
          break;
        }
        case "order":
        default:
          comp = a.display_order - b.display_order;
          break;
      }
      return sortDirection === "asc" ? comp : -comp;
    });

    return copy;
  }, [items, sortField, sortDirection]);

  if (isLoading && (!items || items.length === 0)) {
    return (
      <div
        role="status"
        aria-label="Loading instruments table"
        className="rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] p-6 space-y-3"
      >
        <div className="h-4 bg-zinc-800 rounded w-1/4 animate-pulse" />
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, idx) => (
            <div key={idx} className="h-10 bg-zinc-800/40 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-zinc-900/60 text-[var(--atlas-text-secondary)] font-medium">
              <th scope="col" className="py-2.5 px-3">
                <button
                  type="button"
                  onClick={() => handleSortToggle("name")}
                  className="inline-flex items-center gap-1 hover:text-[var(--atlas-text-primary)] focus:outline-none"
                >
                  <span>Instrument</span>
                  <ArrowUpDown className="h-3 w-3 opacity-60" aria-hidden="true" />
                </button>
              </th>
              <th scope="col" className="py-2.5 px-3">
                <button
                  type="button"
                  onClick={() => handleSortToggle("category")}
                  className="inline-flex items-center gap-1 hover:text-[var(--atlas-text-primary)] focus:outline-none"
                >
                  <span>Category & Venue</span>
                  <ArrowUpDown className="h-3 w-3 opacity-60" aria-hidden="true" />
                </button>
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                <button
                  type="button"
                  onClick={() => handleSortToggle("price")}
                  className="inline-flex items-center gap-1 justify-end hover:text-[var(--atlas-text-primary)] focus:outline-none ml-auto"
                >
                  <span>Last Price</span>
                  <ArrowUpDown className="h-3 w-3 opacity-60" aria-hidden="true" />
                </button>
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                <span>Abs Change</span>
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                <button
                  type="button"
                  onClick={() => handleSortToggle("change")}
                  className="inline-flex items-center gap-1 justify-end hover:text-[var(--atlas-text-primary)] focus:outline-none ml-auto"
                >
                  <span>Change %</span>
                  <ArrowUpDown className="h-3 w-3 opacity-60" aria-hidden="true" />
                </button>
              </th>
              <th scope="col" className="py-2.5 px-3">
                <span>Unit</span>
              </th>
              <th scope="col" className="py-2.5 px-3">
                <span>Freshness</span>
              </th>
              <th scope="col" className="py-2.5 px-3">
                <span>Source & Time</span>
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                <span>Action</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--atlas-border-subtle)]/50 font-mono">
            {sortedItems.map((item) => {
              const { formattedValue, unitLabel } = formatMarketPrice(item);
              const absChangeStr = formatAbsoluteChange(item);
              const pctChangeStr = formatPercentageChange(item);
              const dirStyles = getChangeDirectionStyles(item.change_direction);
              const freshness = getFreshnessBadge(item.freshness_status);
              const delay = getDelayBadge(item.delivery_delay_status, item.delay_seconds);

              return (
                <tr
                  key={item.instrument_entity_id}
                  onClick={() => selectEntity(item.instrument_entity_id)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      selectEntity(item.instrument_entity_id);
                    }
                  }}
                  className="hover:bg-[var(--atlas-surface-hover)] cursor-pointer transition-colors focus:bg-[var(--atlas-surface-hover)] focus:outline-none"
                >
                  {/* Instrument */}
                  <td className="py-2 px-3">
                    <div className="flex items-center gap-1.5 font-sans">
                      <span className="font-medium text-[var(--atlas-text-primary)]">
                        {item.display_name}
                      </span>
                      {item.display_symbol && (
                        <span className="text-[11px] font-mono text-[var(--atlas-text-tertiary)]">
                          {item.display_symbol}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Category & Venue */}
                  <td className="py-2 px-3">
                    <div className="flex items-center gap-1 text-[11px]">
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-zinc-800 text-zinc-300 uppercase">
                        {item.instrument_category.replace("_", " ")}
                      </span>
                      {item.venue && (
                        <span className="text-[var(--atlas-text-tertiary)]">
                          {item.venue}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Last Price */}
                  <td className="py-2 px-3 text-right font-semibold text-[var(--atlas-text-primary)]">
                    {formattedValue}
                  </td>

                  {/* Abs Change */}
                  <td className={`py-2 px-3 text-right ${absChangeStr ? dirStyles.textColor : "text-zinc-500"}`}>
                    {absChangeStr || "—"}
                  </td>

                  {/* Change % */}
                  <td className="py-2 px-3 text-right">
                    {pctChangeStr ? (
                      <span
                        className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[11px] ${dirStyles.textColor} ${dirStyles.badgeBg} border ${dirStyles.badgeBorder}`}
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
                      </span>
                    ) : (
                      <span className="text-zinc-500">—</span>
                    )}
                  </td>

                  {/* Unit */}
                  <td className="py-2 px-3 text-[11px] text-[var(--atlas-text-tertiary)]">
                    {unitLabel || "—"}
                  </td>

                  {/* Freshness */}
                  <td className="py-2 px-3">
                    <div className="flex items-center gap-1.5 text-[11px]">
                      <span className={`h-1.5 w-1.5 rounded-full ${freshness.dotColor}`} />
                      <span className="text-[var(--atlas-text-secondary)]">{freshness.label}</span>
                      {delay.show && (
                        <span className="px-1 py-0.2 rounded text-[9px] bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          {delay.label}
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Source & Time */}
                  <td className="py-2 px-3 text-[11px] text-[var(--atlas-text-tertiary)]">
                    <div>
                      <span>{item.provider_display_name || "ATLAS Feed"}</span>
                      {item.source_timestamp && (
                        <span className="ml-1 text-[10px]">
                          ({formatMarketTimestamp(item.source_timestamp)})
                        </span>
                      )}
                    </div>
                  </td>

                  {/* Action */}
                  <td className="py-2 px-3 text-center">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        selectEntity(item.instrument_entity_id);
                      }}
                      className="p-1 rounded text-zinc-400 hover:text-emerald-400 hover:bg-zinc-800 transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
                      title="Select Entity (Stage 25)"
                      aria-label={`Select ${item.display_name}`}
                    >
                      <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {(hasMore || (cursor && cursor !== "0")) && (
        <div className="flex items-center justify-between px-3 py-2 border-t border-[var(--atlas-border-subtle)] bg-zinc-900/40 text-xs">
          <span className="text-[var(--atlas-text-tertiary)] font-mono">
            Showing {sortedItems.length} instruments
          </span>

          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={!cursor || cursor === "0"}
              onClick={() => onPageChange(null)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="h-3 w-3" />
              <span>First</span>
            </button>

            <button
              type="button"
              disabled={!hasMore}
              onClick={() => onPageChange(nextCursor || null)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] disabled:opacity-40 transition-colors"
            >
              <span>Next</span>
              <ChevronRight className="h-3 w-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
