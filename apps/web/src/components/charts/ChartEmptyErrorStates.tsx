"use client";

/**
 * Loading, Empty, and Error States for ATLAS Charts V1 (Stage 66).
 */

import React from "react";
import { AlertCircle, CandlestickChart, RefreshCw } from "lucide-react";

export function ChartLoadingSkeleton() {
  return (
    <div className="w-full h-[520px] bg-zinc-950 border border-zinc-800/80 rounded flex flex-col justify-between p-6 animate-pulse">
      {/* Top shimmer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-24 h-6 bg-zinc-900 rounded" />
          <div className="w-40 h-6 bg-zinc-900 rounded" />
        </div>
        <div className="w-32 h-6 bg-zinc-900 rounded" />
      </div>

      {/* Center simulated chart candles */}
      <div className="flex items-end justify-between gap-2 h-64 px-8 opacity-40">
        {[40, 65, 30, 80, 55, 90, 70, 45, 85, 60, 75, 50, 95, 60, 80].map((h, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-0.5 bg-zinc-700 h-6" />
            <div
              className={`w-full rounded-sm ${i % 2 === 0 ? "bg-emerald-900/50" : "bg-red-900/50"}`}
              style={{ height: `${h}%` }}
            />
            <div className="w-0.5 bg-zinc-700 h-6" />
          </div>
        ))}
      </div>

      {/* Bottom shimmer */}
      <div className="flex items-center justify-between border-t border-zinc-900 pt-3">
        <div className="w-48 h-4 bg-zinc-900 rounded" />
        <div className="w-32 h-4 bg-zinc-900 rounded" />
      </div>
    </div>
  );
}

export interface ChartEmptyStateProps {
  onSelectDefault?: () => void;
}

export function ChartEmptyState({ onSelectDefault }: ChartEmptyStateProps) {
  return (
    <div className="w-full h-[520px] bg-zinc-950 border border-zinc-800/80 rounded flex flex-col items-center justify-center p-8 text-center">
      <div className="w-12 h-12 rounded-full bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-4">
        <CandlestickChart className="w-6 h-6 text-zinc-400" />
      </div>
      <h3 className="text-base font-semibold text-zinc-100 mb-1">
        No Historical Data Available
      </h3>
      <p className="text-xs text-zinc-400 max-w-md mb-6 leading-relaxed">
        No verified historical OHLCV bars are currently stored for the selected instrument.
        Select an active canonical instrument from the catalog.
      </p>
      {onSelectDefault && (
        <button
          type="button"
          onClick={onSelectDefault}
          className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-mono text-xs font-medium transition-colors"
        >
          Load S&amp;P 500 (SPY)
        </button>
      )}
    </div>
  );
}

export interface ChartErrorStateProps {
  error: string;
  onRetry: () => void;
}

export function ChartErrorState({ error, onRetry }: ChartErrorStateProps) {
  return (
    <div className="w-full h-[520px] bg-zinc-950 border border-red-900/40 rounded flex flex-col items-center justify-center p-8 text-center">
      <div className="w-12 h-12 rounded-full bg-red-950/50 border border-red-800/60 flex items-center justify-center mb-4">
        <AlertCircle className="w-6 h-6 text-red-400" />
      </div>
      <h3 className="text-base font-semibold text-zinc-100 mb-1">
        Chart History Retrieval Error
      </h3>
      <p className="text-xs text-red-300 font-mono max-w-lg mb-6 leading-relaxed bg-red-950/20 p-2.5 rounded border border-red-900/30">
        {error}
      </p>
      <button
        type="button"
        onClick={onRetry}
        className="flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-100 rounded font-mono text-xs font-medium transition-colors"
      >
        <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
        <span>Retry Historical Request</span>
      </button>
    </div>
  );
}
