"use client";

import React, { useState } from "react";
import { BookOpen, ChevronDown, ChevronRight, HelpCircle, Scale, ShieldCheck } from "lucide-react";

export function OptimizationMethodologyInspector() {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  return (
    <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between p-4 text-left transition-colors hover:bg-atlas-surface-2/40"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-atlas-accent" />
          <span className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
            Optimization Mathematical Methodologies & Disclosures
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-atlas-text-muted">
          <span>{isOpen ? "Collapse Documentation" : "Expand Mathematical Formulations"}</span>
          {isOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </div>
      </button>

      {isOpen && (
        <div className="border-t border-atlas-border-default/60 p-5 space-y-6 text-xs text-atlas-text-secondary leading-relaxed">
          {/* Section 1: Modern Portfolio Theory */}
          <div className="space-y-2">
            <h4 className="font-bold text-atlas-text-primary text-sm">
              1. Mean-Variance Quadratic Utility Formulation (Markowitz, 1952)
            </h4>
            <p>
              ATLAS solves the constrained quadratic utility maximization problem balancing expected portfolio return against portfolio variance scaled by investor risk aversion $\lambda$:
            </p>
            <div className="rounded bg-atlas-surface-2/60 p-3 font-mono text-[11px] text-cyan-300">
              min_w &nbsp; 0.5 * w^T Σ w - λ * w^T μ &nbsp;&nbsp; subject to &nbsp;&nbsp; Σ w_i = 1, &nbsp; w_i ≥ 0
            </div>
            <p className="text-[11px] text-atlas-text-muted">
              Analytical Jacobian: ∇f(w) = Σ w - λ μ. Solved via Sequential Least Squares Quadratic Programming (SLSQP).
            </p>
          </div>

          {/* Section 2: Equal Risk Contribution (Risk Parity) */}
          <div className="space-y-2">
            <h4 className="font-bold text-atlas-text-primary text-sm">
              2. Risk Parity via Spinu Convex Logarithmic Formulation (2013)
            </h4>
            <p>
              Traditional risk parity enforces identical total risk contributions across all assets: RC_i = w_i (&Sigma; w)_i = (1/N) &sigma;_p^2. Because direct risk budgeting is non-convex, ATLAS implements Florin Spinu&apos;s strictly convex logarithmic barrier formulation:
            </p>
            <div className="rounded bg-atlas-surface-2/60 p-3 font-mono text-[11px] text-cyan-300">
              min_y &nbsp; 0.5 * y^T Σ y - c * Σ ln(y_i) &nbsp;&nbsp; (y_i &gt; 0) &nbsp;&nbsp; =&gt; &nbsp;&nbsp; w_i* = y_i* / Σ y_j*
            </div>
            <p className="text-[11px] text-atlas-text-muted">
              Gradient: ∇f(y) = Σ y - c / y. Solved unconstrained via L-BFGS-B, guaranteeing unique global convergence and analytical risk parity.
            </p>
          </div>

          {/* Section 3: Ledoit-Wolf Covariance Shrinkage */}
          <div className="space-y-2">
            <h4 className="font-bold text-atlas-text-primary text-sm">
              3. Well-Conditioned Covariance Estimation (Ledoit & Wolf, 2004)
            </h4>
            <p>
              Sample covariance estimators in high dimensions suffer from out-of-sample noise and eigenvalue dispersion. ATLAS applies Ledoit-Wolf shrinkage towards a structured constant-correlation diagonal target $F$:
            </p>
            <div className="rounded bg-atlas-surface-2/60 p-3 font-mono text-[11px] text-cyan-300">
              Σ_LW = δ * F + (1 - δ) * S, &nbsp;&nbsp; where δ ∈ [0, 1] is asymptotically optimal shrinkage intensity
            </div>
            <p className="text-[11px] text-atlas-text-muted">
              Every covariance matrix is checked for positive semi-definiteness (&lambda;<sub>min</sub> &ge; 10<sup>-7</sup>) and condition number stability.
            </p>
          </div>

          {/* Section 4: Turnover & Rebalancing Friction */}
          <div className="space-y-2">
            <h4 className="font-bold text-atlas-text-primary text-sm">
              4. Rebalancing Turnover and Friction Modeling
            </h4>
            <p>
              One-way portfolio turnover measures the fraction of portfolio value traded between current holdings w_curr and candidate weights w_cand:
            </p>
            <div className="rounded bg-atlas-surface-2/60 p-3 font-mono text-[11px] text-cyan-300">
              Turnover = 0.5 * Σ |w_i,cand - w_i,curr| &nbsp;&nbsp; | &nbsp;&nbsp; Est. Cost = rate * Σ |Δw_i| * NAV
            </div>
          </div>

          {/* Institutional Compliance Notice */}
          <div className="rounded border border-atlas-border-default/80 bg-atlas-surface-2/40 p-3 text-[11px] text-atlas-text-muted">
            <div className="flex items-center gap-1.5 font-semibold text-atlas-text-primary mb-1">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Institutional Research & Compliance Disclosures</span>
            </div>
            Optimized portfolios are generated for quantitative modeling and strategic asset allocation analysis. The engine does not execute live trades, nor does it guarantee future returns. Calculations assume deterministic inputs under the specified covariance and expected-return estimation paradigms.
          </div>
        </div>
      )}
    </div>
  );
}
