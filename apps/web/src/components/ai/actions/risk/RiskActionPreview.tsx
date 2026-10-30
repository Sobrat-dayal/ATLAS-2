"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";

interface RiskActionPreviewProps {
  action: ActionDTO;
}

export function RiskActionPreview({ action }: RiskActionPreviewProps) {
  const args = action.proposed_arguments;
  const preview = action.preview;

  return (
    <div className="space-y-3 text-xs">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Portfolio</div>
          <div className="font-mono text-neutral-200">{args.portfolio_id}</div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Model</div>
          <div className="font-mono text-cyan-400 capitalize">
            {(args.model_id || "historical_var").replace(/_/g, " ")}
          </div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Confidence</div>
          <div className="font-mono text-emerald-400 font-semibold">
            {args.confidence_level ? `${(args.confidence_level * 100).toFixed(1)}%` : "99.0%"}
          </div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Horizon</div>
          <div className="font-mono text-neutral-200">
            {args.horizon_days ? `${args.horizon_days} Day(s)` : "1 Day"}
          </div>
        </div>
      </div>

      <div className="p-2.5 rounded bg-neutral-900/60 border border-neutral-800 space-y-1">
        <div className="text-neutral-400 font-medium">Institutional Governance Policy:</div>
        <p className="text-[11px] text-neutral-400 leading-relaxed">
          Risk calculations are executed via isolated worker infrastructure. Completed Risk Runs
          generate immutable audit records and cannot be overwritten or undone.
        </p>
      </div>

      {preview && preview.financial_assumptions.length > 0 && (
        <div className="p-2.5 rounded bg-neutral-900/40 border border-neutral-800">
          <div className="text-neutral-400 font-medium mb-1">Model Assumptions & Constraints:</div>
          <ul className="list-disc list-inside space-y-0.5 text-neutral-400 text-[11px]">
            {preview.financial_assumptions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

