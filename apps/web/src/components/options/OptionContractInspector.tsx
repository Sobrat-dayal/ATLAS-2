"use client";

import React from "react";
import {
  X,
  FileText,
  AlertTriangle,
  Clock,
  Layers,
  Activity,
  CheckCircle2,
  DollarSign,
  ShieldAlert,
} from "lucide-react";
import { AtlasOptionContract, OptionQuote } from "@/lib/options/types";
import {
  formatCurrency,
  formatPercent,
  formatNumber,
  formatQualityFlag,
} from "@/lib/options/formatters";

interface OptionContractInspectorProps {
  contract: AtlasOptionContract | null;
  quote: OptionQuote | null;
  onClose: () => void;
}

export function OptionContractInspector({
  contract,
  quote,
  onClose,
}: OptionContractInspectorProps) {
  if (!contract) return null;

  const isAdjusted = contract.adjustment_status === "ADJUSTED_CORPORATE_ACTION";
  const curr = contract.strike_currency || "USD";

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[480px] bg-zinc-950 border-l border-zinc-800 shadow-2xl z-50 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-cyan-400" />
          <h2 className="text-sm font-bold text-white tracking-wide">
            Contract Specification Inspector
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Symbology and Summary */}
        <div className="bg-zinc-900/80 border border-zinc-800 rounded-lg p-3">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-base font-bold text-white">
                  {contract.underlying_symbol}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded font-bold ${
                    contract.option_type === "CALL"
                      ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                      : "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                  }`}
                >
                  {contract.option_type}
                </span>
                <span className="font-mono text-sm text-zinc-300">
                  {formatCurrency(contract.strike_price, curr)}
                </span>
              </div>
              <div className="font-mono text-xs text-zinc-500 mt-1">
                Expiry: {contract.expiration_date}
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">
                {contract.market_id}
              </span>
            </div>
          </div>

          {contract.osi_symbol && (
            <div className="mt-3 pt-3 border-t border-zinc-800">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">
                OSI Symbol (21-Char Standard)
              </div>
              <div className="font-mono text-xs text-cyan-300 mt-0.5 bg-zinc-950 p-1.5 rounded border border-zinc-850 select-all">
                {contract.osi_symbol}
              </div>
            </div>
          )}
        </div>

        {/* Corporate Action Adjustment Warning */}
        {isAdjusted && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2 text-amber-300 text-xs font-semibold">
              <ShieldAlert className="w-4 h-4 shrink-0" />
              <span>Corporate Action Adjusted Contract</span>
            </div>
            <p className="text-[11px] text-amber-200/80 mt-1.5 leading-relaxed">
              {contract.adjustment_memo ||
                "This contract has nonstandard deliverables resulting from a corporate action (split, spin-off, or special dividend). It is excluded from standard vanilla payoff models."}
            </p>
          </div>
        )}

        {/* Contract Deliverables & Mechanics */}
        <div>
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-500" />
            Terms & Deliverables
          </h3>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
              <div className="text-zinc-500 text-[10px]">Multiplier / Lot Size</div>
              <div className="font-mono font-bold text-white mt-0.5">
                {contract.contract_multiplier} shares/units
              </div>
            </div>
            <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
              <div className="text-zinc-500 text-[10px]">Exercise Style</div>
              <div className="font-mono font-bold text-white mt-0.5">
                {contract.exercise_style}
              </div>
            </div>
            <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
              <div className="text-zinc-500 text-[10px]">Settlement Method</div>
              <div className="font-mono font-bold text-white mt-0.5">
                {contract.settlement_method}
              </div>
            </div>
            <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
              <div className="text-zinc-500 text-[10px]">Deliverable Type</div>
              <div className="font-mono font-bold text-white mt-0.5 text-[11px] truncate">
                {contract.deliverable.deliverable_type}
              </div>
            </div>
          </div>
          <div className="mt-2 p-2 bg-zinc-900/40 rounded border border-zinc-850 text-[11px] text-zinc-400">
            <span className="text-zinc-500 font-medium">Deliverable Summary: </span>
            {contract.deliverable.summary}
          </div>
        </div>

        {/* Live / Delayed Market Quote */}
        {quote && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-zinc-500" />
                Market Quote
              </h3>
              <div className="flex items-center gap-1.5">
                {quote.is_delayed ? (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    Delayed {quote.delay_minutes}m
                  </span>
                ) : (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    Real-Time
                  </span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Bid</div>
                <div className="font-mono font-bold text-emerald-400 mt-0.5">
                  {formatCurrency(quote.bid, curr)}
                </div>
                {quote.bid_size !== null && quote.bid_size !== undefined && (
                  <div className="text-[10px] text-zinc-500">Size: {quote.bid_size}</div>
                )}
              </div>
              <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Ask</div>
                <div className="font-mono font-bold text-rose-400 mt-0.5">
                  {formatCurrency(quote.ask, curr)}
                </div>
                {quote.ask_size !== null && quote.ask_size !== undefined && (
                  <div className="text-[10px] text-zinc-500">Size: {quote.ask_size}</div>
                )}
              </div>
              <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Last Price</div>
                <div className="font-mono font-bold text-white mt-0.5">
                  {formatCurrency(quote.last_price, curr)}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Volume</div>
                <div className="font-mono font-bold text-white">
                  {formatNumber(quote.volume)}
                </div>
              </div>
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Open Interest</div>
                <div className="font-mono font-bold text-white">
                  {formatNumber(quote.open_interest)}
                </div>
                {quote.open_interest_as_of && (
                  <div className="text-[9px] text-zinc-500">
                    As of: {quote.open_interest_as_of}
                  </div>
                )}
              </div>
            </div>

            {/* Quality Flags */}
            <div className="mt-2 flex flex-wrap gap-1.5">
              {quote.quality_flags.map((flag) => {
                const info = formatQualityFlag(flag);
                return (
                  <span
                    key={flag}
                    className={`text-[10px] px-2 py-0.5 rounded border border-zinc-800 ${info.className}`}
                  >
                    {info.label}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Source Greeks */}
        <div>
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-zinc-500" />
            Source Greeks & Volatility
          </h3>

          <div className="bg-zinc-900/50 p-2.5 rounded border border-zinc-800/80 mb-2">
            <div className="text-zinc-500 text-[10px]">Implied Volatility (IV)</div>
            <div className="font-mono text-base font-bold text-cyan-400">
              {quote?.implied_volatility !== null && quote?.implied_volatility !== undefined
                ? formatPercent(quote.implied_volatility)
                : "No source IV provided"}
            </div>
          </div>

          {quote?.greeks ? (
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Delta (Δ)</div>
                <div className="font-mono font-bold text-white">
                  {quote.greeks.delta !== null && quote.greeks.delta !== undefined
                    ? quote.greeks.delta.toFixed(4)
                    : "—"}
                </div>
              </div>
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Gamma (Γ)</div>
                <div className="font-mono font-bold text-white">
                  {quote.greeks.gamma !== null && quote.greeks.gamma !== undefined
                    ? quote.greeks.gamma.toFixed(4)
                    : "—"}
                </div>
              </div>
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Theta (Θ)</div>
                <div className="font-mono font-bold text-white">
                  {quote.greeks.theta !== null && quote.greeks.theta !== undefined
                    ? quote.greeks.theta.toFixed(4)
                    : "—"}
                </div>
              </div>
              <div className="bg-zinc-900/50 p-2 rounded border border-zinc-800/80">
                <div className="text-zinc-500 text-[10px]">Vega (ν)</div>
                <div className="font-mono font-bold text-white">
                  {quote.greeks.vega !== null && quote.greeks.vega !== undefined
                    ? quote.greeks.vega.toFixed(4)
                    : "—"}
                </div>
              </div>
            </div>
          ) : (
            <div className="p-3 bg-zinc-900/30 rounded border border-zinc-850 text-center text-xs text-zinc-500">
              No Greeks provided by upstream market data source. (Zero values are never fabricated).
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

