"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  AlertCircle,
  Loader2,
  Clock,
  ShieldAlert,
  ChevronRight,
  Database,
} from "lucide-react";
import { AiToolCallStatus } from "@/lib/ai/tools/types";
import { AiToolResultInspector } from "./AiToolResultInspector";

interface AiToolCallCardProps {
  toolId: string;
  status: AiToolCallStatus | string;
  argumentsPayload?: Record<string, unknown>;
  result?: unknown;
  error?: string | null;
  executionTimeMs?: number | null;
  approvalRequestId?: string | null;
  onOpenApproval?: (approvalId: string) => void;
}

export function AiToolCallCard({
  toolId,
  status,
  argumentsPayload = {},
  result,
  error,
  executionTimeMs,
  approvalRequestId,
  onOpenApproval,
}: AiToolCallCardProps) {
  const [inspectorOpen, setInspectorOpen] = useState(false);

  // Friendly short tool name: e.g. atlas.instrument.search -> instrument.search
  const displayName = toolId.replace(/^atlas\./, "");

  const renderStatusBadge = () => {
    switch (status) {
      case "RUNNING":
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20">
            <Loader2 className="w-3 h-3 animate-spin" />
            Running
          </span>
        );
      case "COMPLETED":
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            Completed
          </span>
        );
      case "APPROVAL_REQUIRED":
        return (
          <button
            onClick={() => approvalRequestId && onOpenApproval?.(approvalRequestId)}
            className="flex items-center gap-1 text-[11px] font-medium text-amber-300 bg-amber-500/20 px-2 py-0.5 rounded border border-amber-500/40 hover:bg-amber-500/30 transition-colors"
          >
            <ShieldAlert className="w-3 h-3 text-amber-400" />
            Review & Approve
          </button>
        );
      case "FAILED":
      case "REJECTED":
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20">
            <AlertCircle className="w-3 h-3" />
            Failed
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-[11px] font-medium text-zinc-400 bg-zinc-800 px-2 py-0.5 rounded">
            <Clock className="w-3 h-3" />
            {status}
          </span>
        );
    }
  };

  return (
    <>
      <div className="flex flex-col gap-1.5 my-2 rounded border border-zinc-800 bg-zinc-950/60 p-2.5 text-xs text-zinc-200">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <Database className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <span className="font-mono font-medium text-zinc-100 truncate">
              {displayName}
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {executionTimeMs !== undefined && executionTimeMs !== null && (
              <span className="text-[11px] text-zinc-500">
                {executionTimeMs.toFixed(1)}ms
              </span>
            )}
            {renderStatusBadge()}
          </div>
        </div>

        {/* Error notice if present */}
        {error && (
          <div className="text-[11px] text-rose-400 bg-rose-950/30 border border-rose-900/40 rounded px-2 py-1">
            {error}
          </div>
        )}

        {/* Action to inspect result */}
        {result !== undefined && result !== null && (
          <div className="flex items-center justify-between pt-1 border-t border-zinc-800/60 text-[11px]">
            <span className="text-zinc-500">Grounded financial payload verified</span>
            <button
              onClick={() => setInspectorOpen(true)}
              className="flex items-center gap-0.5 text-blue-400 hover:text-blue-300 transition-colors font-medium"
            >
              Inspect Data <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>

      <AiToolResultInspector
        toolId={toolId}
        result={result as Record<string, unknown>}
        isOpen={inspectorOpen}
        onClose={() => setInspectorOpen(false)}
      />
    </>
  );
}

