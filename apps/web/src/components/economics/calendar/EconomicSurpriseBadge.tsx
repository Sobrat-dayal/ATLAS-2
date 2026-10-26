"use client";

import React from "react";
import { EconomicSurpriseMetricDTO } from "@/lib/economics/calendar";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface EconomicSurpriseBadgeProps {
  surprise?: EconomicSurpriseMetricDTO | null;
  compact?: boolean;
}

export function EconomicSurpriseBadge({ surprise, compact = false }: EconomicSurpriseBadgeProps) {
  if (!surprise) {
    return <span className="text-atlas-text-muted text-xs font-mono">—</span>;
  }

  const { direction, surprise_value, percentage_point_diff, basis_point_diff, unit } = surprise;

  let colorClasses = "text-atlas-text-muted bg-atlas-surface border-atlas-border-subtle";
  let icon = <Minus className="w-3 h-3" />;
  let label = "In Line";

  if (direction === "ABOVE_CONSENSUS") {
    colorClasses = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
    icon = <ArrowUpRight className="w-3 h-3" />;
    label = "Above";
  } else if (direction === "BELOW_CONSENSUS") {
    colorClasses = "text-rose-400 bg-rose-500/10 border-rose-500/20";
    icon = <ArrowDownRight className="w-3 h-3" />;
    label = "Below";
  }

  // Format value display based on metric type
  let formattedValue = "";
  if (percentage_point_diff !== null && percentage_point_diff !== undefined) {
    const sign = percentage_point_diff > 0 ? "+" : "";
    formattedValue = `${sign}${percentage_point_diff.toFixed(2)} pp`;
  } else if (basis_point_diff !== null && basis_point_diff !== undefined) {
    const sign = basis_point_diff > 0 ? "+" : "";
    formattedValue = `${sign}${basis_point_diff.toFixed(0)} bps`;
  } else {
    const sign = surprise_value > 0 ? "+" : "";
    formattedValue = `${sign}${surprise_value.toLocaleString()} ${unit}`;
  }

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono border ${colorClasses}`}
        title={`Economic Surprise: ${label} Consensus by ${formattedValue}`}
      >
        {icon}
        <span>{formattedValue}</span>
      </span>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono border ${colorClasses}`}
      title={`Surprise: ${label} Consensus (${formattedValue})`}
    >
      {icon}
      <span className="font-semibold">{formattedValue}</span>
      <span className="text-[10px] uppercase tracking-wider opacity-75">({label})</span>
    </div>
  );
}
