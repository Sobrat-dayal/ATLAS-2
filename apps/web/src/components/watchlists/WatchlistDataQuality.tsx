import React from "react";
import { LiveDataQuality } from "@/lib/watchlists/live";

interface WatchlistDataQualityProps {
  dataQuality: LiveDataQuality;
  activeCount: number;
  totalCount: number;
}

export function WatchlistDataQuality({
  dataQuality,
  activeCount,
  totalCount,
}: WatchlistDataQualityProps) {
  let badgeStyle = "text-zinc-500 border-zinc-800 bg-zinc-900";
  let label = "Unavailable";

  switch (dataQuality) {
    case "realtime":
      badgeStyle = "text-emerald-400 border-emerald-500/30 bg-emerald-950/40";
      label = "Realtime";
      break;
    case "delayed":
      badgeStyle = "text-amber-400 border-amber-500/30 bg-amber-950/40";
      label = "Delayed (15m)";
      break;
    case "mixed":
      badgeStyle = "text-sky-400 border-sky-500/30 bg-sky-950/40";
      label = "Mixed Quality";
      break;
    case "stale":
      badgeStyle = "text-zinc-400 border-zinc-700 bg-zinc-900";
      label = "Stale";
      break;
    case "unavailable":
    default:
      badgeStyle = "text-zinc-500 border-zinc-800 bg-zinc-900";
      label = "Snapshot Only";
      break;
  }

  return (
    <div
      className="inline-flex items-center gap-1.5 px-2 py-1 rounded border text-[11px] select-none"
      title={`Market Data Quality: ${label} (${activeCount} of ${totalCount} series streamed)`}
      role="status"
    >
      <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wider ${badgeStyle}`}>
        {label}
      </span>
      <span className="font-mono text-[10px] text-zinc-400">
        Live: {activeCount}/{totalCount}
      </span>
    </div>
  );
}
