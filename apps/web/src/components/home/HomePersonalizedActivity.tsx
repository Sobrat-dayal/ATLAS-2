"use client";

import React, { useState } from "react";
import {
  History,
  ShieldCheck,
  RotateCcw,
  Trash2,
  PowerOff,
  Clock,
  Sparkles,
} from "lucide-react";
import { useHomeActivity } from "@/hooks/home/useHomeActivity";
import { HomeWidgetSurface } from "./HomeWidgetSurface";
import { HomeActivityRow } from "./HomeActivityRow";
import { HomeActivityClearDialog } from "./HomeActivityClearDialog";

export function HomePersonalizedActivity() {
  const {
    data,
    items,
    isLoading,
    isError,
    error,
    refetch,
    loadMore,
    isLoadingMore,
    enableHistory,
    disableHistory,
    clearHistory,
    isMutating,
  } = useHomeActivity();

  const [dialogState, setDialogState] = useState<{
    isOpen: boolean;
    mode: "clear" | "disable";
  }>({
    isOpen: false,
    mode: "clear",
  });

  const handleOpenClear = () => setDialogState({ isOpen: true, mode: "clear" });
  const handleOpenDisable = () => setDialogState({ isOpen: true, mode: "disable" });
  const handleCloseDialog = () => setDialogState((prev) => ({ ...prev, isOpen: false }));

  const handleConfirmDialog = async () => {
    if (dialogState.mode === "clear") {
      await clearHistory();
    } else {
      await disableHistory();
    }
    handleCloseDialog();
  };

  const isEnabled = Boolean(data?.enabled);

  return (
    <>
      <HomeWidgetSurface
        id="home-personalized-activity"
        title="Recent Activity"
        subtitle={isEnabled ? "Workspace Continuity" : "Disabled (Private)"}
        actions={
          isEnabled ? (
            <div className="flex items-center gap-1.5">
              {items.length > 0 && (
                <button
                  type="button"
                  onClick={handleOpenClear}
                  disabled={isMutating}
                  className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-error hover:bg-atlas-error/10 rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-error disabled:opacity-50"
                  aria-label="Clear recorded activity history"
                  title="Clear all recorded ATLAS activity history"
                >
                  <Trash2 className="h-3 w-3" aria-hidden="true" />
                  <span>Clear</span>
                </button>
              )}
              <button
                type="button"
                onClick={handleOpenDisable}
                disabled={isMutating}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent disabled:opacity-50"
                aria-label="Disable activity history recording"
                title="Disable activity history recording"
              >
                <PowerOff className="h-3 w-3" aria-hidden="true" />
                <span>Disable</span>
              </button>
            </div>
          ) : undefined
        }
      >
        {/* Loading State */}
        {isLoading && (
          <div className="flex flex-col gap-2" role="status" aria-label="Loading recent activity">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-11 rounded border border-atlas-border-subtle bg-atlas-surface-2/30 animate-pulse flex items-center px-3"
              />
            ))}
          </div>
        )}

        {/* Error State */}
        {!isLoading && isError && (
          <div
            className="flex flex-col items-center justify-center p-6 text-center border border-atlas-error/20 bg-atlas-error/5 rounded"
            role="alert"
          >
            <p className="text-xs font-medium text-atlas-error">
              {error?.message || "Failed to retrieve recent activity"}
            </p>
            <button
              type="button"
              onClick={() => refetch()}
              className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded bg-atlas-surface-2 hover:bg-atlas-surface-hover text-atlas-text-primary border border-atlas-border-default transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            >
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Disabled State */}
        {!isLoading && !isError && !isEnabled && (
          <div className="flex flex-col items-center justify-center p-6 text-center rounded border border-dashed border-atlas-border-default bg-atlas-surface-2/20">
            <div className="h-9 w-9 rounded-full bg-atlas-surface-3 border border-atlas-border-subtle flex items-center justify-center text-atlas-text-secondary mb-3">
              <ShieldCheck className="h-4.5 w-4.5 text-atlas-accent" aria-hidden="true" />
            </div>
            <h3 className="text-xs font-semibold text-atlas-text-primary">
              Activity History Disabled
            </h3>
            <p className="text-[11px] text-atlas-text-muted max-w-sm mt-1 leading-relaxed">
              Keep a private history of modules you open and entities you select, so you can resume your work quickly from Home.
            </p>
            <div className="flex items-center gap-1.5 mt-2 text-[10px] text-atlas-text-muted/80">
              <Sparkles className="h-3 w-3 text-atlas-accent/70" aria-hidden="true" />
              <span>Private to your account. No search or command text is recorded.</span>
            </div>
            <button
              type="button"
              onClick={() => enableHistory()}
              disabled={isMutating}
              className="mt-4 inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded bg-atlas-accent text-white hover:bg-atlas-accent-hover transition-colors shadow-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent disabled:opacity-50"
            >
              <History className="h-3.5 w-3.5" aria-hidden="true" />
              <span>{isMutating ? "Enabling..." : "Enable Activity History"}</span>
            </button>
          </div>
        )}

        {/* Enabled Empty State */}
        {!isLoading && !isError && isEnabled && items.length === 0 && (
          <div className="flex flex-col items-center justify-center p-6 text-center rounded border border-dashed border-atlas-border-default bg-atlas-surface-2/20">
            <div className="h-8 w-8 rounded-full bg-atlas-surface-3 flex items-center justify-center text-atlas-text-muted mb-2">
              <Clock className="h-4 w-4" aria-hidden="true" />
            </div>
            <p className="text-xs font-medium text-atlas-text-primary">
              No activity recorded yet
            </p>
            <p className="text-[11px] text-atlas-text-muted max-w-xs mt-1">
              Modules you navigate to and entities you explicitly select will appear here for workspace continuity.
            </p>
          </div>
        )}

        {/* Populated List State */}
        {!isLoading && !isError && isEnabled && items.length > 0 && (
          <div className="flex flex-col gap-2">
            <div className="flex flex-col gap-1.5" role="feed" aria-label="Recent user activities">
              {items.map((item) => (
                <HomeActivityRow key={item.activity_id} item={item} />
              ))}
            </div>

            {/* Pagination: Show More */}
            {data?.has_more && (
              <div className="pt-2 flex justify-center">
                <button
                  type="button"
                  onClick={() => loadMore()}
                  disabled={isLoadingMore}
                  className="px-3 py-1 rounded text-xs font-medium text-atlas-text-secondary hover:text-atlas-text-primary hover:bg-atlas-surface-hover border border-atlas-border-subtle hover:border-atlas-border-default transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent disabled:opacity-50"
                >
                  {isLoadingMore ? "Loading..." : "Show more"}
                </button>
              </div>
            )}
          </div>
        )}
      </HomeWidgetSurface>

      {/* Confirmation Dialog */}
      <HomeActivityClearDialog
        isOpen={dialogState.isOpen}
        mode={dialogState.mode}
        onClose={handleCloseDialog}
        onConfirm={handleConfirmDialog}
        isSubmitting={isMutating}
      />
    </>
  );
}
