"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { CryptoSpotMarketDirectoryItem } from "@/lib/markets/crypto";
import { CryptoSpotMarketRow } from "./CryptoSpotMarketRow";

export interface CryptoSpotMarketTableProps {
  markets: CryptoSpotMarketDirectoryItem[];
  selectedPairId: string | null;
  onSelectPair: (market: CryptoSpotMarketDirectoryItem) => void;
  isLoading: boolean;
  totalCount: number;
  nextCursor?: string | null;
  onNextPage: () => void;
  onPreviousPage: () => void;
  hasPreviousPage: boolean;
}

export function CryptoSpotMarketTable({
  markets,
  selectedPairId,
  onSelectPair,
  isLoading,
  totalCount,
  nextCursor,
  onNextPage,
  onPreviousPage,
  hasPreviousPage,
}: CryptoSpotMarketTableProps) {
  return (
    <div className="flex flex-col rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] overflow-hidden">
      {/* Table container */}
      <div className="overflow-x-auto no-scrollbar">
        <table
          className="w-full border-collapse text-left"
          aria-label="Cryptocurrency Spot Markets Directory"
        >
          <thead>
            <tr className="border-b border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-secondary)]/50 text-[11px] font-semibold text-[var(--atlas-text-secondary)] uppercase tracking-wider">
              <th scope="col" className="px-3 py-2.5">
                Trading Pair
              </th>
              <th scope="col" className="px-3 py-2.5">
                Exchange
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                Last Price
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                Bid
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                Ask
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                Spread
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                24h Change
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                24h Volume
              </th>
              <th scope="col" className="px-3 py-2.5 text-center">
                Status
              </th>
              <th scope="col" className="px-3 py-2.5 text-right">
                Source
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--atlas-border-subtle)] font-sans">
            {isLoading && markets.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-12 text-center text-xs text-[var(--atlas-text-tertiary)]">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
                    <span>Loading cryptocurrency spot markets...</span>
                  </div>
                </td>
              </tr>
            ) : markets.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-12 text-center text-xs text-[var(--atlas-text-tertiary)]">
                  No cryptocurrency spot markets found. Try adjusting your search query or filters.
                </td>
              </tr>
            ) : (
              markets.map((market) => (
                <CryptoSpotMarketRow
                  key={market.instrument_entity_id}
                  market={market}
                  isSelected={selectedPairId === market.instrument_entity_id}
                  onSelect={onSelectPair}
                />
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between px-3 py-2.5 border-t border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] text-xs text-[var(--atlas-text-secondary)]">
        <div>
          Showing <span className="font-medium text-[var(--atlas-text-primary)]">{markets.length}</span> of{" "}
          <span className="font-medium text-[var(--atlas-text-primary)]">{totalCount}</span> spot markets
        </div>

        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={onPreviousPage}
            disabled={!hasPreviousPage || isLoading}
            aria-label="Previous Page"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Prev</span>
          </button>
          <button
            type="button"
            onClick={onNextPage}
            disabled={!nextCursor || isLoading}
            aria-label="Next Page"
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-medium border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] hover:bg-[var(--atlas-surface-hover)] disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <span>Next</span>
            <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>
  );
}
