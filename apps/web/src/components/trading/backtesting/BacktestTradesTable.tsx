"use client";

import React, { useState } from "react";
import { TradeRecord } from "@/lib/trading/backtesting/types";
import { formatCurrency, formatPercent } from "@/lib/trading/backtesting/formatters";
import {
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  ExternalLink,
} from "lucide-react";

interface BacktestTradesTableProps {
  trades: TradeRecord[];
}

export function BacktestTradesTable({ trades }: BacktestTradesTableProps) {
  const [filterType, setFilterType] = useState<"ALL" | "WIN" | "LOSS">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTrade, setSelectedTrade] = useState<TradeRecord | null>(null);

  const filteredTrades = trades.filter((t) => {
    if (filterType === "WIN" && t.net_pnl <= 0) return false;
    if (filterType === "LOSS" && t.net_pnl >= 0) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        t.trade_id.toLowerCase().includes(q) ||
        t.instrument_id.toLowerCase().includes(q) ||
        t.exit_reason.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 text-neutral-200">
      {/* Header and Controls */}
      <div className="flex flex-wrap items-center justify-between pb-4 border-b border-neutral-800 gap-3 mb-4">
        <div>
          <h3 className="text-sm font-semibold tracking-wide text-neutral-100">
            Trade Blotter & Executed Fills
          </h3>
          <p className="text-xs text-neutral-400 mt-0.5">
            Trade-by-trade audit showing slippage, commissions, and holding durations
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-500" />
            <input
              type="text"
              placeholder="Search trade ID or instrument..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-neutral-950 border border-neutral-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-neutral-200 focus:outline-none focus:border-amber-400 w-52"
            />
          </div>

          {/* Filter Pills */}
          <div className="flex items-center bg-neutral-950 border border-neutral-800 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setFilterType("ALL")}
              className={`px-2.5 py-1 rounded ${
                filterType === "ALL"
                  ? "bg-neutral-800 text-neutral-100 font-semibold"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              All ({trades.length})
            </button>
            <button
              onClick={() => setFilterType("WIN")}
              className={`px-2.5 py-1 rounded ${
                filterType === "WIN"
                  ? "bg-emerald-950 text-emerald-300 font-semibold"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              Winners
            </button>
            <button
              onClick={() => setFilterType("LOSS")}
              className={`px-2.5 py-1 rounded ${
                filterType === "LOSS"
                  ? "bg-rose-950 text-rose-300 font-semibold"
                  : "text-neutral-400 hover:text-neutral-200"
              }`}
            >
              Losers
            </button>
          </div>
        </div>
      </div>

      {/* Trades Table */}
      {filteredTrades.length === 0 ? (
        <div className="text-center py-10 text-neutral-500 text-xs">
          No trades matching the selected criteria.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-neutral-800 text-neutral-400 uppercase tracking-wider text-[10px]">
                <th className="pb-2.5 font-medium">Trade ID</th>
                <th className="pb-2.5 font-medium">Instrument</th>
                <th className="pb-2.5 font-medium">Side</th>
                <th className="pb-2.5 font-medium">Entry</th>
                <th className="pb-2.5 font-medium">Exit</th>
                <th className="pb-2.5 font-medium">Duration</th>
                <th className="pb-2.5 font-medium text-right">Qty</th>
                <th className="pb-2.5 font-medium text-right">Commissions</th>
                <th className="pb-2.5 font-medium text-right">Slippage</th>
                <th className="pb-2.5 font-medium text-right">Net P&L</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-800/60 font-mono text-[11px]">
              {filteredTrades.map((t) => {
                const isWin = t.net_pnl > 0;
                return (
                  <tr
                    key={t.trade_id}
                    onClick={() => setSelectedTrade(t)}
                    className="hover:bg-neutral-800/40 cursor-pointer transition-colors"
                  >
                    <td className="py-2.5 text-neutral-300 font-sans font-medium">
                      {t.trade_id}
                    </td>
                    <td className="py-2.5 text-neutral-300 font-sans">{t.instrument_id}</td>
                    <td className="py-2.5">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-sans font-semibold ${
                          t.direction === "LONG"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60"
                            : "bg-rose-950 text-rose-400 border border-rose-800/60"
                        }`}
                      >
                        {t.direction}
                      </span>
                    </td>
                    <td className="py-2.5 text-neutral-300">
                      <div>${t.entry_price.toFixed(2)}</div>
                      <div className="text-[10px] text-neutral-500">{t.entry_time.split(" ")[0]}</div>
                    </td>
                    <td className="py-2.5 text-neutral-300">
                      <div>${t.exit_price.toFixed(2)}</div>
                      <div className="text-[10px] text-neutral-500">{t.exit_time.split(" ")[0]}</div>
                    </td>
                    <td className="py-2.5 text-neutral-400 font-sans">
                      {t.holding_period_days}d
                    </td>
                    <td className="py-2.5 text-right text-neutral-300">{t.quantity}</td>
                    <td className="py-2.5 text-right text-neutral-400">
                      ${t.commissions.toFixed(2)}
                    </td>
                    <td className="py-2.5 text-right text-neutral-400">
                      ${t.slippage_cost.toFixed(2)}
                    </td>
                    <td
                      className={`py-2.5 text-right font-bold ${
                        isWin ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {formatCurrency(t.net_pnl)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Selected Trade Inspector Modal */}
      {selectedTrade && (
        <div className="fixed inset-0 bg-neutral-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-neutral-900 border border-neutral-700 rounded-xl max-w-lg w-full p-6 text-neutral-200 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-neutral-800">
              <h4 className="text-base font-semibold text-neutral-100">
                Trade Inspector — {selectedTrade.trade_id}
              </h4>
              <button
                onClick={() => setSelectedTrade(null)}
                className="text-neutral-400 hover:text-neutral-200 text-sm font-semibold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Instrument</span>
                <span className="font-semibold text-neutral-200">{selectedTrade.instrument_id}</span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Direction</span>
                <span className="font-semibold text-neutral-200">{selectedTrade.direction}</span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Entry Fill</span>
                <span className="font-semibold text-neutral-200 font-mono">
                  ${selectedTrade.entry_price.toFixed(2)} ({selectedTrade.entry_time})
                </span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Exit Fill</span>
                <span className="font-semibold text-neutral-200 font-mono">
                  ${selectedTrade.exit_price.toFixed(2)} ({selectedTrade.exit_time})
                </span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Gross P&L</span>
                <span className="font-semibold font-mono text-neutral-200">
                  {formatCurrency(selectedTrade.gross_pnl)}
                </span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Net P&L</span>
                <span
                  className={`font-semibold font-mono ${
                    selectedTrade.net_pnl > 0 ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {formatCurrency(selectedTrade.net_pnl)}
                </span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Commissions Paid</span>
                <span className="font-semibold font-mono text-neutral-200">
                  ${selectedTrade.commissions.toFixed(2)}
                </span>
              </div>
              <div className="bg-neutral-950 p-2.5 rounded-lg border border-neutral-800">
                <span className="text-neutral-500 block">Slippage Impact</span>
                <span className="font-semibold font-mono text-neutral-200">
                  ${selectedTrade.slippage_cost.toFixed(2)}
                </span>
              </div>
            </div>

            <div className="p-3 bg-neutral-950 rounded-lg border border-neutral-800 text-xs">
              <span className="text-neutral-500 block mb-1">Exit Attribution Reason:</span>
              <span className="text-neutral-300 font-mono">{selectedTrade.exit_reason}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

