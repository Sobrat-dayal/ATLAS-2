"use client";

import React from "react";
import {
  RiskScenarioRunDTO,
  ScenarioComparisonResponseDTO,
} from "@/lib/risk/types";
import {
  formatCurrency,
  formatPnl,
  formatSignedPercent,
  formatWeight,
  getScenarioImpactBadge,
} from "@/lib/risk/formatting";
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  DollarSign,
  Layers,
  Scale,
  ShieldAlert,
  Zap,
} from "lucide-react";

interface ScenarioResultsWorkspaceProps {
  run: RiskScenarioRunDTO | null;
  comparison: ScenarioComparisonResponseDTO | null;
}

export function ScenarioResultsWorkspace({
  run,
  comparison,
}: ScenarioResultsWorkspaceProps) {
  if (!run && !comparison) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-8 text-center text-xs text-atlas-text-muted">
        <Zap className="h-8 w-8 mx-auto text-atlas-text-muted opacity-40 mb-2" />
        <p className="font-medium text-atlas-text-secondary">No Scenario Execution Active</p>
        <p className="mt-1">
          Select any scenario from the library above and click &quot;Shock&quot; to inspect revaluation impact.
        </p>
      </div>
    );
  }

  const impactBadge = run ? getScenarioImpactBadge(run.portfolio_return) : null;

  return (
    <div className="space-y-4">
      {/* 1. Execution Summary Card */}
      {run && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-atlas-border-default/40 pb-2">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-amber-400" />
              <div>
                <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
                  Scenario Shock Results: {run.scenario_id}
                </h3>
                <span className="font-mono text-[10px] text-atlas-text-muted">
                  Run ID: {run.run_id} | As Of: {run.as_of?.substring(0, 10)}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {impactBadge && (
                <span
                  className={`rounded border px-2 py-0.5 text-[11px] font-semibold uppercase ${impactBadge.bgClass} ${impactBadge.textClass} ${impactBadge.borderClass}`}
                >
                  {impactBadge.label}
                </span>
              )}
              {run.is_reconciled ? (
                <span className="flex items-center gap-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 text-[10px] font-mono">
                  <CheckCircle2 className="h-3 w-3" /> Reconciled (diff &lt; 0.0001)
                </span>
              ) : (
                <span className="flex items-center gap-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 px-2 py-0.5 text-[10px] font-mono">
                  Reconciliation Warning: {run.reconciliation_diff}
                </span>
              )}
            </div>
          </div>

          {/* Three Key Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Metric 1: Shocked NAV */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-3">
              <div className="text-[11px] font-medium text-atlas-text-secondary uppercase">
                Shocked Portfolio NAV
              </div>
              <div className="mt-1 text-xl font-bold font-mono text-atlas-text-primary">
                {formatCurrency(run.shocked_nav)}
              </div>
              <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">
                Base NAV: {formatCurrency(run.base_nav)}
              </div>
            </div>

            {/* Metric 2: Portfolio P&L */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-3">
              <div className="text-[11px] font-medium text-atlas-text-secondary uppercase">
                Portfolio Shock P&L
              </div>
              <div
                className={`mt-1 text-xl font-bold font-mono ${
                  run.portfolio_pnl < 0 ? "text-rose-400" : "text-emerald-400"
                }`}
              >
                {formatPnl(run.portfolio_pnl)}
              </div>
              <div className="text-[10px] text-atlas-text-muted mt-0.5 font-mono">
                Exact Σ ΔV_i Position Revaluations
              </div>
            </div>

            {/* Metric 3: Portfolio Shock Return */}
            <div className="rounded border border-atlas-border-default/50 bg-atlas-surface-2 p-3">
              <div className="text-[11px] font-medium text-atlas-text-secondary uppercase">
                Portfolio Shock Return %
              </div>
              <div
                className={`mt-1 text-xl font-bold font-mono flex items-center gap-1 ${
                  run.portfolio_return < 0 ? "text-rose-400" : "text-emerald-400"
                }`}
              >
                {run.portfolio_return < 0 ? (
                  <ArrowDownRight className="h-5 w-5" />
                ) : (
                  <ArrowUpRight className="h-5 w-5" />
                )}
                <span>{formatSignedPercent(run.portfolio_return)}</span>
              </div>
              <div className="text-[10px] text-atlas-text-muted mt-0.5">
                Multiplicative Price &amp; FX Compound
              </div>
            </div>
          </div>

          {/* Position Impact Breakdown Table */}
          <div className="border-t border-atlas-border-default/40 pt-2">
            <div className="text-[11px] font-semibold text-atlas-text-secondary uppercase tracking-wider mb-2 flex items-center gap-1">
              <Layers className="h-3.5 w-3.5 text-atlas-accent-blue" />
              <span>Position Revaluation &amp; Precedence Collision Breakdown</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse font-mono">
                <thead>
                  <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-3 text-[10px] font-semibold text-atlas-text-secondary uppercase">
                    <th className="py-1.5 px-2">Instrument</th>
                    <th className="py-1.5 px-2 text-right">Base Weight</th>
                    <th className="py-1.5 px-2 text-right">Base Price</th>
                    <th className="py-1.5 px-2 text-right">Shock Price</th>
                    <th className="py-1.5 px-2 text-right">Base Value</th>
                    <th className="py-1.5 px-2 text-right">Shocked Value</th>
                    <th className="py-1.5 px-2 text-right">P&amp;L</th>
                    <th className="py-1.5 px-2 text-right">Return %</th>
                    <th className="py-1.5 px-2">Applied Shock / Priority</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-atlas-border-default/40 text-[11px]">
                  {run.positions.map((pos) => (
                    <tr key={pos.symbol} className="hover:bg-atlas-surface-2/60 transition">
                      <td className="py-2 px-2">
                        <div className="font-bold text-atlas-text-primary">{pos.symbol}</div>
                        <div className="text-[10px] text-atlas-text-muted font-sans truncate max-w-[140px]">
                          {pos.name}
                        </div>
                      </td>
                      <td className="py-2 px-2 text-right text-atlas-text-secondary">
                        {formatWeight(pos.weight)}
                      </td>
                      <td className="py-2 px-2 text-right text-atlas-text-secondary">
                        ${pos.base_price?.toFixed(2)}
                      </td>
                      <td className="py-2 px-2 text-right text-atlas-text-primary">
                        ${pos.shocked_price?.toFixed(2)}
                      </td>
                      <td className="py-2 px-2 text-right text-atlas-text-secondary">
                        {formatCurrency(pos.base_value)}
                      </td>
                      <td className="py-2 px-2 text-right font-bold text-atlas-text-primary">
                        {formatCurrency(pos.shocked_value)}
                      </td>
                      <td
                        className={`py-2 px-2 text-right font-bold ${
                          pos.pnl < 0 ? "text-rose-400" : "text-emerald-400"
                        }`}
                      >
                        {formatPnl(pos.pnl)}
                      </td>
                      <td
                        className={`py-2 px-2 text-right font-bold ${
                          pos.return_pct < 0 ? "text-rose-400" : "text-emerald-400"
                        }`}
                      >
                        {formatSignedPercent(pos.return_pct)}
                      </td>
                      <td className="py-2 px-2 text-[10px] font-sans">
                        <span className="rounded bg-atlas-surface-3 px-1.5 py-0.5 border border-atlas-border-default/50 text-atlas-text-secondary">
                          {pos.matched_shock_type} ({(pos.applied_shock_magnitude * 100).toFixed(1)}%)
                        </span>
                        {pos.fx_shock_magnitude !== 0 && (
                          <span className="ml-1 rounded bg-purple-500/10 text-purple-300 px-1 py-0.5">
                            FX: {(pos.fx_shock_magnitude * 100).toFixed(1)}%
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* 2. Multi-Scenario Comparison Matrix */}
      {comparison && comparison.scenarios && comparison.scenarios.length > 0 && (
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-3.5 space-y-3">
          <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-atlas-accent-blue" />
              <h3 className="text-xs font-semibold text-atlas-text-primary uppercase tracking-wider">
                Multi-Scenario Comparative Stress Matrix
              </h3>
            </div>
            <div className="font-mono text-[10px] text-atlas-text-muted">
              Base NAV: {formatCurrency(comparison.base_nav)}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2 text-[11px] font-semibold text-atlas-text-secondary uppercase">
                  <th className="py-2 px-3">Scenario</th>
                  <th className="py-2 px-3">Type</th>
                  <th className="py-2 px-3 text-right">Shocked NAV</th>
                  <th className="py-2 px-3 text-right">Portfolio P&amp;L</th>
                  <th className="py-2 px-3 text-right">Return %</th>
                  <th className="py-2 px-3">Worst-Hit Position</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-atlas-border-default/40 font-mono">
                {comparison.scenarios.map((item) => (
                  <tr key={item.scenario_id} className="hover:bg-atlas-surface-2/60 transition">
                    <td className="py-2 px-3">
                      <div className="font-bold text-atlas-text-primary font-sans">
                        {item.scenario_name}
                      </div>
                      <div className="text-[10px] text-atlas-text-muted">{item.scenario_id}</div>
                    </td>
                    <td className="py-2 px-3 font-sans">
                      <span className="rounded bg-atlas-surface-3 px-1.5 py-0.5 text-[10px] text-atlas-text-secondary">
                        {item.scenario_type.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right text-atlas-text-primary">
                      {formatCurrency(item.shocked_nav)}
                    </td>
                    <td
                      className={`py-2 px-3 text-right font-bold ${
                        item.portfolio_pnl < 0 ? "text-rose-400" : "text-emerald-400"
                      }`}
                    >
                      {formatPnl(item.portfolio_pnl)}
                    </td>
                    <td
                      className={`py-2 px-3 text-right font-bold ${
                        item.portfolio_return < 0 ? "text-rose-400" : "text-emerald-400"
                      }`}
                    >
                      {formatSignedPercent(item.portfolio_return)}
                    </td>
                    <td className="py-2 px-3 text-atlas-text-secondary">
                      <span className="font-bold text-rose-400">{item.worst_position_symbol}</span>{" "}
                      ({formatPnl(item.worst_position_pnl)})
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

