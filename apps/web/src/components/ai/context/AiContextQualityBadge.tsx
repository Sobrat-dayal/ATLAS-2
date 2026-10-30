"use client";

import React from "react";
import { DataQualityStatus } from "@/lib/ai/context/types";

interface AiContextQualityBadgeProps {
  status: DataQualityStatus | string;
  className?: string;
}

export function AiContextQualityBadge({ status, className = "" }: AiContextQualityBadgeProps) {
  const norm = (status || "").toUpperCase();

  let colorClasses = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
  let label = "Complete";

  if (norm === "PARTIAL") {
    colorClasses = "bg-amber-500/10 text-amber-400 border-amber-500/30";
    label = "Partial";
  } else if (norm === "STALE") {
    colorClasses = "bg-orange-500/10 text-orange-400 border-orange-500/30";
    label = "Stale";
  } else if (norm === "RESTRICTED") {
    colorClasses = "bg-rose-500/10 text-rose-400 border-rose-500/30";
    label = "Restricted";
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wider ${colorClasses} ${className}`}
      title={`Data Quality: ${label}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  );
}

