"use client";

import React from "react";
import { formatBps, formatPercent, getEffectColorClass } from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO } from "@/lib/portfolios/attribution/types";

interface ActiveReturnWaterfallProps {
  run: AttributionRunDTO;
}

interface WaterfallStep {
  label: string;
  value: number;
  isTotal?: boolean;
  cumulativeStart: number;
  cumulativeEnd: number;
}

export function ActiveReturnWaterfall({ run }: ActiveReturnWaterfallProps) {
  const alloc = parseFloat(run.total_allocation_effect || "0");
  const select = parseFloat(run.total_selection_effect || "0");
  const inter = parseFloat(run.total_interaction_effect || "0");
  const residual = parseFloat(run.reconciliation_residual || "0");
  const active = parseFloat(run.active_return || "0");

  const steps: WaterfallStep[] = [
    {
      label: "Allocation Effect",
      value: alloc,
      cumulativeStart: 0,
      cumulativeEnd: alloc,
    },
    {
      label: "Selection Effect",
      value: select,
      cumulativeStart: alloc,
      cumulativeEnd: alloc + select,
    },
    {
      label: "Interaction",
      value: inter,
      cumulativeStart: alloc + select,
      cumulativeEnd: alloc + select + inter,
    },
  ];

  if (Math.abs(residual) > 0.00001) {
    steps.push({
      label: "Residual",
      value: residual,
      cumulativeStart: alloc + select + inter,
      cumulativeEnd: alloc + select + inter + residual,
    });
  }

  steps.push({
    label: "Active Return",
    value: active,
    isTotal: true,
    cumulativeStart: 0,
    cumulativeEnd: active,
  });

  // Calculate dynamic scale
  let minVal = 0;
  let maxVal = 0;
  steps.forEach((s) => {
    minVal = Math.min(minVal, s.cumulativeStart, s.cumulativeEnd);
    maxVal = Math.max(maxVal, s.cumulativeStart, s.cumulativeEnd);
  });
  const span = Math.max(Math.abs(maxVal - minVal), 0.01) * 1.25;
  const zeroY = 120 + ((maxVal) / span) * 100;

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
      <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-2">
        <div>
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Active Return Decomposition Waterfall
          </h3>
          <p className="text-xs text-atlas-text-secondary">
            Mathematical breakdown of active return into Brinson-Fachler allocation, selection, and interaction components.
          </p>
        </div>
        <div className="text-right">
          <span className="text-xs font-medium text-atlas-text-secondary">Total Active Return: </span>
          <span className={`text-sm font-bold ${getEffectColorClass(run.active_return)}`}>
            {formatPercent(run.active_return, 2, true)} ({formatBps(run.active_return)})
          </span>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-5">
        {steps.map((step, idx) => {
          const isPos = step.value >= 0;
          return (
            <div
              key={idx}
              className={`rounded border p-3 transition-colors ${
                step.isTotal
                  ? "border-atlas-accent/40 bg-atlas-surface-2/80 font-medium"
                  : "border-atlas-border-default/40 bg-atlas-surface-2/40"
              }`}
            >
              <div className="text-[11px] font-medium text-atlas-text-secondary">
                {step.label}
              </div>
              <div className={`mt-1.5 text-base font-bold ${getEffectColorClass(step.value)}`}>
                {formatPercent(step.value, 2, true)}
              </div>
              <div className="mt-0.5 text-[11px] text-atlas-text-muted">
                {formatBps(step.value)}
              </div>

              {/* Progress bar visualizer */}
              <div className="mt-2.5 h-1.5 w-full overflow-hidden rounded-full bg-atlas-surface-3">
                <div
                  className={`h-full ${
                    step.isTotal
                      ? isPos ? "bg-emerald-400" : "bg-rose-400"
                      : isPos ? "bg-emerald-500/80" : "bg-rose-500/80"
                  }`}
                  style={{
                    width: `${Math.min(Math.abs(step.value) * 1000, 100)}%`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

