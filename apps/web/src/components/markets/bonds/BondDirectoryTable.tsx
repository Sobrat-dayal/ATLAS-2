"use client";

import React from "react";
import { ChevronRight, Loader2 } from "lucide-react";
import { BondDirectoryItem } from "@/lib/markets/bonds";
import { BondDirectoryRow } from "./BondDirectoryRow";
import { BondEmptyState } from "./BondEmptyState";

export interface BondDirectoryTableProps {
  items: BondDirectoryItem[];
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  total: number;
  selectedId: string | null;
  onSelect: (item: BondDirectoryItem) => void;
  onResetFilters: () => void;
  onRetry: () => void;
  nextCursor?: string | null;
  hasMore: boolean;
  onNextPage?: () => void;
  hasActiveFilters: boolean;
}

export function BondDirectoryTable({
  items,
  isLoading,
  isError,
  errorMessage,
  total,
  selectedId,
  onSelect,
  onResetFilters,
  onRetry,
  nextCursor,
  hasMore,
  onNextPage,
  hasActiveFilters,
}: BondDirectoryTableProps) {
  if (isError) {
    return (
      <BondEmptyState
        type="error"
        errorMessage={errorMessage}
        onRetry={onRetry}
      />
    );
  }

  if (!isLoading && items.length === 0) {
    return (
      <BondEmptyState
        type={hasActiveFilters ? "no_matches" : "no_data"}
        onResetFilters={onResetFilters}
      />
    );
  }

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse" aria-label="Bond securities directory">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] text-[11px] font-mono text-[var(--atlas-text-tertiary)] uppercase tracking-wider">
              <th scope="col" className="py-2.5 px-3">
                Security / ISIN
              </th>
              <th scope="col" className="py-2.5 px-3">
                Security Name &amp; Issuer
              </th>
              <th scope="col" className="py-2.5 px-3">
                Debt Type
              </th>
              <th scope="col" className="py-2.5 px-3">
                Ccy
              </th>
              <th scope="col" className="py-2.5 px-3">
                Coupon Rate
              </th>
              <th scope="col" className="py-2.5 px-3">
                Maturity
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Observed Price
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Yield (YTM)
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                Status
              </th>
              <th scope="col" className="py-2.5 px-2 text-right">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <BondDirectoryRow
                key={item.instrument_entity_id}
                item={item}
                isSelected={item.instrument_entity_id === selectedId}
                onSelect={onSelect}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-3 py-2.5 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] text-xs text-[var(--atlas-text-secondary)]">
        <div className="flex items-center gap-2">
          {isLoading && (
            <span className="inline-flex items-center gap-1.5 text-emerald-400 font-mono text-[11px]">
              <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
              Loading securities...
            </span>
          )}
          {!isLoading && (
            <span className="font-mono text-[11px] text-[var(--atlas-text-tertiary)]">
              Showing {items.length} of {total} securities
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {hasMore && onNextPage && (
            <button
              type="button"
              onClick={onNextPage}
              disabled={isLoading || !nextCursor}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-[var(--atlas-text-primary)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] border border-[var(--atlas-border-subtle)] rounded transition-colors disabled:opacity-50"
            >
              <span>Next Page</span>
              <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
