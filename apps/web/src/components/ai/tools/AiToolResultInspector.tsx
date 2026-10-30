"use client";

import React, { useState } from "react";
import { Copy, Check, X, ShieldCheck, Database, Clock, Hash } from "lucide-react";
import { AiToolResult } from "@/lib/ai/tools/types";

interface AiToolResultInspectorProps {
  toolId: string;
  result: AiToolResult | Record<string, unknown> | null;
  isOpen: boolean;
  onClose: () => void;
}

export function AiToolResultInspector({
  toolId,
  result,
  isOpen,
  onClose,
}: AiToolResultInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !result) return null;

  // Normalize result data
  const dataPayload = (result as AiToolResult).data !== undefined
    ? (result as AiToolResult).data
    : result;
  const manifest = (result as AiToolResult).source_manifest;
  const executionTimeMs = (result as AiToolResult).execution_time_ms;
  const asOf = (result as AiToolResult).as_of;
  const contentHash = (result as AiToolResult).content_hash;

  const jsonString = JSON.stringify(dataPayload, null, 2);

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="flex flex-col w-full max-w-2xl max-h-[85vh] rounded-lg border border-zinc-700 bg-zinc-900 shadow-2xl text-zinc-100 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3 bg-zinc-950/60">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-sm font-semibold tracking-wide text-zinc-100">
                Verified AI Tool Result
              </h3>
              <p className="text-xs text-zinc-400 font-mono">{toolId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Metadata Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 border-b border-zinc-800 px-4 py-2.5 bg-zinc-950/30 text-xs">
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span className="truncate">
              {manifest?.data_source || "ATLAS Engine"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-zinc-400">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>
              {executionTimeMs !== undefined ? `${executionTimeMs.toFixed(1)}ms` : "Cached"}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-zinc-400 col-span-2 truncate">
            <Hash className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span className="font-mono text-[11px] truncate">
              {contentHash ? `${contentHash.slice(0, 16)}...` : "Verified SHA-256"}
            </span>
          </div>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-auto p-4 bg-zinc-950/80">
          <pre className="font-mono text-xs text-zinc-300 leading-relaxed overflow-x-auto select-text">
            {jsonString}
          </pre>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-zinc-800 px-4 py-3 bg-zinc-950/60">
          <div className="text-[11px] text-zinc-500">
            {manifest?.attribution || "ATLAS Institutional Security Master"}
            {asOf ? ` • As of ${new Date(asOf).toLocaleTimeString()}` : ""}
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 rounded bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-200 hover:bg-zinc-700 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Payload</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

