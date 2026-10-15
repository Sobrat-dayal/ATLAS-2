"use client";

import React from "react";
import { FxPairDirectoryItem } from "@/lib/markets/fx";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { FxPairDirectoryRow } from "./FxPairDirectoryRow";

export interface FxPairDirectoryTableProps {
  items: FxPairDirectoryItem[];
  isLoading: boolean;
  selectedEntityId: string | null;
  onSelectEntity: (instrumentEntityId: string) => void;
  hasMore: boolean;
  nextCursor?: string | null;
  cursor?: string | null;
  onPageChange: (cursor: string | null) => void;
  totalMatched?: number;
}

export function FxPairDirectoryTable({
  items,
  isLoading,
  selectedEntityId,
  onSelectEntity,
  hasMore,
  nextCursor,
  cursor,
  onPageChange,
  totalMatched,
}: FxPairDirectoryTableProps) {
  const handlePrevPage = () => {
    // Offset-based back step
    if (!cursor) return;
    const curIdx = parseInt(cursor, 10);
    if (isNaN(curIdx) || curIdx <= 25) {
      onPageChange(null);
    } else {
      onPageChange(String(Math.max(0, curIdx - 50)));
    }
  };

  const handleNextPage = () => {
    if (nextCursor) {
      onPageChange(nextCursor);
    }
  };

  const isFirstPage = !cursor;

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md overflow-hidden flex flex-col">
      {/* Table Container */}
      <div className="overflow-x-auto w-full">
        <table className="w-full text-left border-collapse" aria-label="Currency Pairs Directory">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/80 text-[11px] font-semibold uppercase tracking-wider text-[var(--atlas-text-tertiary)]">
              <th scope="col" className="py-2.5 px-3">
                Currency Pair
              </th>
              <th scope="col" className="py-2.5 px-3">
                Rate Kind
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Bid
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Ask
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Midpoint
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Spread
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                24h Change
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                Status
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                Source
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Observed
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--atlas-border-subtle)]">
            {items.map((item) => (
              <FxPairDirectoryRow
                key={item.instrument_entity_id}
                item={item}
                isSelected={selectedEntityId === item.instrument_entity_id}
                onSelect={onSelectEntity}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/50 text-xs text-[var(--atlas-text-secondary)]">
        <div>
          {totalMatched !== undefined && (
            <span>
              Showing {items.length} of {totalMatched} {totalMatched === 1 ? "pair" : "pairs"}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handlePrevPage}
            disabled={isFirstPage || isLoading}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-3.5 w-3.5" />
            <span>Previous</span>
          </button>
          <button
            type="button"
            onClick={handleNextPage}
            disabled={!hasMore || isLoading}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium text-[var(--atlas-text-secondary)] hover:text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
