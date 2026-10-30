"use client";

import React from "react";
import {
  formatActionStatusBadge,
  formatClassificationBadge,
} from "@/lib/ai/actions/formatting";
import { ActionDTO, ExecutionReceiptDTO } from "@/lib/ai/actions/types";
import { AiActionPreview } from "./AiActionPreview";
import { AiActionReceipt } from "./AiActionReceipt";

interface AiActionCardProps {
  action: ActionDTO;
  receipt?: ExecutionReceiptDTO | null;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
  onUndo?: (actionId: string, receiptId: string) => void;
  isLoading?: boolean;
}

export function AiActionCard({
  action,
  receipt,
  onApprove,
  onDeny,
  onUndo,
  isLoading = false,
}: AiActionCardProps) {
  const classBadge = formatClassificationBadge(action.classification);
  const statusBadge = formatActionStatusBadge(action.action_status);

  return (
    <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 shadow-sm overflow-hidden text-xs">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 p-3 border-b border-neutral-800 bg-neutral-900/70">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-neutral-200 capitalize">
            {action.target_module} Action
          </span>
          <span className="font-mono text-neutral-500 text-[11px]">
            {action.action_type.split(".").pop()?.replace(/_/g, " ")}
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${classBadge.colorClass}`}
          >
            {classBadge.label}
          </span>
          <span
            className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${statusBadge.colorClass}`}
          >
            {statusBadge.label}
          </span>
        </div>
      </div>

      {/* Body: Preview / Approval */}
      <div className="p-3 space-y-3">
        <AiActionPreview
          action={action}
          onApprove={onApprove}
          onDeny={onDeny}
          isLoading={isLoading}
        />

        {/* Execution Receipt if completed */}
        {receipt && (
          <AiActionReceipt receipt={receipt} onUndo={onUndo} isUndoing={isLoading} />
        )}
      </div>
    </div>
  );
}

