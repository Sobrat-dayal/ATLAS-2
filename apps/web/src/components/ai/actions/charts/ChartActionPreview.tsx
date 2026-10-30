"use client";

import React from "react";
import { ActionDTO } from "@/lib/ai/actions/types";

interface ChartActionPreviewProps {
  action: ActionDTO;
}

export function ChartActionPreview({ action }: ChartActionPreviewProps) {
  const args = action.proposed_arguments;
  const preview = action.preview;

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Target Chart</div>
          <div className="font-mono text-neutral-200 truncate">{action.target_resource_id}</div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Instrument</div>
          <div className="font-mono text-emerald-400 font-semibold">
            {args.instrument_id || preview?.current_state?.instrument_id || "Active"}
          </div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Timeframe</div>
          <div className="font-mono text-neutral-200">
            {args.interval || preview?.current_state?.interval || "1D"}
          </div>
        </div>
        <div className="p-2 rounded bg-neutral-900 border border-neutral-800">
          <div className="text-neutral-500 text-[10px] uppercase font-semibold">Type</div>
          <div className="capitalize text-neutral-200">
            {args.chart_type || preview?.current_state?.chart_type || "Candlestick"}
          </div>
        </div>
      </div>

      {preview && preview.financial_assumptions.length > 0 && (
        <div className="p-2.5 rounded bg-neutral-900/50 border border-neutral-800 text-xs">
          <div className="text-neutral-400 font-medium mb-1.5">Technical Indicator Assumptions:</div>
          <ul className="list-disc list-inside space-y-0.5 text-neutral-300">
            {preview.financial_assumptions.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

