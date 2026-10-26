"use client";

import React from "react";
import { Newspaper, AlertTriangle, RefreshCw, X } from "lucide-react";

interface NewsEmptyStateProps {
  isError?: boolean;
  errorMessage?: string | null;
  hasFilters?: boolean;
  onClearFilters?: () => void;
  onRetry?: () => void;
}

export function NewsEmptyState({
  isError,
  errorMessage,
  hasFilters,
  onClearFilters,
  onRetry,
}: NewsEmptyStateProps) {
  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 my-4 shadow-sm">
        <div className="w-10 h-10 rounded-full bg-amber-500/10 flex items-center justify-center text-amber-600 dark:text-amber-400 mb-3">
          <AlertTriangle className="w-5 h-5" />
        </div>
        <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 font-mono mb-1">
          NEWS SERVICE UNAVAILABLE
        </h3>
        <p className="text-xs text-zinc-500 max-w-sm mb-4">
          {errorMessage || "Unable to retrieve verified news feed from authorized providers."}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 transition-colors shadow-sm"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry Feed Request</span>
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 my-4 shadow-sm">
      <div className="w-10 h-10 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center text-zinc-400 mb-3">
        <Newspaper className="w-5 h-5 stroke-[1.5]" />
      </div>
      <h3 className="text-sm font-bold text-zinc-900 dark:text-zinc-100 font-mono mb-1">
        NO MATCHING NEWS HEADLINES
      </h3>
      <p className="text-xs text-zinc-500 max-w-sm mb-4">
        {hasFilters
          ? "No source-verified articles match your active filter criteria."
          : "No news articles are currently available in this feed category."}
      </p>
      {hasFilters && onClearFilters && (
        <button
          onClick={onClearFilters}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium border border-zinc-200 dark:border-zinc-700 bg-white dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors shadow-sm"
        >
          <X className="w-3.5 h-3.5" />
          <span>Clear All Filters</span>
        </button>
      )}
    </div>
  );
}
