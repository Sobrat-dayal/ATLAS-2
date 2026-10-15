"use client";

import React from "react";
import { EquityDirectoryItem } from "@/lib/markets/equities";
import { EquityDirectoryRow } from "./EquityDirectoryRow";
import { ChevronLeft, ChevronRight } from "lucide-react";

export interface EquityDirectoryTableProps {
  items: EquityDirectoryItem[];
  isLoading: boolean;
  selectedEntityId: string | null;
  onSelectEntity: (instrumentEntityId: string) => void;
  hasMore: boolean;
  nextCursor?: string | null;
  cursor: string | null;
  onPageChange: (cursor: string | null) => void;
}

export function EquityDirectoryTable({
  items,
  isLoading,
  selectedEntityId,
  onSelectEntity,
  hasMore,
  nextCursor,
  cursor,
  onPageChange,
}: EquityDirectoryTableProps) {
  const currentOffset = cursor ? parseInt(cursor, 10) : 0;
  const pageSize = items.length;

  return (
    <div className="bg-[var(--atlas-surface-card)] border border-[var(--atlas-border-subtle)] rounded-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse" role="table">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/80 text-[11px] font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
              <th scope="col" className="py-2.5 px-3 text-left">
                Security
              </th>
              <th scope="col" className="py-2.5 px-3 text-left">
                Symbol
              </th>
              <th scope="col" className="py-2.5 px-3 text-left">
                Exchange
              </th>
              <th scope="col" className="py-2.5 px-3 text-left">
                Market
              </th>
              <th scope="col" className="py-2.5 px-3 text-left">
                CCY
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Last
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Change
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Change %
              </th>
              <th scope="col" className="py-2.5 px-3 text-center">
                Status
              </th>
              <th scope="col" className="py-2.5 px-3 text-right">
                Updated
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--atlas-border-subtle)]/50">
            {items.map((item) => (
              <EquityDirectoryRow
                key={`${item.instrument_entity_id}-${item.exchange_mic}`}
                item={item}
                isSelected={selectedEntityId === item.instrument_entity_id}
                onSelect={onSelectEntity}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="flex items-center justify-between px-3 py-2.5 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)]/50 text-xs text-[var(--atlas-text-secondary)]">
        <div>
          Showing{" "}
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {items.length > 0 ? currentOffset + 1 : 0}
          </span>{" "}
          to{" "}
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">
            {currentOffset + pageSize}
          </span>{" "}
          instruments
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={!cursor || currentOffset === 0 || isLoading}
            onClick={() => {
              // For offset-based cursor, navigate backward
              const prev = Math.max(0, currentOffset - 25);
              onPageChange(prev === 0 ? null : prev.toString());
            }}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Previous</span>
          </button>

          <button
            type="button"
            disabled={!hasMore || !nextCursor || isLoading}
            onClick={() => onPageChange(nextCursor || null)}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
