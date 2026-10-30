"use client";

import React from "react";
import { BookOpen, Calculator, Info, ShieldAlert } from "lucide-react";

export function MethodologyInspectorPanel() {
  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
        <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2">
          <BookOpen className="h-4 w-4 text-atlas-accent" />
          <h3 className="text-sm font-semibold text-atlas-text-primary">
            Institutional Attribution Mathematical Specifications
          </h3>
        </div>
        <p className="mt-2 text-xs text-atlas-text-secondary leading-relaxed">
          ATLAS adheres strictly to the CFA Institute Global Investment Performance Standards (GIPS) and the Brinson-Fachler (1985)
          framework for arithmetic single-period decomposition, combined with Carino (1999) logarithmic linking for compounding multi-period attribution.
        </p>
      </div>

      {/* Grid of Methodology Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Brinson-Fachler Decomposition */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            1. Brinson-Fachler Model (Default)
          </h4>
          <p className="mt-1 text-xs text-atlas-text-secondary">
            Evaluates sector allocation relative to the total benchmark return, penalizing overweighting in underperforming sectors.
          </p>

          <div className="mt-3 space-y-2 rounded bg-atlas-surface-2 p-3 font-mono text-xs">
            <div>
              <span className="text-atlas-text-muted">Allocation Effect:</span>
              <div className="text-atlas-accent font-semibold">A_k = (w_P,k - w_B,k) · (R_B,k - R_B)</div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Selection Effect:</span>
              <div className="text-atlas-accent font-semibold">S_k = w_B,k · (R_P,k - R_B,k)</div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Interaction Effect:</span>
              <div className="text-atlas-accent font-semibold">I_k = (w_P,k - w_B,k) · (R_P,k - R_B,k)</div>
            </div>
            <div className="border-t border-atlas-border-default/40 pt-1">
              <span className="text-atlas-text-muted">Total Segment Effect:</span>
              <div className="text-emerald-400 font-bold">E_k = A_k + S_k + I_k</div>
            </div>
          </div>
        </div>

        {/* Brinson-Hood-Beebower (BHB) Model */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            2. Brinson-Hood-Beebower (BHB) Model
          </h4>
          <p className="mt-1 text-xs text-atlas-text-secondary">
            Classic 1986 allocation formula without benchmark-mean subtraction. Used for historical comparability with legacy systems.
          </p>

          <div className="mt-3 space-y-2 rounded bg-atlas-surface-2 p-3 font-mono text-xs">
            <div>
              <span className="text-atlas-text-muted">Allocation Effect:</span>
              <div className="text-atlas-accent font-semibold">A_k = (w_P,k - w_B,k) · R_B,k</div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Selection Effect:</span>
              <div className="text-atlas-accent font-semibold">S_k = w_B,k · (R_P,k - R_B,k)</div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Interaction Effect:</span>
              <div className="text-atlas-accent font-semibold">I_k = (w_P,k - w_B,k) · (R_P,k - R_B,k)</div>
            </div>
            <div className="border-t border-atlas-border-default/40 pt-1">
              <span className="text-atlas-text-muted">Total Segment Effect:</span>
              <div className="text-emerald-400 font-bold">E_k = A_k + S_k + I_k</div>
            </div>
          </div>
        </div>

        {/* Carino Logarithmic Linking */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            3. Multi-Period Carino Linking Algorithm
          </h4>
          <p className="mt-1 text-xs text-atlas-text-secondary">
            Mathematically converts single-period arithmetic attribution into geometrically linked cumulative active returns.
          </p>

          <div className="mt-3 space-y-2 rounded bg-atlas-surface-2 p-3 font-mono text-xs">
            <div>
              <span className="text-atlas-text-muted">Period Log Scaling Coefficient:</span>
              <div className="text-atlas-accent font-semibold">
                c_t = [ (ln(1 + R_P,t) - ln(1 + R_B,t)) / (R_P,t - R_B,t) ] · [ (R_P - R_B) / (ln(1 + R_P) - ln(1 + R_B)) ]
              </div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Linked Additivity Identity:</span>
              <div className="text-emerald-400 font-bold">Σ c_t · (A_t + S_t + I_t) ≡ R_P^compound - R_B^compound</div>
            </div>
          </div>
        </div>

        {/* Currency & Security Return Contributions */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            4. Contributions & Currency Decomposition
          </h4>
          <p className="mt-1 text-xs text-atlas-text-secondary">
            Absolute return contribution and unhedged international multi-currency impact.
          </p>

          <div className="mt-3 space-y-2 rounded bg-atlas-surface-2 p-3 font-mono text-xs">
            <div>
              <span className="text-atlas-text-muted">Security Return Contribution:</span>
              <div className="text-atlas-accent font-semibold">C_j = w_P,j · R_P,j</div>
            </div>
            <div>
              <span className="text-atlas-text-muted">Currency Three-Way Decomposition:</span>
              <div className="text-atlas-accent font-semibold">R_base = R_local + R_FX + (R_local · R_FX)</div>
            </div>
            <div className="border-t border-atlas-border-default/40 pt-1">
              <span className="text-atlas-text-muted">Reconciliation Identity:</span>
              <div className="text-emerald-400 font-bold">Σ C_j ≡ R_P (Exact Reconciled)</div>
            </div>
          </div>
        </div>
      </div>

      {/* Disclosures Footer */}
      <div className="rounded border border-amber-500/30 bg-amber-500/5 p-4 text-xs text-amber-300">
        <div className="flex items-center gap-2 font-semibold">
          <ShieldAlert className="h-4 w-4 text-amber-400" />
          <span>Institutional Reporting Disclosures</span>
        </div>
        <p className="mt-1 text-[11px] text-atlas-text-secondary leading-relaxed">
          Attribution calculations are analytical decompositions of historical observed performance and do not represent predictive guarantees
          or investment advice. Cash balances without benchmark counterparts are treated as an off-benchmark allocation category with zero benchmark weight.
        </p>
      </div>
    </div>
  );
}

