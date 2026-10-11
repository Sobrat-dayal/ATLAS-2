"use client";

import React, { useEffect, useRef } from "react";
import { CheckCheck, Loader2, RefreshCw, X } from "lucide-react";
import { useNotifications } from "@/lib/notifications/useNotifications";
import { NotificationRow } from "./NotificationRow";

export function NotificationCenter() {
  const {
    isOpen,
    setIsOpen,
    filter,
    setFilter,
    items,
    unreadCount,
    isLoading,
    isLoadingMore,
    hasMore,
    error,
    loadMore,
    refreshList,
    markAllRead,
  } = useNotifications();

  const containerRef = useRef<HTMLDivElement>(null);

  // Close on Escape or click outside
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setIsOpen(false);
      }
    };

    const handleClickOutside = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node) &&
        !(e.target as HTMLElement).closest("#atlas-notification-trigger")
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen, setIsOpen]);

  if (!isOpen) {
    return null;
  }

  const filteredItems =
    filter === "unread"
      ? items.filter((i) => !i.read_at && !i.archived_at)
      : items;

  return (
    <div
      ref={containerRef}
      role="dialog"
      aria-label="Notifications"
      aria-modal="true"
      className="absolute right-0 top-11 z-50 flex w-[380px] max-w-[calc(100vw-24px)] flex-col rounded-b-md border border-atlas-border-default bg-atlas-surface-0 shadow-2xl transition-all max-h-[580px]"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-atlas-border-default px-3 py-2 bg-atlas-surface-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-atlas-text-primary">
            Notifications
          </span>
          {unreadCount > 0 && (
            <span className="rounded-full bg-atlas-accent/15 px-1.5 py-0.2 text-[10px] font-semibold text-atlas-accent">
              {unreadCount} unread
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          {unreadCount > 0 && (
            <button
              type="button"
              onClick={() => markAllRead()}
              className="flex items-center gap-1 rounded px-2 py-1 text-[11px] font-medium text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
              title="Mark all as read"
            >
              <CheckCheck className="h-3.5 w-3.5" />
              <span>Mark all read</span>
            </button>
          )}

          <button
            type="button"
            onClick={() => setIsOpen(false)}
            aria-label="Close notification center"
            className="rounded p-1 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Tabs / Segmented Filter */}
      <div className="flex border-b border-atlas-border-default bg-atlas-surface-1/50 px-3 py-1">
        <div className="flex gap-2">
          <button
            type="button"
            role="tab"
            aria-selected={filter === "all"}
            onClick={() => setFilter("all")}
            className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
              filter === "all"
                ? "bg-atlas-surface-selected text-atlas-accent"
                : "text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            All
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={filter === "unread"}
            onClick={() => setFilter("unread")}
            className={`rounded px-2.5 py-1 text-xs font-medium transition-colors ${
              filter === "unread"
                ? "bg-atlas-surface-selected text-atlas-accent"
                : "text-atlas-text-muted hover:text-atlas-text-primary"
            }`}
          >
            Unread
            {unreadCount > 0 && ` (${unreadCount})`}
          </button>
        </div>
      </div>

      {/* Body List */}
      <div className="flex-1 overflow-y-auto min-h-[160px] max-h-[460px]">
        {isLoading && items.length === 0 ? (
          <div className="flex h-40 flex-col items-center justify-center gap-2 text-atlas-text-secondary">
            <Loader2 className="h-5 w-5 animate-spin text-atlas-accent" />
            <span className="text-xs">Loading notifications...</span>
          </div>
        ) : error && items.length === 0 ? (
          <div className="flex h-40 flex-col items-center justify-center gap-2 px-4 text-center">
            <span className="text-xs text-atlas-negative">{error}</span>
            <button
              type="button"
              onClick={() => refreshList()}
              className="flex items-center gap-1 rounded bg-atlas-surface-2 px-2.5 py-1 text-xs font-medium text-atlas-text-primary hover:bg-atlas-surface-hover"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Retry</span>
            </button>
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="flex h-40 flex-col items-center justify-center gap-1 text-atlas-text-muted">
            <span className="text-xs font-medium">
              {filter === "unread" ? "No unread notifications" : "No notifications"}
            </span>
          </div>
        ) : (
          <div className="divide-y divide-atlas-border-default/40">
            {filteredItems.map((item) => (
              <NotificationRow key={item.notification_id} item={item} />
            ))}

            {hasMore && (
              <div className="p-2 text-center bg-atlas-surface-1/30">
                <button
                  type="button"
                  onClick={() => loadMore()}
                  disabled={isLoadingMore}
                  className="w-full rounded py-1.5 text-xs font-medium text-atlas-accent hover:bg-atlas-surface-hover disabled:opacity-50 transition-colors"
                >
                  {isLoadingMore ? "Loading more..." : "Load more"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
