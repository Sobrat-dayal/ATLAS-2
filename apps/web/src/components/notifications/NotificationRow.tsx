"use client";

import React from "react";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  Archive,
  ArrowRight,
  Check,
  CheckCircle2,
  Info,
  RotateCcw,
  TriangleAlert,
} from "lucide-react";
import { useSelectedEntity } from "@/hooks/entity";
import { formatRelativeTime, isAllowedInternalRoute } from "@/lib/notifications/constants";
import { NotificationItem } from "@/lib/notifications/types";
import { useNotifications } from "@/lib/notifications/useNotifications";

export interface NotificationRowProps {
  item: NotificationItem;
  onNavigate?: () => void;
}

export function NotificationRow({ item, onNavigate }: NotificationRowProps) {
  const router = useRouter();
  const { selectEntity } = useSelectedEntity();
  const { markRead, markUnread, archive, setIsOpen } = useNotifications();

  const isUnread = !item.read_at && !item.archived_at;

  const handleRowClick = () => {
    // 1. Mark read on click
    if (isUnread) {
      markRead(item.notification_id);
    }

    // 2. Navigation action evaluation
    if (item.action_kind === "none" || !item.action_route) {
      return;
    }

    // Defense in depth: validate route allowlist
    if (!isAllowedInternalRoute(item.action_route)) {
      console.warn("Blocked navigation to disallowed route:", item.action_route);
      return;
    }

    // ENTITY_ROUTE: select entity then navigate
    if (item.action_kind === "entity_route" && item.action_entity_id) {
      selectEntity(item.action_entity_id);
    }

    setIsOpen(false);
    if (onNavigate) onNavigate();
    router.push(item.action_route);
  };

  const getSeverityIcon = () => {
    switch (item.severity) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-atlas-positive shrink-0" />;
      case "warning":
        return <TriangleAlert className="h-4 w-4 text-atlas-warning shrink-0" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-atlas-negative shrink-0" />;
      case "info":
      default:
        return <Info className="h-4 w-4 text-atlas-accent shrink-0" />;
    }
  };

  return (
    <div
      role="article"
      aria-label={`${item.title}. ${isUnread ? "Unread" : "Read"}`}
      className={`group relative flex flex-col gap-1.5 p-3 border-b border-atlas-border-default transition-colors ${
        isUnread
          ? "bg-atlas-surface-1/60 hover:bg-atlas-surface-hover/80"
          : "bg-atlas-surface-0 hover:bg-atlas-surface-hover/50 text-atlas-text-secondary"
      }`}
    >
      {/* Top Header: Severity, Category, Timestamp, Actions */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          {getSeverityIcon()}
          <span className="text-[11px] font-semibold uppercase tracking-wider text-atlas-text-muted">
            {item.category}
          </span>
          {isUnread && (
            <span
              className="inline-block h-1.5 w-1.5 rounded-full bg-atlas-accent"
              aria-label="Unread"
              title="Unread notification"
            />
          )}
        </div>

        <div className="flex items-center gap-1">
          <span className="text-[11px] text-atlas-text-muted">
            {formatRelativeTime(item.created_at)}
          </span>

          {/* Row actions */}
          <div className="flex items-center gap-0.5 opacity-80 group-hover:opacity-100 transition-opacity">
            {isUnread ? (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  markRead(item.notification_id);
                }}
                title="Mark as read"
                aria-label="Mark as read"
                className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-selected hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
              >
                <Check className="h-3.5 w-3.5" />
              </button>
            ) : (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  markUnread(item.notification_id);
                }}
                title="Mark as unread"
                aria-label="Mark as unread"
                className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-selected hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
              >
                <RotateCcw className="h-3 w-3" />
              </button>
            )}

            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                archive(item.notification_id);
              }}
              title="Archive notification"
              aria-label="Archive notification"
              className="rounded p-1 text-atlas-text-muted hover:bg-atlas-surface-selected hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
            >
              <Archive className="h-3 w-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Clickable Content Body */}
      <button
        type="button"
        onClick={handleRowClick}
        className="text-left w-full focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent rounded-sm"
      >
        <div
          className={`text-xs font-medium leading-snug line-clamp-2 ${
            isUnread ? "text-atlas-text-primary font-semibold" : "text-atlas-text-secondary"
          }`}
        >
          {item.title}
        </div>

        <div className="mt-1 text-xs text-atlas-text-secondary leading-relaxed line-clamp-3 break-words">
          {item.message}
        </div>

        {/* Action Affordance */}
        {item.action_kind !== "none" && item.action_route && (
          <div className="mt-2 flex items-center gap-1 text-[11px] font-medium text-atlas-accent group-hover:underline">
            <span>
              {item.action_kind === "entity_route"
                ? `View in ${item.action_route.slice(1)}`
                : `Go to ${item.action_route.slice(1)}`}
            </span>
            <ArrowRight className="h-3 w-3" />
          </div>
        )}
      </button>
    </div>
  );
}
