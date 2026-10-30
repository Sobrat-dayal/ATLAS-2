"use client";

import React, { useMemo, useState } from "react";
import { CurrentVsCandidateItemDTO } from "@/lib/portfolios/optimization/types";
import {
  formatBps,
  formatCurrency,
  formatPercent,
  formatWeightPercent,
} from "@/lib/portfolios/optimization/formatting";
import {
  AlertTriangle,
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle,
  Copy,
  DollarSign,
  Download,
  Info,
  Scale,
} from "lucide-react";

interface HypotheticalTradeTableProps {
  comparisons: CurrentVsCandidateItemDTO[];
  baseCurrency?: string;
  baselineNav?: string;
  estimatedTurnover?: string;
  estimatedCost?: string;
}

export function HypotheticalTradeTable({
  comparisons,
  baseCurrency = "USD",
  baselineNav = "0",
  estimatedTurnover = "0",
  estimatedCost = "0",
}: HypotheticalTradeTableProps) {
  const [filterAction, setFilterAction] = useState<"ALL" | "BUY" | "SELL">("ALL");
  const [copied, setCopied] = useState<boolean>(false);

  // Filter comparisons where delta != 0
  const activeTrades = useMemo(() => {
    return comparisons.filter((item) => {
      const delta = Math.abs(parseFloat(item.weight_delta) || 0);
      if (delta < 0.0001) return false;
      if (filterAction === "BUY") return item.trade_direction === "BUY";
      if (filterAction === "SELL") return item.trade_direction === "SELL";
      return true;
    });
  }, [comparisons, filterAction]);

  // Aggregated rebalancing statistics
  const stats = useMemo(() => {
    let grossBuys = 0;
    let grossSells = 0;
    let totalCost = 0;

    comparisons.forEach((c) => {
      const tradeVal = parseFloat(c.trade_value_delta) || 0;
      const cost = parseFloat(c.estimated_cost) || 0;
      totalCost += cost;

      if (c.trade_direction === "BUY") {
        grossBuys += Math.abs(tradeVal);
      } else if (c.trade_direction === "SELL") {
        grossSells += Math.abs(tradeVal);
      }
    });

    const netCashDelta = grossSells - grossBuys;
    const isSelfFunding = Math.abs(netCashDelta) < 1.0;

    return {
      grossBuys,
      grossSells,
      netCashDelta,
      isSelfFunding,
      totalCost,
    };
  }, [comparisons]);

  const handleCopy = () => {
    const headers = "Symbol,Name,Direction,Current Weight,Target Weight,Delta Weight,Trade Value,Est Cost\n";
    const rows = comparisons
      .map(
        (c) =>
          `"${c.symbol}","${c.name}","${c.trade_direction}","${c.current_weight}","${c.candidate_weight}","${c.weight_delta}","${c.trade_value_delta}","${c.estimated_cost}"`
      )
      .join("\n");

    navigator.clipboard.writeText(headers + rows);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      {/* Prominent Institutional Non-Execution Disclaimer */}
      <div className="flex items-start gap-3 rounded border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-300">
        <AlertTriangle className="h-5 w-5 shrink-0 text-amber-400 mt-0.5" />
        <div className="space-y-1">
          <p className="font-bold uppercase tracking-wider text-amber-200">
            Hypothetical Rebalancing Plan — Decision Support Only
          </p>
          <p className="text-amber-300/90 leading-relaxed text-[11px]">
            Candidate trades are mathematically derived target weights designed for portfolio analysis and rebalancing evaluation.
            <strong className="text-amber-200"> No orders have been placed with brokers, sent to execution venues, or posted to the Stage 110 accounting ledger.</strong>
          </p>
        </div>
      </div>

      {/* Rebalancing Summary KPI Ribbon */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-5">
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">Gross Buys</span>
          <p className="mt-1 font-mono text-sm font-bold text-emerald-400">
            +{formatCurrency(stats.grossBuys, baseCurrency)}
          </p>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">Gross Sells</span>
          <p className="mt-1 font-mono text-sm font-bold text-rose-400">
            -{formatCurrency(stats.grossSells, baseCurrency)}
          </p>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">Net Cash Delta</span>
          <div className="mt-1 flex items-center gap-1.5">
            <span
              className={`font-mono text-sm font-bold ${
                stats.isSelfFunding
                  ? "text-cyan-300"
                  : stats.netCashDelta >= 0
                  ? "text-emerald-400"
                  : "text-rose-400"
              }`}
            >
              {stats.netCashDelta >= 0 ? "+" : ""}
              {formatCurrency(stats.netCashDelta, baseCurrency)}
            </span>
            {stats.isSelfFunding && (
              <span className="rounded bg-cyan-500/10 px-1.5 py-0.2 text-[9px] font-semibold text-cyan-300">
                BALANCED
              </span>
            )}
          </div>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">Est. Transaction Cost</span>
          <p className="mt-1 font-mono text-sm font-bold text-amber-300">
            {formatCurrency(stats.totalCost, baseCurrency)}
          </p>
        </div>

        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
          <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">One-Way Turnover</span>
          <p className="mt-1 font-mono text-sm font-bold text-atlas-text-primary">
            {formatWeightPercent(parseFloat(estimatedTurnover) || 0)}
          </p>
        </div>
      </div>

      {/* Filter and Actions Bar */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs text-atlas-text-muted">Filter Orders:</span>
            <div className="inline-flex rounded border border-atlas-border-default/60 bg-atlas-surface-2 p-0.5 text-xs">
              {(["ALL", "BUY", "SELL"] as const).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setFilterAction(mode)}
                  className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
                    filterAction === mode
                      ? "bg-atlas-surface-1 text-atlas-text-primary shadow-sm"
                      : "text-atlas-text-muted hover:text-atlas-text-primary"
                  }`}
                >
                  {mode === "ALL" ? `All (${activeTrades.length})` : mode}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 rounded border border-atlas-border-default/60 bg-atlas-surface-2 px-2.5 py-1 text-xs text-atlas-text-secondary hover:text-atlas-text-primary transition-colors"
            >
              <Copy className="h-3.5 w-3.5" />
              <span>{copied ? "Copied CSV!" : "Copy Orders"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="overflow-hidden rounded border border-atlas-border-default/60 bg-atlas-surface-1">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/40 text-atlas-text-muted">
                <th className="px-4 py-2.5 font-medium">Action</th>
                <th className="px-4 py-2.5 font-medium">Symbol / Security</th>
                <th className="px-4 py-2.5 font-medium">Sector</th>
                <th className="px-4 py-2.5 font-medium text-right">Current Wt</th>
                <th className="px-4 py-2.5 font-medium text-right">Target Wt</th>
                <th className="px-4 py-2.5 font-medium text-right">Delta Wt</th>
                <th className="px-4 py-2.5 font-medium text-right">Target Trade Value</th>
                <th className="px-4 py-2.5 font-medium text-right">Est. Cost (10 bps)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-atlas-border-default/40">
              {activeTrades.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-atlas-text-muted">
                    No rebalancing trades required. Target portfolio matches current weights.
                  </td>
                </tr>
              ) : (
                activeTrades.map((item) => {
                  const isBuy = item.trade_direction === "BUY";
                  const isSell = item.trade_direction === "SELL";
                  const tradeVal = parseFloat(item.trade_value_delta) || 0;
                  const deltaWt = parseFloat(item.weight_delta) || 0;

                  return (
                    <tr key={item.symbol} className="hover:bg-atlas-surface-2/30 transition-colors">
                      {/* Action Badge */}
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-[10px] font-bold ${
                            isBuy
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : isSell
                              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              : "bg-slate-500/10 text-slate-400"
                          }`}
                        >
                          {isBuy ? (
                            <ArrowUpRight className="h-3 w-3" />
                          ) : (
                            <ArrowDownRight className="h-3 w-3" />
                          )}
                          {item.trade_direction}
                        </span>
                      </td>

                      {/* Symbol & Name */}
                      <td className="px-4 py-3">
                        <div className="font-mono font-bold text-atlas-text-primary">
                          {item.symbol}
                        </div>
                        <div className="truncate text-[11px] text-atlas-text-muted max-w-[200px]">
                          {item.name}
                        </div>
                      </td>

                      {/* Sector */}
                      <td className="px-4 py-3 text-atlas-text-secondary text-[11px]">
                        {item.category_label || item.category_id || "—"}
                      </td>

                      {/* Current Weight */}
                      <td className="px-4 py-3 text-right font-mono text-atlas-text-muted">
                        {formatWeightPercent(parseFloat(item.current_weight) || 0)}
                      </td>

                      {/* Target Weight */}
                      <td className="px-4 py-3 text-right font-mono font-semibold text-cyan-300">
                        {formatWeightPercent(parseFloat(item.candidate_weight) || 0)}
                      </td>

                      {/* Delta Weight */}
                      <td
                        className={`px-4 py-3 text-right font-mono font-bold ${
                          deltaWt > 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {deltaWt > 0 ? "+" : ""}
                        {(deltaWt * 100).toFixed(2)}%
                      </td>

                      {/* Trade Value Delta */}
                      <td
                        className={`px-4 py-3 text-right font-mono font-semibold ${
                          tradeVal > 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {tradeVal > 0 ? "+" : ""}
                        {formatCurrency(tradeVal, baseCurrency)}
                      </td>

                      {/* Est Cost */}
                      <td className="px-4 py-3 text-right font-mono text-amber-300">
                        {formatCurrency(parseFloat(item.estimated_cost) || 0, baseCurrency)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
