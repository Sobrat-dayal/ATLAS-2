"use client";

import React from "react";
import { ExecutionReceiptDTO } from "@/lib/ai/actions/types";
import { AiActionDiff } from "./AiActionDiff";

interface AiActionReceiptProps {
  receipt: ExecutionReceiptDTO;
  onUndo?: (actionId: string, receiptId: string) => void;
  isUndoing?: boolean;
}

export function AiActionReceipt({
  receipt,
  onUndo,
  isUndoing = false,
}: AiActionReceiptProps) {
  const isCompleted = receipt.operation_status === "COMPLETED";

  return (
    <div className="p-3.5 rounded-lg border border-neutral-800 bg-neutral-900/60 space-y-3 text-xs">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${
              isCompleted
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-rose-500/10 text-rose-400 border-rose-500/20"
            }`}
          >
            {isCompleted ? "✓ Execution Verified" : "✕ Execution Failed"}
          </span>
          <span className="font-mono text-neutral-400">{receipt.receipt_id}</span>
        </div>

        {onUndo && isCompleted && (
          <button
            type="button"
            onClick={() => onUndo(receipt.action_id, receipt.receipt_id)}
            disabled={isUndoing}
            className="px-2.5 py-1 rounded border border-neutral-700 hover:bg-neutral-800 text-neutral-300 font-medium transition-colors disabled:opacity-50 text-[11px]"
          >
            {isUndoing ? "Restoring..." : "Restore Prior State (Undo)"}
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Target</div>
          <div className="font-mono text-neutral-200 truncate">{receipt.target_resource_id}</div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Prior Revision</div>
          <div className="font-mono text-neutral-400 truncate">{receipt.target_revision_before}</div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Verified Revision</div>
          <div className="font-mono text-emerald-400 font-semibold truncate">{receipt.target_revision_after}</div>
        </div>
      </div>

      {receipt.diffs && receipt.diffs.length > 0 && (
        <div className="space-y-1">
          <div className="text-neutral-400 font-medium text-[11px]">Applied State Changes:</div>
          <AiActionDiff diffs={receipt.diffs} />
        </div>
      )}

      {receipt.error_message && (
        <div className="p-2.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
          <strong>Error ({receipt.error_code || "FAILED"}):</strong> {receipt.error_message}
        </div>
      )}
    </div>
  );
}

