"use client";

/**
 * Active Indicators Strip & Legend Component (Stage 69).
 *
 * Renders active indicator study badges with real-time/crosshair values,
 * visibility toggles, configuration triggers, and removal actions.
 */

import React from "react";
import { Eye, EyeOff, Settings, Trash2 } from "lucide-react";
import {
  HoveredBarData,
  IndicatorCalculationResult,
  IndicatorDefinition,
  IndicatorInstanceConfig,
} from "@/lib/charts";

export interface ActiveIndicatorsProps {
  instances: IndicatorInstanceConfig[];
  catalog?: IndicatorDefinition[];
  results: IndicatorCalculationResult[];
  hoveredBar?: HoveredBarData | null;
  onToggleVisibility: (instanceId: string) => void;
  onConfigure: (instance: IndicatorInstanceConfig) => void;
  onRemove: (instanceId: string) => void;
}

export function ActiveIndicators({
  instances,
  catalog = [],
  results,
  hoveredBar,
  onToggleVisibility,
  onConfigure,
  onRemove,
}: ActiveIndicatorsProps) {
  if (instances.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 px-3 py-1.5 bg-zinc-950/80 border-b border-zinc-800/80 text-xs">
      <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-semibold mr-1">
        Studies:
      </span>

      {instances.map((inst) => {
        const defn = catalog.find((d) => d.indicator_id === inst.indicator_id);
        const res = results.find((r) => r.instance_id === inst.instance_id);

        // Find value at hovered bar, or fallback to latest point
        let displayVal: string = "—";
        let pointStatus = res?.status || "READY";

        if (res && res.series.length > 0) {
          const pts = res.series[0].points;
          if (pts.length > 0) {
            let matchedPt = null;
            if (hoveredBar?.time_unix) {
              matchedPt = pts.find((p) => p.time_unix === hoveredBar.time_unix);
            }
            if (!matchedPt) {
              // fallback to latest valid point in series
              for (let i = pts.length - 1; i >= 0; i--) {
                if (pts[i].value != null) {
                  matchedPt = pts[i];
                  break;
                }
              }
              if (!matchedPt) {
                matchedPt = pts[pts.length - 1];
              }
            }

            if (matchedPt) {
              pointStatus = matchedPt.status;
              if (matchedPt.value != null) {
                displayVal = matchedPt.value.toFixed(2);
              }
            }
          }
        }

        const period = inst.parameters["period"] || 20;
        const label = `${defn?.display_name || "SMA"} (${period})`;
        const color = inst.color || defn?.default_color || "#38bdf8";

        return (
          <div
            key={inst.instance_id}
            className={`flex items-center gap-2 px-2 py-0.5 rounded border text-[11px] font-mono transition-colors ${
              inst.visible
                ? "bg-zinc-900/90 border-zinc-800 text-zinc-200"
                : "bg-zinc-950/50 border-zinc-900 text-zinc-500 opacity-60"
            }`}
          >
            {/* Swatch & Title */}
            <div className="flex items-center gap-1.5">
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: color }}
              />
              <span className="font-medium text-zinc-100">{label}</span>
            </div>

            {/* Value / Status */}
            <div className="flex items-center gap-1 font-semibold">
              {pointStatus === "READY" ? (
                <span style={{ color }}>{displayVal}</span>
              ) : pointStatus === "WARMUP" ? (
                <span className="text-zinc-500 text-[10px] uppercase">Warmup</span>
              ) : pointStatus === "DATA_GAP" ? (
                <span className="text-amber-500 text-[10px] uppercase">Gap</span>
              ) : pointStatus === "INSUFFICIENT_HISTORY" ? (
                <span className="text-rose-400 text-[10px] uppercase">Low Bars</span>
              ) : (
                <span className="text-zinc-500 text-[10px]">—</span>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-1 ml-1 pl-1 border-l border-zinc-800">
              <button
                type="button"
                onClick={() => onToggleVisibility(inst.instance_id)}
                className="text-zinc-400 hover:text-zinc-100 p-0.5 rounded hover:bg-zinc-800 transition-colors"
                title={inst.visible ? "Hide indicator" : "Show indicator"}
                aria-label={inst.visible ? "Hide indicator" : "Show indicator"}
              >
                {inst.visible ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3 text-zinc-600" />}
              </button>

              <button
                type="button"
                onClick={() => onConfigure(inst)}
                className="text-zinc-400 hover:text-zinc-100 p-0.5 rounded hover:bg-zinc-800 transition-colors"
                title="Configure indicator parameters"
                aria-label="Configure indicator parameters"
              >
                <Settings className="w-3 h-3" />
              </button>

              <button
                type="button"
                onClick={() => onRemove(inst.instance_id)}
                className="text-zinc-400 hover:text-rose-400 p-0.5 rounded hover:bg-zinc-800 transition-colors"
                title="Remove indicator"
                aria-label="Remove indicator"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
