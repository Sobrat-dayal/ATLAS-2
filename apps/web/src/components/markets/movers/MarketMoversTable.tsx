"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import {
  MoverCategory,
  MoverRankedItem,
} from "@/lib/markets/movers";
import { MarketMoverRow } from "./MarketMoverRow";

export interface MarketMoversTableProps {
  items: MoverRankedItem[];
  category: MoverCategory;
  selectedItem: MoverRankedItem | null;
  onSelectItem: (item: MoverRankedItem) => void;
  isLoading: boolean;
  hasMore: boolean;
  nextCursor?: string | null;
  currentCursor?: string | null;
  onNextPage?: () => void;
  onPrevPage?: () => void;
}

export function MarketMoversTable({
  items,
  category,
  selectedItem,
  onSelectItem,
  isLoading,
  hasMore,
  currentCursor,
  onNextPage,
  onPrevPage,
}: MarketMoversTableProps) {
  if (isLoading && items.length === 0) {
    return (
      <div className="w-full bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg p-8 flex flex-col items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-7 w-7 border-2 border-emerald-500 border-t-transparent mb-3" />
        <span className="text-xs text-[var(--atlas-text-secondary)] font-medium">
          Evaluating qualified market movements...
        </span>
      </div>
    );
  }

  if (items.length === 0) {
    return null; // Empty state will be displayed by parent
  }

  return (
    <div className="w-full bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-lg overflow-hidden flex flex-col">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse" role="table">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-zinc-950/40 text-[11px] font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
              <th scope="col" className="py-2.5 px-3 text-center w-12">
                #
              </th>
              <th scope="col" className="py-2.5 px-3">
                Security / Pair
              </th>
              <th scope="col" className="py-2.5 px-3">
                Venue
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Last Traded
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Reference
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Change
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Change %
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Activity
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <MarketMoverRow
                key={`${item.market_series_identity}-${item.rank}`}
                item={item}
                category={category}
                isSelected={
                  selectedItem?.instrument_entity_id === item.instrument_entity_id
                }
                onSelect={onSelectItem}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      {(hasMore || currentCursor) && (
        <div className="flex items-center justify-between px-4 py-2.5 border-t border-[var(--atlas-border-subtle)] bg-zinc-950/20 text-xs text-[var(--atlas-text-secondary)]">
          <div className="flex items-center gap-1">
            <span>Showing</span>
            <span className="font-mono font-semibold text-[var(--atlas-text-primary)]">
              {items.length}
            </span>
            <span>ranked observations</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={!currentCursor || isLoading}
              onClick={onPrevPage}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </button>

            <button
              type="button"
              disabled={!hasMore || isLoading}
              onClick={onNextPage}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-800 text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <span>Next</span>
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
