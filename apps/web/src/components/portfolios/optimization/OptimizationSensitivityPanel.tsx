"use client";

import React from "react";
import { SensitivityScenarioDTO } from "@/lib/portfolios/optimization/types";
import { formatPercent, formatWeightPercent } from "@/lib/portfolios/optimization/formatting";
import { Activity, Compass, Flame, ShieldAlert, Sparkles, TrendingUp } from "lucide-react";

interface OptimizationSensitivityPanelProps {
  scenarios: SensitivityScenarioDTO[];
}

export function OptimizationSensitivityPanel({
  scenarios,
}: OptimizationSensitivityPanelProps) {
  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-8 text-center text-xs text-atlas-text-muted">
        No sensitivity scenarios recorded for this optimization run.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-atlas-accent" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            Optimization Sensitivity & Parameter Stress Scenarios
          </h3>
        </div>
        <p className="mt-0.5 text-xs text-atlas-text-muted">
          Evaluating portfolio weight robustness under alpha shifts (+100 bps) and risk aversion spectrum perturbations (&lambda; &isin; [1.0, 4.0]).
        </p>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {scenarios.map((sc, idx) => {
          const ret = parseFloat(sc.estimated_return) || 0;
          const vol = parseFloat(sc.estimated_volatility) || 0;
          const turnover = parseFloat(sc.estimated_turnover) || 0;
          const sharpe = vol > 0.0001 ? ret / vol : 0;

          // Determine icon and color accent
          let icon = <Compass className="h-4 w-4 text-cyan-400" />;
          let badgeColor = "bg-cyan-500/10 text-cyan-300 border-cyan-500/20";

          if (sc.scenario_name.toLowerCase().includes("conservative") || sc.parameter_value === "4.0") {
            icon = <ShieldAlert className="h-4 w-4 text-emerald-400" />;
            badgeColor = "bg-emerald-500/10 text-emerald-300 border-emerald-500/20";
          } else if (sc.scenario_name.toLowerCase().includes("aggressive") || sc.parameter_value === "1.0") {
            icon = <Flame className="h-4 w-4 text-amber-400" />;
            badgeColor = "bg-amber-500/10 text-amber-300 border-amber-500/20";
          } else if (sc.scenario_name.toLowerCase().includes("optimistic") || sc.parameter_name === "alpha_shock") {
            icon = <TrendingUp className="h-4 w-4 text-purple-400" />;
            badgeColor = "bg-purple-500/10 text-purple-300 border-purple-500/20";
          }

          // Top 4 holdings by weight
          const sortedWeights = Object.entries(sc.candidate_weights || {})
            .map(([s, w]) => ({ symbol: s, weight: parseFloat(w) || 0 }))
            .sort((a, b) => b.weight - a.weight)
            .slice(0, 4);

          return (
            <div
              key={idx}
              className="flex flex-col justify-between rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 space-y-4"
            >
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {icon}
                    <h4 className="text-sm font-bold text-atlas-text-primary">
                      {sc.scenario_name}
                    </h4>
                  </div>
                  <span className={`rounded border px-1.5 py-0.5 text-[10px] font-mono font-semibold ${badgeColor}`}>
                    {sc.parameter_name}={sc.parameter_value}
                  </span>
                </div>

                {/* Metrics Breakdown */}
                <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded bg-atlas-surface-2/40 p-2">
                    <span className="text-[10px] text-atlas-text-muted">Expected Return</span>
                    <p className="font-mono font-bold text-emerald-400">{formatPercent(ret)}</p>
                  </div>

                  <div className="rounded bg-atlas-surface-2/40 p-2">
                    <span className="text-[10px] text-atlas-text-muted">Volatility</span>
                    <p className="font-mono font-bold text-atlas-text-primary">{formatPercent(vol)}</p>
                  </div>

                  <div className="rounded bg-atlas-surface-2/40 p-2">
                    <span className="text-[10px] text-atlas-text-muted">Sharpe Ratio</span>
                    <p className="font-mono font-bold text-cyan-300">{sharpe.toFixed(2)}</p>
                  </div>

                  <div className="rounded bg-atlas-surface-2/40 p-2">
                    <span className="text-[10px] text-atlas-text-muted">Turnover</span>
                    <p className="font-mono font-bold text-amber-300">{formatWeightPercent(turnover)}</p>
                  </div>
                </div>
              </div>

              {/* Top Holdings in Scenario */}
              <div>
                <span className="text-[10px] uppercase tracking-wider text-atlas-text-muted">
                  Dominant Weights
                </span>
                <div className="mt-1.5 space-y-1">
                  {sortedWeights.map((hw) => (
                    <div
                      key={hw.symbol}
                      className="flex items-center justify-between text-[11px] font-mono"
                    >
                      <span className="text-atlas-text-secondary">{hw.symbol}</span>
                      <span className="font-semibold text-atlas-text-primary">
                        {formatWeightPercent(hw.weight)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
