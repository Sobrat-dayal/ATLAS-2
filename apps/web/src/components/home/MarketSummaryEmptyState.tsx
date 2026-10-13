"use client";

import { AlertCircle, LineChart } from "lucide-react";

interface MarketSummaryEmptyStateProps {
  title?: string;
  description?: string;
  isError?: boolean;
  onRetry?: () => void;
}

export function MarketSummaryEmptyState({
  title = "No Market Observations Available",
  description = "No market instruments are currently available for this overview. Data feeds may be initializing or awaiting upstream updates.",
  isError = false,
  onRetry,
}: MarketSummaryEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 rounded-lg border border-dashed border-zinc-800 bg-zinc-900/30 text-center">
      <div className="p-2.5 rounded-full bg-zinc-800/80 mb-3 text-zinc-400">
        {isError ? (
          <AlertCircle className="h-5 w-5 text-rose-400" aria-hidden="true" />
        ) : (
          <LineChart className="h-5 w-5 text-zinc-400" aria-hidden="true" />
        )}
      </div>

      <h4 className="text-sm font-semibold text-zinc-200 mb-1">{title}</h4>
      <p className="text-xs text-zinc-400 max-w-sm mb-4 leading-relaxed">
        {description}
      </p>

      <div className="flex items-center gap-3">
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="px-3 py-1.5 text-xs font-medium text-zinc-200 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
          >
            Retry Connection
          </button>
        )}
        <a
          href="/markets"
          className="px-3 py-1.5 text-xs font-medium text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          Open Markets Workspace →
        </a>
      </div>
    </div>
  );
}
