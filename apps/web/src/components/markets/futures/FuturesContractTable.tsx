"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { FuturesContractDirectoryItem } from "@/lib/markets/futures";
import { FuturesContractRow } from "./FuturesContractRow";
import { FuturesEmptyState } from "./FuturesEmptyState";

export interface FuturesContractTableProps {
  contracts: FuturesContractDirectoryItem[];
  selectedContractId: string | null;
  onSelectContract: (id: string) => void;
  isLoading: boolean;
  total: number;
  hasMore: boolean;
  onNextPage: () => void;
  onPrevPage: () => void;
  canPrevPage: boolean;
  onResetFilters: () => void;
}

export function FuturesContractTable({
  contracts,
  selectedContractId,
  onSelectContract,
  isLoading,
  total,
  hasMore,
  onNextPage,
  onPrevPage,
  canPrevPage,
  onResetFilters,
}: FuturesContractTableProps) {
  if (isLoading && contracts.length === 0) {
    return (
      <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)]">
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">Contract</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">Underlying</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">Venue</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">Month</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)]">Expiry</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">Last</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">Settlement</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">Change</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">Volume</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-right">Open Int</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-center">Settlement</th>
                <th className="px-3 py-2 text-[10px] uppercase font-semibold text-[var(--atlas-text-tertiary)] text-center">Status</th>
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 10 }).map((_, i) => (
                <tr key={i} className="border-b border-[var(--atlas-border-subtle)] animate-pulse">
                  <td colSpan={12} className="px-3 py-4">
                    <div className="h-4 bg-[var(--atlas-surface-subtle)] rounded w-full" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  if (contracts.length === 0) {
    return (
      <FuturesEmptyState
        title="No Futures Contracts Found"
        description="No exchange-traded futures contracts match the selected query or filter criteria."
        onReset={onResetFilters}
      />
    );
  }

  return (
    <div className="rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] select-none">
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)]">
                Contract
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)]">
                Underlying Commodity
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)]">
                Venue
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)]">
                Month
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)]">
                Expiry
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-right">
                Last
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-right">
                Settlement
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-right">
                Change vs Settle
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-right">
                Volume
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-right">
                Open Int
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-center">
                Method
              </th>
              <th className="px-3 py-2 text-[10px] uppercase tracking-wider font-semibold text-[var(--atlas-text-tertiary)] text-center">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {contracts.map((c) => (
              <FuturesContractRow
                key={c.instrument_entity_id}
                contract={c}
                isSelected={c.instrument_entity_id === selectedContractId}
                onSelect={onSelectContract}
              />
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between px-3 py-2.5 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-subtle)] text-xs text-[var(--atlas-text-secondary)]">
        <div>
          Showing <span className="font-mono font-medium text-[var(--atlas-text-primary)]">{contracts.length}</span> of{" "}
          <span className="font-mono font-medium text-[var(--atlas-text-primary)]">{total}</span> contracts
        </div>
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onPrevPage}
            disabled={!canPrevPage || isLoading}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Prev</span>
          </button>
          <button
            type="button"
            onClick={onNextPage}
            disabled={!hasMore || isLoading}
            className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
