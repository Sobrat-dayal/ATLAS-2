"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";

interface AiActionApprovalProps {
  action: ActionDTO;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
  isLoading?: boolean;
}

export function AiActionApproval({
  action,
  onApprove,
  onDeny,
  isLoading = false,
}: AiActionApprovalProps) {
  const isApproved = action.action_status === "APPROVED";
  const isDenied = action.action_status === "DENIED";
  const isExecuted =
    action.action_status === "COMPLETED" ||
    action.action_status === "EXECUTING";

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 rounded-lg border border-neutral-800 bg-neutral-900/60 text-xs">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-neutral-200">Execution Authorization:</span>
          {isApproved ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ✓ User Confirmed
            </span>
          ) : isDenied ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              ✕ Denied by User
            </span>
          ) : isExecuted ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Executed
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
              ⚠ Explicit Confirmation Required
            </span>
          )}
        </div>
        {action.preview && (
          <div className="flex items-center gap-3 text-[10px] text-neutral-500 font-mono">
            <span>Hash: {action.preview.preview_hash.slice(0, 12)}...</span>
            <span>Rev: {action.expected_resource_revision}</span>
          </div>
        )}
      </div>

      {!isApproved && !isDenied && !isExecuted && (
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            type="button"
            onClick={() => onDeny(action.action_id)}
            disabled={isLoading}
            className="flex-1 sm:flex-none px-3 py-1.5 rounded border border-neutral-700 hover:bg-neutral-800 text-neutral-400 hover:text-neutral-200 font-medium transition-colors disabled:opacity-50"
          >
            Deny
          </button>
          <button
            type="button"
            onClick={() => onApprove(action.action_id)}
            disabled={isLoading}
            className="flex-1 sm:flex-none px-4 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
          >
            {isLoading ? "Validating..." : "Approve & Confirm"}
          </button>
        </div>
      )}
    </div>
  );
}

