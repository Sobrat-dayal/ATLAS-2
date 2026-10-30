"use client";

import React from "react";
import { AlertTriangle, CheckCircle2, RefreshCw, Unlink } from "lucide-react";
import { LinkingStatus } from "@/lib/context/types";

interface ContextCompatibilityStatusProps {
  status: LinkingStatus;
  className?: string;
}

export function ContextCompatibilityStatus({
  status,
  className = "",
}: ContextCompatibilityStatusProps) {
  if (status === "LINKED" || status === "UPDATED") {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[9px] text-emerald-400 font-mono ${className}`}
        title="Widget is synchronized and up-to-date with active channel"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        <span className="hidden md:inline">SYNCED</span>
      </span>
    );
  }

  if (status === "UPDATING") {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[9px] text-blue-400 font-mono ${className}`}
        title="Synchronizing financial context..."
      >
        <RefreshCw className="w-2.5 h-2.5 animate-spin" />
        <span className="hidden md:inline">SYNCING</span>
      </span>
    );
  }

  if (status === "INDEPENDENT") {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[9px] text-atlas-text-muted font-mono ${className}`}
        title="Widget operates in independent local state"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-slate-500" />
        <span className="hidden md:inline">LOCAL</span>
      </span>
    );
  }

  if (status === "INCOMPATIBLE_CONTEXT" || status === "TARGET_UNAVAILABLE") {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[9px] text-amber-400 font-mono ${className}`}
        title="Active channel entity is not compatible with this widget"
      >
        <AlertTriangle className="w-2.5 h-2.5" />
        <span className="hidden md:inline">INCOMPATIBLE</span>
      </span>
    );
  }

  return null;
}
