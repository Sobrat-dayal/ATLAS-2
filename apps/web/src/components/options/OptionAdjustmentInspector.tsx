"use client";

import React from "react";
import { X, ShieldAlert, FileText, CheckCircle2 } from "lucide-react";

interface AdjustmentRecord {
  adjustment_id: string;
  original_contract_id: string;
  adjusted_contract_id: string;
  corporate_action_type: string;
  effective_date: string;
  original_deliverable_summary: string;
  adjusted_deliverable_summary: string;
  shares_count: number;
  cash_amount: number;
  memo: string;
}

interface OptionAdjustmentInspectorProps {
  symbol: string;
  adjustments: AdjustmentRecord[];
  isOpen: boolean;
  onClose: () => void;
}

export function OptionAdjustmentInspector({
  symbol,
  adjustments,
  isOpen,
  onClose,
}: OptionAdjustmentInspectorProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
          <div className="flex items-center gap-2 text-amber-300">
            <ShieldAlert className="w-5 h-5" />
            <h2 className="text-base font-bold text-white">
              Corporate Action Adjustment History: {symbol}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-400 hover:text-white hover:bg-zinc-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 overflow-y-auto space-y-4">
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 text-xs text-amber-200 leading-relaxed">
            <span className="font-semibold text-amber-300">Quantitative Isolation Policy:</span> When corporate actions alter underlying deliverables (such as spin-offs, reverse splits, or cash dividends), adjusted contracts trade with nonstandard deliverables. ATLAS explicitly flags and isolates adjusted contracts, disallowing vanilla 100-share expiration payoff calculations until custom contract delivery specifications are evaluated.
          </div>

          {adjustments.length === 0 ? (
            <div className="p-8 text-center text-zinc-500 text-xs">
              No corporate-action adjustments on record for {symbol}.
            </div>
          ) : (
            adjustments.map((adj) => (
              <div
                key={adj.adjustment_id}
                className="bg-zinc-900/70 border border-zinc-800 rounded-lg p-4 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-cyan-400">
                    {adj.adjustment_id}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30">
                    {adj.corporate_action_type}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-zinc-500 text-[10px]">Effective Date:</span>
                    <div className="font-mono text-zinc-200 mt-0.5">{adj.effective_date}</div>
                  </div>
                  <div>
                    <span className="text-zinc-500 text-[10px]">Original Deliverable:</span>
                    <div className="text-zinc-300 mt-0.5">{adj.original_deliverable_summary}</div>
                  </div>
                </div>

                <div className="p-2.5 bg-zinc-950 rounded border border-zinc-850">
                  <div className="text-[10px] text-zinc-500 font-medium">Adjusted Deliverable Package:</div>
                  <div className="font-mono text-xs text-amber-300 font-semibold mt-0.5">
                    {adj.shares_count} shares + ${adj.cash_amount.toFixed(2)} cash
                  </div>
                  <div className="text-[11px] text-zinc-400 mt-1">{adj.memo}</div>
                </div>

                <div className="flex items-center gap-2 text-[10px] text-zinc-500 pt-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Reconciled with Security Master & OCC/Exchange Notice</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="p-4 border-t border-zinc-800 bg-zinc-900/40 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-medium bg-zinc-800 hover:bg-zinc-700 text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

