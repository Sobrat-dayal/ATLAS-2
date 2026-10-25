"use client";

import React from "react";
import { Bell } from "lucide-react";

interface AlertBadgeProps {
  count: number;
  onClick?: (e: React.MouseEvent) => void;
}

export function AlertBadge({ count, onClick }: AlertBadgeProps) {
  if (count <= 0) return null;

  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-950/60 border border-sky-800 text-sky-400 hover:bg-sky-900/60 transition-colors"
      title={`${count} active alert${count > 1 ? "s" : ""} configured`}
      aria-label={`${count} active alerts`}
    >
      <Bell className="w-2.5 h-2.5" />
      <span>{count}</span>
    </button>
  );
}
