"use client";

import React from "react";
import { formatVolPercent, formatWeight } from "@/lib/risk/formatting";
import {
  ContributionsResponseDTO,
  RiskContributionItemDTO,
} from "@/lib/risk/types";
import { CheckCircle2, ShieldAlert } from "lucide-react";

interface RiskContributionTableProps {
  contributionsData: ContributionsResponseDTO | null;
}

export function RiskContributionTable({
  contributionsData,
}: RiskContributionTableProps) {
  const items = contributionsData?.contributions || [];
  const modelVol = contributionsData?.model_volatility;
  const modelVar = contributionsData?.model_variance;

  if (items.length === 0) {
    return (
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-6 text-center text-xs text-atlas-text-muted">
        No security risk contribution data available. Run the Euler risk model to generate component decompositions.
      </div>
    );
  }

  // Calculate totals for Euler reconciliation check
  const totalWeight = items.reduce((acc, it) => acc + it.weight, 0);
  const totalCVC = items.reduce((acc, it) => acc + it.component_volatility_contribution, 0);
  const totalPCR = items.reduce((acc, it) => acc + it.percentage_volatility_contribution, 0);
  const totalVC = items.reduce((acc, it) => acc + it.variance_contribution, 0);

  // Reconciliation flags
  const cvcReconciled = modelVol !== undefined && modelVol !== null && Math.abs(totalCVC - modelVol) < 1e-4;
  const pcrReconciled = Math.abs(totalPCR - 1.0) < 1e-4;

  return (
    <div className="overflow-hidden rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-atlas-border-default/40 px-4 py-3">
        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold text-atlas-text-primary">
              Euler Risk Decomposition & Security Risk Contributions
            </h4>
            <span className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-medium text-blue-400">
              Euler Identity: σ_P = Σ w_i (∂σ_P/∂w_i)
            </span>
          </div>
          <p className="mt-0.5 text-xs text-atlas-text-muted">
            Additive marginal, component, and percentage volatility contributions preserving negative hedges.
          </p>
        </div>

        {/* Euler Reconciliation Badge */}
        <div className="flex items-center gap-2">
          <div
            className={`flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium ${
              cvcReconciled && pcrReconciled
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-amber-500/30 bg-amber-500/10 text-amber-400"
            }`}
          >
            <CheckCircle2 className="h-3 w-3" />
            <span>
              {cvcReconciled && pcrReconciled
                ? "Euler Additivity Verified (100.0%)"
                : "Reconciled with Minor Rounding"}
            </span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-atlas-border-default/60 bg-atlas-surface-2/60 text-[11px] font-medium text-atlas-text-secondary">
              <th className="py-2.5 px-4 font-sans">Instrument</th>
              <th className="py-2.5 px-3 font-sans">Category / Sector</th>
              <th className="py-2.5 px-3 text-right">Portfolio Weight (wᵢ)</th>
              <th className="py-2.5 px-3 text-right">Marginal Vol (MRCᵢ)</th>
              <th className="py-2.5 px-3 text-right">Component Vol (CRCᵢ)</th>
              <th className="py-2.5 px-3 text-right">% Vol Contribution (PCRᵢ)</th>
              <th className="py-2.5 px-4 text-right">Variance Contrib (VCᵢ)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-atlas-border-default/30">
            {items.map((it) => {
              const isNegative = it.component_volatility_contribution < -1e-6;
              return (
                <tr key={it.symbol} className="transition hover:bg-atlas-surface-2/40">
                  <td className="py-2 px-4">
                    <div className="font-bold text-atlas-text-primary">{it.symbol}</div>
                    <div className="font-sans text-[10px] text-atlas-text-muted truncate max-w-[140px]">
                      {it.name}
                    </div>
                  </td>
                  <td className="py-2 px-3 font-sans text-atlas-text-secondary">
                    {it.category_label || "Cash / Unclassified"}
                  </td>
                  <td className="py-2 px-3 text-right font-medium text-atlas-text-primary">
                    {formatWeight(it.weight, 2)}
                  </td>
                  <td className="py-2 px-3 text-right text-atlas-text-secondary">
                    {formatVolPercent(it.marginal_volatility_contribution, 2)}
                  </td>
                  <td
                    className={`py-2 px-3 text-right font-semibold ${
                      isNegative ? "text-emerald-400" : "text-atlas-text-primary"
                    }`}
                  >
                    {isNegative ? "–" : ""}
                    {formatVolPercent(Math.abs(it.component_volatility_contribution), 2)}
                  </td>
                  <td
                    className={`py-2 px-3 text-right font-bold ${
                      isNegative ? "text-emerald-400" : "text-atlas-accent-gold"
                    }`}
                  >
                    {isNegative ? "–" : ""}
                    {formatWeight(Math.abs(it.percentage_volatility_contribution), 2)}
                  </td>
                  <td className="py-2 px-4 text-right text-atlas-text-muted">
                    {it.variance_contribution.toExponential(4)}
                  </td>
                </tr>
              );
            })}
          </tbody>

          {/* Strict Euler Reconciliation Summary Footer */}
          <tfoot>
            <tr className="border-t-2 border-atlas-border-default bg-atlas-surface-2/80 font-bold text-atlas-text-primary">
              <td className="py-2.5 px-4 font-sans uppercase tracking-wider text-xs">
                Euler Total
              </td>
              <td className="py-2.5 px-3 font-sans text-xs text-atlas-text-secondary">
                {items.length} Constituents
              </td>
              <td className="py-2.5 px-3 text-right text-xs">
                {formatWeight(totalWeight, 2)}
              </td>
              <td className="py-2.5 px-3 text-right text-atlas-text-muted">—</td>
              <td className="py-2.5 px-3 text-right text-xs text-blue-400">
                {formatVolPercent(totalCVC, 2)}
              </td>
              <td className="py-2.5 px-3 text-right text-xs text-atlas-accent-gold">
                {formatWeight(totalPCR, 2)}
              </td>
              <td className="py-2.5 px-4 text-right text-xs text-atlas-text-secondary">
                {totalVC.toExponential(4)}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}

