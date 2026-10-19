import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

interface WatchlistErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function WatchlistErrorState({ message, onRetry }: WatchlistErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center border border-red-900/40 rounded-lg bg-red-950/10">
      <div className="w-10 h-10 rounded-full bg-red-900/30 flex items-center justify-center text-red-400 mb-3 border border-red-800/40">
        <AlertCircle className="w-5 h-5 text-red-400" />
      </div>
      <h3 className="text-xs font-semibold text-red-200 uppercase tracking-wider mb-1">
        Failed to Load Watchlist
      </h3>
      <p className="text-xs text-zinc-400 max-w-sm mb-5 leading-relaxed">
        {message || "An unexpected error occurred while communicating with the Watchlists service."}
      </p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded bg-zinc-800 text-zinc-200 hover:bg-zinc-700 border border-zinc-700 transition-colors focus:outline-none focus:ring-1 focus:ring-zinc-400"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Retry Connection
        </button>
      )}
    </div>
  );
}
