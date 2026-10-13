"use client";

import React from "react";
import { AlertCircle, Inbox, RefreshCw } from "lucide-react";

export interface MarketsEmptyStateProps {
  title: string;
  description: string;
  isError?: boolean;
  onRetry?: () => void;
}

export function MarketsEmptyState({
  title,
  description,
  isError = false,
  onRetry,
}: MarketsEmptyStateProps) {
  return (
    <div
      role={isError ? "alert" : "region"}
      aria-label={title}
      className="flex flex-col items-center justify-center p-8 rounded-lg border border-[var(--atlas-border-subtle)] bg-[var(--atlas-surface-card)] text-center my-4"
    >
      <div
        className={`p-2.5 rounded-full mb-3 ${
          isError
            ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
            : "bg-zinc-800/60 text-zinc-400 border border-zinc-700/40"
        }`}
      >
        {isError ? (
          <AlertCircle className="h-5 w-5" aria-hidden="true" />
        ) : (
          <Inbox className="h-5 w-5" aria-hidden="true" />
        )}
      </div>

      <h3 className="text-sm font-semibold text-[var(--atlas-text-primary)] mb-1">
        {title}
      </h3>
      <p className="text-xs text-[var(--atlas-text-secondary)] max-w-md mb-4">
        {description}
      </p>

      {isError && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded transition-colors focus:outline-none focus:ring-1 focus:ring-emerald-500/50"
        >
          <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
          <span>Retry Connection</span>
        </button>
      )}
    </div>
  );
}
