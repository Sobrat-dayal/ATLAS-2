/**
 * Structured CLI result display rendering tables, formatted text, and errors.
 */

import React from "react";
import type { TerminalExecutionDetail } from "@/lib/terminal/executionTypes";
import { SqlResultGrid } from "../sql/SqlResultGrid";
import { ExecutionStatusBadge } from "../execution/ExecutionStatusBadge";
import { AlertCircle } from "lucide-react";

interface AtlasCliResultViewerProps {
  execution: TerminalExecutionDetail;
}

export const AtlasCliResultViewer: React.FC<AtlasCliResultViewerProps> = ({ execution }) => {
  const { status, stdout_summary, error_message, error_code, duration_ms, tabular_result } =
    execution;

  return (
    <div className="flex flex-col gap-2 my-2 text-xs font-mono">
      <div className="flex items-center gap-2">
        <ExecutionStatusBadge status={status} durationMs={duration_ms} />
        {error_code && (
          <span className="text-rose-400 font-semibold text-[11px]">
            [{error_code}]
          </span>
        )}
      </div>

      {error_message && (
        <div className="flex items-start gap-2 p-2 rounded bg-rose-950/40 border border-rose-900/60 text-rose-300">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="whitespace-pre-wrap">{error_message}</div>
        </div>
      )}

      {tabular_result && (
        <div className="max-h-64 my-1">
          <SqlResultGrid result={tabular_result} durationMs={duration_ms} />
        </div>
      )}

      {stdout_summary && !tabular_result && (
        <pre className="p-2.5 rounded bg-neutral-900/80 border border-neutral-800 text-neutral-200 overflow-x-auto whitespace-pre-wrap font-mono leading-relaxed text-[11px]">
          {stdout_summary}
        </pre>
      )}
    </div>
  );
};

