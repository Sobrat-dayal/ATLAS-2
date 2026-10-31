"use client";

import React from "react";
import { formatPercent, formatStrike } from "@/lib/options/formatters";
import { LineChart, TrendingUp, Info } from "lucide-react";

interface VolatilitySmileData {
  underlying_symbol: string;
  expiration_date: string;
  smile_points: Array<{ strike_price: number; implied_volatility: number; option_type: string }>;
  skew_metrics?: {
    put_skew_25d?: number;
    call_skew_25d?: number;
    risk_reversal_25d?: number;
  };
}

interface TermStructureData {
  underlying_symbol: string;
  points: Array<{ expiration_date: string; days_to_expiration: number; atm_iv: number }>;
}

interface OptionsVolatilityViewProps {
  smile: VolatilitySmileData | null;
  termStructure: TermStructureData | null;
  currency?: string;
  isLoading?: boolean;
}

export function OptionsVolatilityView({
  smile,
  termStructure,
  currency = "USD",
  isLoading,
}: OptionsVolatilityViewProps) {
  if (isLoading) {
    return (
      <div className="p-12 text-center text-zinc-500 text-xs">
        Loading implied volatility and skew analytics...
      </div>
    );
  }

  const smilePoints = smile?.smile_points || [];
  const termPoints = termStructure?.points || [];

  return (
    <div className="p-4 space-y-6 bg-zinc-950 overflow-y-auto h-full">
      {/* 25-Delta Skew Indicators */}
      {smile?.skew_metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-zinc-900/60 border border-zinc-850 rounded-lg p-3">
            <div className="text-zinc-500 text-xs">25-Delta Put Skew (OOTM Put IV - ATM)</div>
            <div className="font-mono text-lg font-bold text-rose-400 mt-1">
              {smile.skew_metrics.put_skew_25d !== undefined
                ? `${(smile.skew_metrics.put_skew_25d * 100).toFixed(2)}%`
                : "—"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Downside Tail Premium</div>
          </div>

          <div className="bg-zinc-900/60 border border-zinc-850 rounded-lg p-3">
            <div className="text-zinc-500 text-xs">25-Delta Call Skew (OOTM Call IV - ATM)</div>
            <div className="font-mono text-lg font-bold text-emerald-400 mt-1">
              {smile.skew_metrics.call_skew_25d !== undefined
                ? `${(smile.skew_metrics.call_skew_25d * 100).toFixed(2)}%`
                : "—"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Upside Tail Premium</div>
          </div>

          <div className="bg-zinc-900/60 border border-zinc-850 rounded-lg p-3">
            <div className="text-zinc-500 text-xs">Risk Reversal (25D Call IV - 25D Put IV)</div>
            <div
              className={`font-mono text-lg font-bold mt-1 ${
                (smile.skew_metrics.risk_reversal_25d || 0) >= 0
                  ? "text-emerald-400"
                  : "text-rose-400"
              }`}
            >
              {smile.skew_metrics.risk_reversal_25d !== undefined
                ? `${(smile.skew_metrics.risk_reversal_25d * 100).toFixed(2)}%`
                : "—"}
            </div>
            <div className="text-[10px] text-zinc-500 mt-0.5">Directional Sentiment Skew</div>
          </div>
        </div>
      )}

      {/* Volatility Smile Chart */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <LineChart className="w-4 h-4 text-cyan-400" />
              Implied Volatility Smile ({smile?.expiration_date})
            </h3>
            <p className="text-xs text-zinc-500 mt-0.5">
              Source-provided implied volatility plotted across strike prices
            </p>
          </div>
        </div>

        {smilePoints.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-xs text-zinc-500">
            No source implied volatility data for this expiration.
          </div>
        ) : (
          <div className="h-64 flex flex-col justify-end pt-4 pb-2">
            <div className="flex items-end justify-between h-48 gap-2 border-b border-zinc-800 px-4">
              {smilePoints.map((pt, i) => {
                const maxIv = Math.max(...smilePoints.map((p) => p.implied_volatility), 0.5);
                const heightPct = Math.min(100, (pt.implied_volatility / maxIv) * 100);

                return (
                  <div key={i} className="flex-1 flex flex-col items-center group relative">
                    {/* Tooltip */}
                    <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-zinc-950 border border-zinc-700 px-2 py-1 rounded text-[10px] font-mono text-white pointer-events-none z-10 whitespace-nowrap">
                      {formatStrike(pt.strike_price, currency)}: {formatPercent(pt.implied_volatility)}
                    </div>
                    {/* Bar */}
                    <div
                      style={{ height: `${heightPct}%` }}
                      className="w-full max-w-[24px] bg-gradient-to-t from-cyan-600/40 to-cyan-400 rounded-t transition-all group-hover:brightness-125"
                    />
                    {/* Strike label */}
                    <div className="text-[9px] font-mono text-zinc-500 mt-2 truncate w-full text-center">
                      {pt.strike_price}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between text-[10px] text-zinc-500 px-4 mt-2">
              <span>Lower Strikes (Puts)</span>
              <span>ATM Strike</span>
              <span>Higher Strikes (Calls)</span>
            </div>
          </div>
        )}
      </div>

      {/* Volatility Term Structure */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-4">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          Volatility Term Structure (ATM IV vs Expiration)
        </h3>

        {termPoints.length === 0 ? (
          <div className="h-32 flex items-center justify-center text-xs text-zinc-500">
            No term structure data points.
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {termPoints.map((tp) => (
              <div
                key={tp.expiration_date}
                className="bg-zinc-950 border border-zinc-850 p-3 rounded-lg"
              >
                <div className="text-zinc-500 text-[10px] font-mono">{tp.expiration_date}</div>
                <div className="font-mono text-sm font-bold text-cyan-300 mt-1">
                  {formatPercent(tp.atm_iv)}
                </div>
                <div className="text-[10px] text-zinc-500 mt-0.5">{tp.days_to_expiration} DTE</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

