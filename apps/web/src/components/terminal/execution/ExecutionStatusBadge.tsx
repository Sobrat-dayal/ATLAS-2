/**
 * Professional execution status indicator badge with institutional color mapping.
 */

import React from "react";
import type { ExecutionStatus } from "@/lib/terminal/executionTypes";
import { CheckCircle2, AlertTriangle, XCircle, Clock, Loader2, Ban } from "lucide-react";

interface ExecutionStatusBadgeProps {
  status: ExecutionStatus;
  durationMs?: number | null;
  className?: string;
}

export const ExecutionStatusBadge: React.FC<ExecutionStatusBadgeProps> = ({
  status,
  durationMs,
  className = "",
}) => {
  let colorClass = "bg-neutral-800 text-neutral-300 border-neutral-700";
  let Icon = Clock;
  let label: string = status;

  switch (status) {
    case "COMPLETED":
      colorClass = "bg-emerald-950/60 text-emerald-300 border-emerald-800/80";
      Icon = CheckCircle2;
      label = "Completed";
      break;
    case "RUNNING":
    case "STREAMING":
    case "STARTING":
    case "PREPARING":
      colorClass = "bg-blue-950/60 text-blue-300 border-blue-800/80";
      Icon = Loader2;
      label = status === "STREAMING" ? "Streaming" : "Running";
      break;
    case "QUEUED":
      colorClass = "bg-amber-950/60 text-amber-300 border-amber-800/80";
      Icon = Clock;
      label = "Queued";
      break;
    case "FAILED":
      colorClass = "bg-rose-950/60 text-rose-300 border-rose-800/80";
      Icon = XCircle;
      label = "Failed";
      break;
    case "TIMED_OUT":
      colorClass = "bg-amber-950/60 text-amber-300 border-amber-800/80";
      Icon = AlertTriangle;
      label = "Timed Out";
      break;
    case "CANCELLED":
    case "CANCEL_REQUESTED":
      colorClass = "bg-neutral-800 text-neutral-400 border-neutral-700";
      Icon = Ban;
      label = "Cancelled";
      break;
    case "SECURITY_DENIED":
      colorClass = "bg-rose-950/60 text-rose-300 border-rose-800/80";
      Icon = Ban;
      label = "Security Denied";
      break;
  }

  const isSpinning = status === "RUNNING" || status === "STREAMING" || status === "STARTING";

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono border ${colorClass} ${className}`}
      title={`Execution status: ${status}`}
    >
      <Icon className={`w-3.5 h-3.5 ${isSpinning ? "animate-spin" : ""}`} />
      <span className="font-semibold uppercase tracking-wider">{label}</span>
      {durationMs != null && (
        <span className="opacity-75 text-[10px]">
          {durationMs < 1000 ? `${durationMs.toFixed(1)}ms` : `${(durationMs / 1000).toFixed(2)}s`}
        </span>
      )}
    </div>
  );
};
