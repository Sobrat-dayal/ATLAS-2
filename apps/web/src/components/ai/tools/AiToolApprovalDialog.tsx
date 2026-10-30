"use client";

import React, { useState } from "react";
import { AlertTriangle, CheckCircle, XCircle, ShieldAlert, X } from "lucide-react";
import { AiToolApprovalRequest } from "@/lib/ai/tools/types";

interface AiToolApprovalDialogProps {
  approval: AiToolApprovalRequest | null;
  isOpen: boolean;
  onApprove: (reason?: string) => Promise<void>;
  onDeny: (reason?: string) => Promise<void>;
  onClose: () => void;
  loading?: boolean;
}

export function AiToolApprovalDialog({
  approval,
  isOpen,
  onApprove,
  onDeny,
  onClose,
  loading = false,
}: AiToolApprovalDialogProps) {
  const [reason, setReason] = useState("");

  if (!isOpen || !approval) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="flex flex-col w-full max-w-lg rounded-lg border border-amber-600/40 bg-zinc-900 shadow-2xl text-zinc-100 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3 bg-amber-950/20">
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <div>
              <h3 className="text-sm font-semibold tracking-wide text-amber-200">
                Action Approval Required
              </h3>
              <p className="text-xs text-zinc-400 font-mono">{approval.tool_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Warning callout */}
        <div className="p-4 space-y-4">
          <div className="flex items-start gap-3 rounded-md bg-amber-500/10 border border-amber-500/20 p-3 text-xs text-amber-200">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              The AI Assistant has proposed an operation requiring explicit user authorization
              ({approval.approval_class}). Verify the proposed arguments before confirming.
            </div>
          </div>

          {/* Arguments Summary */}
          <div>
            <span className="text-xs font-medium text-zinc-400">Proposed Parameters:</span>
            <div className="mt-1.5 rounded bg-zinc-950 border border-zinc-800 p-2.5 font-mono text-xs text-zinc-300 max-h-40 overflow-auto">
              <pre>{JSON.stringify(approval.arguments_summary, null, 2)}</pre>
            </div>
          </div>

          {/* Decision Reason input */}
          <div>
            <label className="block text-xs font-medium text-zinc-400 mb-1">
              Optional Decision Note:
            </label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Authorized for current analysis session"
              className="w-full rounded bg-zinc-950 border border-zinc-800 px-3 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-2 border-t border-zinc-800 px-4 py-3 bg-zinc-950/60">
          <button
            onClick={() => onDeny(reason || "Denied by user")}
            disabled={loading}
            className="flex items-center gap-1.5 rounded bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-300 hover:bg-zinc-700 hover:text-rose-300 transition-colors disabled:opacity-50"
          >
            <XCircle className="w-3.5 h-3.5" />
            <span>Deny</span>
          </button>
          <button
            onClick={() => onApprove(reason || "Approved by user")}
            disabled={loading}
            className="flex items-center gap-1.5 rounded bg-amber-600 hover:bg-amber-500 px-4 py-1.5 text-xs font-semibold text-white shadow transition-colors disabled:opacity-50"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>{loading ? "Processing..." : "Approve & Execute"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

