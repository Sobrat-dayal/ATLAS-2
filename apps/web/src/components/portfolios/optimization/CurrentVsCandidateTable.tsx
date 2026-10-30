"use client";

import React, { useMemo, useState } from "react";
import { Badge } from "@/design-system";
import {
  formatCurrency,
  formatPercent,
  formatWeightPercent,
  getTradeDirectionBadge,
} from "@/lib/portfolios/optimization/formatting";
import {
  CurrentVsCandidateItemDTO,
  PortfolioOptimizationRunDTO,
} from "@/lib/portfolios/optimization/types";
import { ArrowDown, ArrowUp, ArrowUpDown, Filter, Search } from "lucide-react";

interface CurrentVsCandidateTableProps {
  run: PortfolioOptimizationRunDTO;
}

export function CurrentVsCandidateTable({ run }: CurrentVsCandidateTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [directionFilter, setDirectionFilter] = useState<string>("ALL");

  const filteredItems = useMemo(() => {
    return (run.comparisons || []).filter((item) => {
      const matchesSearch =
        item.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.category_label.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesDirection =
        directionFilter === "ALL" || item.trade_direction === directionFilter;

      return matchesSearch && matchesDirection;
    });
  }, [run.comparisons, searchQuery, directionFilter]);

  // Totals
  const totals = useMemo(() => {
    let currVal = 0.0;
    let candVal = 0.0;
    let tradeVal = 0.0;
    let totalCost = 0.0;

    for (const item of run.comparisons || []) {
      currVal += parseFloat(item.current_value || "0");
      candVal += parseFloat(item.candidate_value || "0");
      tradeVal += parseFloat(item.trade_value_delta || "0");
      totalCost += parseFloat(item.estimated_cost || "0");
    }

    return {
      currentValue: currVal,
      candidateValue: candVal,
      tradeDelta: tradeVal,
      totalCost: totalCost,
    };
  }, [run.comparisons]);

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      {/* Header and Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/60 p-3">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Current vs Candidate Portfolio Allocation
          </h3>
          <p className="text-[12px] text-atlas-text-secondary">
            Comparative security-level weight deltas and hypothetical trade orders.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-atlas-text-muted" />
            <input
              type="text"
              placeholder="Search symbol, name, or sector..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-8 w-56 rounded border border-atlas-border-default bg-atlas-surface-2 pl-8 pr-3 text-[12px] text-atlas-text-primary placeholder-atlas-text-muted focus:border-cyan-500 focus:outline-none"
            />
          </div>

          {/* Direction Filter */}
          <div className="flex rounded border border-atlas-border-default bg-atlas-surface-2 p-0.5 text-[11px] font-mono">
            {["ALL", "BUY", "SELL", "HOLD"].map((dir) => (
              <button
                key={dir}
                onClick={() => setDirectionFilter(dir)}
                className={`rounded px-2 py-1 transition-colors ${
                  directionFilter === dir
                    ? "bg-atlas-surface-3 text-cyan-400 font-semibold"
                    : "text-atlas-text-muted hover:text-atlas-text-secondary"
                }`}
              >
                {dir}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Dense Data Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-[12px] font-mono border-collapse">
          <thead>
            <tr className="border-b border-atlas-border-default/40 bg-atlas-surface-2/60 text-[11px] uppercase tracking-wider text-atlas-text-secondary">
              <th className="py-2.5 pl-4 pr-2 font-medium">Symbol</th>
              <th className="py-2.5 px-2 font-medium">Name</th>
              <th className="py-2.5 px-2 font-medium">Sector</th>
              <th className="py-2.5 px-2 text-right font-medium">Current Wt</th>
              <th className="py-2.5 px-2 text-right font-medium">Target Wt</th>
              <th className="py-2.5 px-2 text-right font-medium">Delta Wt</th>
              <th className="py-2.5 px-2 text-right font-medium">Current Value</th>
              <th className="py-2.5 px-2 text-right font-medium">Candidate Value</th>
              <th className="py-2.5 px-2 text-right font-medium">Trade Delta</th>
              <th className="py-2.5 px-2 text-center font-medium">Action</th>
              <th className="py-2.5 pr-4 pl-2 text-right font-medium">Est. Cost</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/20">
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan={11} className="py-8 text-center text-atlas-text-muted">
                  No assets match the active filter criteria.
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => {
                const deltaNum = parseFloat(item.weight_delta || "0");
                const badge = getTradeDirectionBadge(item.trade_direction);
                return (
                  <tr
                    key={item.symbol}
                    className="hover:bg-atlas-surface-2/50 transition-colors"
                  >
                    <td className="py-2 pl-4 pr-2 font-bold text-atlas-text-primary">
                      {item.symbol}
                    </td>
                    <td className="py-2 px-2 text-atlas-text-secondary truncate max-w-[150px]">
                      {item.name}
                    </td>
                    <td className="py-2 px-2 text-atlas-text-muted text-[11px]">
                      {item.category_label}
                    </td>
                    <td className="py-2 px-2 text-right text-atlas-text-secondary">
                      {formatWeightPercent(item.current_weight, 2)}
                    </td>
                    <td className="py-2 px-2 text-right font-semibold text-atlas-text-primary">
                      {formatWeightPercent(item.candidate_weight, 2)}
                    </td>
                    <td
                      className={`py-2 px-2 text-right font-semibold ${
                        deltaNum > 0
                          ? "text-emerald-400"
                          : deltaNum < 0
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {formatPercent(item.weight_delta, 2)}
                    </td>
                    <td className="py-2 px-2 text-right text-atlas-text-muted">
                      {formatCurrency(item.current_value, run.base_currency)}
                    </td>
                    <td className="py-2 px-2 text-right text-atlas-text-primary">
                      {formatCurrency(item.candidate_value, run.base_currency)}
                    </td>
                    <td
                      className={`py-2 px-2 text-right font-semibold ${
                        parseFloat(item.trade_value_delta) > 0
                          ? "text-emerald-400"
                          : parseFloat(item.trade_value_delta) < 0
                          ? "text-rose-400"
                          : "text-atlas-text-muted"
                      }`}
                    >
                      {formatCurrency(item.trade_value_delta, run.base_currency)}
                    </td>
                    <td className="py-2 px-2 text-center">
                      <span
                        className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-bold border ${badge.className}`}
                      >
                        {badge.label}
                      </span>
                    </td>
                    <td className="py-2 pr-4 pl-2 text-right text-atlas-text-muted text-[11px]">
                      {formatCurrency(item.estimated_cost, run.base_currency)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
          {/* Summary Footer */}
          <tfoot>
            <tr className="border-t-2 border-atlas-border-default/80 bg-atlas-surface-2/70 font-semibold text-atlas-text-primary">
              <td className="py-2.5 pl-4 pr-2" colSpan={3}>
                Portfolio Totals ({run.universe_symbols.length} Universe Assets)
              </td>
              <td className="py-2.5 px-2 text-right">100.00%</td>
              <td className="py-2.5 px-2 text-right">100.00%</td>
              <td className="py-2.5 px-2 text-right text-atlas-text-muted">0.00%</td>
              <td className="py-2.5 px-2 text-right">
                {formatCurrency(totals.currentValue, run.base_currency)}
              </td>
              <td className="py-2.5 px-2 text-right">
                {formatCurrency(totals.candidateValue, run.base_currency)}
              </td>
              <td className="py-2.5 px-2 text-right text-cyan-400">
                {formatCurrency(totals.tradeDelta, run.base_currency)}
              </td>
              <td className="py-2.5 px-2 text-center text-[10px] text-zinc-400">
                SELF-FUNDING
              </td>
              <td className="py-2.5 pr-4 pl-2 text-right text-amber-400">
                {formatCurrency(totals.totalCost, run.base_currency)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
