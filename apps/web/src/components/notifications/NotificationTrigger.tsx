"use client";

import React from "react";
import { Bell } from "lucide-react";
import { useNotifications } from "@/lib/notifications/useNotifications";

export function NotificationTrigger() {
  const { unreadCount, isOpen, setIsOpen } = useNotifications();

  const badgeText = unreadCount > 99 ? "99+" : unreadCount > 0 ? String(unreadCount) : null;
  const accessibleLabel =
    unreadCount > 0 ? `Notifications, ${unreadCount} unread` : "Notifications";

  return (
    <button
      type="button"
      id="atlas-notification-trigger"
      aria-label={accessibleLabel}
      aria-expanded={isOpen}
      aria-haspopup="dialog"
      onClick={() => setIsOpen(!isOpen)}
      className="relative rounded-sm p-1.5 text-atlas-text-secondary hover:bg-atlas-surface-hover hover:text-atlas-text-primary transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-accent"
    >
      <Bell className="h-4 w-4" />
      {badgeText && (
        <span
          className="absolute -top-1 -right-1 flex min-w-[18px] h-[18px] items-center justify-center rounded-full bg-atlas-accent px-1 text-[10px] font-bold leading-none text-white shadow-sm"
          aria-hidden="true"
        >
          {badgeText}
        </span>
      )}
    </button>
  );
}
