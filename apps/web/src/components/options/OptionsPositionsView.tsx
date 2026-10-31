"use client";

import React from "react";
import { OptionPositionItem } from "@/lib/options/types";
import { formatCurrency, formatNumber } from "@/lib/options/formatters";
import { Lock, PieChart, ShieldCheck } from "lucide-react";

interface OptionsPositionsViewProps {
  positions: OptionPositionItem[];
  portfolioId: string;
  onSelectPortfolio: (id: string) => void;
  currency?: string;
  isLoading?: boolean;
}

export function OptionsPositionsView({
  positions,
  portfolioId,
  onSelectPortfolio,
  currency = "USD",
  isLoading,
}: OptionsPositionsViewProps) {
  if (isLoading) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        Loading portfolio options positions...
      </div>
    );
  }

  const totalMarketVal = positions.reduce((acc, p) => acc + (p.market_value || 0), 0);
  const totalUnrealized = positions.reduce((acc, p) => acc + (p.unrealized_pnl || 0), 0);

  return (
    <div className="p-4 space-y-4 bg-zinc-950 overflow-y-auto h-full">
      {/* Portfolio Header & Multi-Tenant Isolation Badge */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-zinc-900/60 border border-zinc-800 p-3 rounded-lg">
        <div className="flex items-center gap-3">
          <PieChart className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-sm font-bold text-white">Options Portfolio Holdings</h3>
            <p className="text-xs text-zinc-500 mt-0.5">Portfolio ID: {portfolioId}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Tenant Isolated & RLS Enforced</span>
          </div>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div className="bg-zinc-900/50 border border-zinc-850 p-3 rounded-lg">
          <div className="text-zinc-500 text-xs">Total Options Market Value</div>
          <div className="font-mono text-lg font-bold text-white mt-1">
            {formatCurrency(totalMarketVal, currency)}
          </div>
        </div>
        <div className="bg-zinc-900/50 border border-zinc-850 p-3 rounded-lg">
          <div className="text-zinc-500 text-xs">Total Unrealized P&L</div>
          <div
            className={`font-mono text-lg font-bold mt-1 ${
              totalUnrealized >= 0 ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {formatCurrency(totalUnrealized, currency)}
          </div>
        </div>
      </div>

      {/* Positions Table */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg overflow-hidden">
        {positions.length === 0 ? (
          <div className="p-8 text-center text-xs text-zinc-500">
            No active options positions held in portfolio {portfolioId}.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead className="bg-zinc-900 border-b border-zinc-800 text-[10px] text-zinc-500 uppercase tracking-wider">
                <tr>
                  <th className="py-2 px-3">Underlying</th>
                  <th className="py-2 px-3">Type</th>
                  <th className="py-2 px-3 text-right">Strike</th>
                  <th className="py-2 px-3">Expiration</th>
                  <th className="py-2 px-3 text-right">Side / Qty</th>
                  <th className="py-2 px-3 text-right">Multiplier</th>
                  <th className="py-2 px-3 text-right">Entry Cost</th>
                  <th className="py-2 px-3 text-right">Market Price</th>
                  <th className="py-2 px-3 text-right">Market Value</th>
                  <th className="py-2 px-3 text-right">Unrealized P&L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {positions.map((pos) => {
                  const isCall = pos.option_type === "CALL";
                  const pnl = pos.unrealized_pnl || 0;

                  return (
                    <tr key={pos.contract_id} className="hover:bg-zinc-800/40 transition-colors">
                      <td className="py-2 px-3 font-bold text-white">{pos.underlying_symbol}</td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            isCall
                              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                              : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                          }`}
                        >
                          {pos.option_type}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-200">
                        {formatCurrency(pos.strike_price, currency)}
                      </td>
                      <td className="py-2 px-3 text-zinc-400">{pos.expiration_date}</td>
                      <td className="py-2 px-3 text-right">
                        <span
                          className={pos.is_long ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}
                        >
                          {pos.is_long ? "LONG" : "SHORT"} {pos.quantity}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-400">{pos.multiplier}</td>
                      <td className="py-2 px-3 text-right text-zinc-300">
                        {formatCurrency(pos.entry_cost, currency)}
                      </td>
                      <td className="py-2 px-3 text-right text-zinc-200">
                        {pos.current_market_price !== null && pos.current_market_price !== undefined
                          ? formatCurrency(pos.current_market_price, currency)
                          : "—"}
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-white">
                        {pos.market_value !== null && pos.market_value !== undefined
                          ? formatCurrency(pos.market_value, currency)
                          : "—"}
                      </td>
                      <td
                        className={`py-2 px-3 text-right font-bold ${
                          pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {formatCurrency(pnl, currency)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="p-2.5 bg-zinc-900/30 rounded border border-zinc-850 text-[10px] text-zinc-500">
        <span className="font-semibold text-zinc-400">Read-Only Strategy Analytics:</span> ATLAS is an institutional research and analytical intelligence system. Order routing, paper trading, and broker execution sandbox integrations are scheduled for Stages 144–145.
      </div>
    </div>
  );
}
