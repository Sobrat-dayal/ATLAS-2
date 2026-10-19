import React from "react";
import { DeliveryDelayStatus, FreshnessStatus } from "@/lib/watchlists/types";

interface WatchlistStatusBadgeProps {
  freshnessStatus: FreshnessStatus;
  deliveryDelayStatus: DeliveryDelayStatus;
  delaySeconds?: number | null;
}

export function WatchlistStatusBadge({
  freshnessStatus,
  deliveryDelayStatus,
  delaySeconds,
}: WatchlistStatusBadgeProps) {
  let label = "Unavailable";
  let badgeStyle = "bg-zinc-800 text-zinc-400 border-zinc-700";

  if (freshnessStatus === "fresh") {
    if (deliveryDelayStatus === "delayed") {
      const delayMins = delaySeconds ? Math.round(delaySeconds / 60) : 15;
      label = `Delayed (${delayMins}m)`;
      badgeStyle = "bg-amber-950/60 text-amber-300 border-amber-800/80";
    } else {
      label = "Fresh";
      badgeStyle = "bg-emerald-950/60 text-emerald-300 border-emerald-800/80";
    }
  } else if (freshnessStatus === "aging") {
    label = "Aging";
    badgeStyle = "bg-amber-950/40 text-amber-400 border-amber-800/60";
  } else if (freshnessStatus === "stale") {
    label = "Stale";
    badgeStyle = "bg-orange-950/50 text-orange-400 border-orange-800/70";
  } else {
    label = "Unavailable";
    badgeStyle = "bg-zinc-800/70 text-zinc-400 border-zinc-700";
  }

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono font-medium border tracking-wider uppercase ${badgeStyle}`}
      title={`Freshness: ${freshnessStatus}, Latency: ${deliveryDelayStatus}`}
    >
      {label}
    </span>
  );
}
