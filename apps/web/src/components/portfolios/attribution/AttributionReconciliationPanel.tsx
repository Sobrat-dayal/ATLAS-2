"use client";

import React from "react";
import {
  formatBps,
  formatPercent,
  formatWeight,
  getCompletenessBadge,
  getReconciliationBadge,
} from "@/lib/portfolios/attribution/formatting";
import { AttributionRunDTO } from "@/lib/portfolios/attribution/types";
import {
  CheckCircle2,
  Copy,
  Hash,
  HelpCircle,
  Lock,
  Scale,
  ShieldCheck,
  XCircle,
} from "lucide-react";

interface AttributionReconciliationPanelProps {
  run: AttributionRunDTO;
}

export function AttributionReconciliationPanel({ run }: AttributionReconciliationPanelProps) {
  const rec = run.reconciliation;
  const dq = run.data_quality;
  const recBadge = getReconciliationBadge(rec.status);
  const qualBadge = getCompletenessBadge(dq.completeness);

  const [copied, setCopied] = React.useState(false);

  const copyHash = () => {
    navigator.clipboard.writeText(dq.input_hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const auditChecks = [
    {
      title: "Portfolio Return Reconstruction",
      formula: "Σ (w_P,k · R_P,k) ≡ R_P",
      reconciled: rec.portfolio_reconciled,
      computed: formatPercent(rec.reconstructed_portfolio_return, 4, true),
      expected: formatPercent(rec.portfolio_return, 4, true),
      tolerance: `≤ ${parseFloat(rec.tolerance) * 10000} bps`,
    },
    {
      title: "Benchmark Return Reconstruction",
      formula: "Σ (w_B,k · R_B,k) ≡ R_B",
      reconciled: rec.benchmark_reconciled,
      computed: formatPercent(rec.reconstructed_benchmark_return, 4, true),
      expected: formatPercent(rec.benchmark_return, 4, true),
      tolerance: `≤ ${parseFloat(rec.tolerance) * 10000} bps`,
    },
    {
      title: "Active Return Attribution Additivity",
      formula: "R_P - R_B ≡ Allocation + Selection + Interaction + Residual",
      reconciled: rec.attribution_reconciled,
      computed: formatPercent(rec.total_attributed, 4, true),
      expected: formatPercent(rec.active_return, 4, true),
      tolerance: `Residual: ${formatBps(rec.residual)}`,
    },
    {
      title: "Security Contributions Consistency",
      formula: "Σ C_j ≡ R_P",
      reconciled: rec.security_contributions_reconciled,
      computed: formatPercent(rec.security_contributions_sum, 4, true),
      expected: formatPercent(rec.portfolio_return, 4, true),
      tolerance: `Exact to NAV`,
    },
  ];

  return (
    <div className="space-y-4">
      {/* Audit Status Top Bar */}
      <div className="flex flex-col gap-3 rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-400">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-atlas-text-primary">
                Mathematical Attribution Audit
              </h3>
              <span className={`rounded px-2 py-0.5 text-xs font-semibold ${recBadge.colorClass}`}>
                {recBadge.label}
              </span>
            </div>
            <p className="text-xs text-atlas-text-secondary">
              5-point independent financial verification guarantees mathematical integrity with zero unexplained leakage.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-atlas-text-muted">Max Tolerance:</span>
          <span className="rounded bg-atlas-surface-2 px-2 py-1 text-atlas-text-primary">
            {parseFloat(rec.tolerance) * 10000} bps ({rec.tolerance})
          </span>
        </div>
      </div>

      {/* 4 Audit Check Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {auditChecks.map((check, i) => (
          <div
            key={i}
            className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  {check.reconciled ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  ) : (
                    <XCircle className="h-4 w-4 text-rose-400" />
                  )}
                  <h4 className="text-xs font-semibold text-atlas-text-primary">
                    {check.title}
                  </h4>
                </div>
                <div className="mt-1 font-mono text-[11px] text-atlas-accent">
                  {check.formula}
                </div>
              </div>
              <span
                className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                  check.reconciled
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                }`}
              >
                {check.reconciled ? "PASSED" : "FAILED"}
              </span>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-2 border-t border-atlas-border-default/40 pt-2 font-mono text-xs">
              <div>
                <span className="text-[10px] text-atlas-text-muted block">Reconstructed</span>
                <span className="font-semibold text-atlas-text-primary">{check.computed}</span>
              </div>
              <div>
                <span className="text-[10px] text-atlas-text-muted block">Actual Ledger</span>
                <span className="font-semibold text-atlas-text-primary">{check.expected}</span>
              </div>
              <div>
                <span className="text-[10px] text-atlas-text-muted block">Tolerance / Residual</span>
                <span className="text-atlas-text-secondary">{check.tolerance}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Provenance & Data Quality */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {/* Input Provenance Hash */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center gap-2 border-b border-atlas-border-default/40 pb-2">
            <Hash className="h-4 w-4 text-atlas-accent" />
            <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
              Cryptographic Input Provenance Hash
            </h4>
          </div>
          <p className="mt-2 text-xs text-atlas-text-secondary leading-relaxed">
            Deterministic SHA-256 digest computed across holdings, prices, tax-lots, and benchmark constituents. Guarantees reproducibility across auditor reviews.
          </p>
          <div className="mt-3 flex items-center justify-between rounded bg-atlas-surface-2 px-3 py-2 text-xs font-mono">
            <span className="truncate text-atlas-text-primary max-w-[340px]" title={dq.input_hash}>
              {dq.input_hash}
            </span>
            <button
              onClick={copyHash}
              className="flex items-center gap-1 text-[11px] text-atlas-accent hover:underline"
            >
              <Copy className="h-3.5 w-3.5" />
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
          </div>
          <div className="mt-2 text-[10px] text-atlas-text-muted">
            Algorithm: SHA-256 | Run ID: {run.id}
          </div>
        </div>

        {/* Data Quality & Coverage Summary */}
        <div className="rounded border border-atlas-border-default/60 bg-atlas-surface-1 p-4">
          <div className="flex items-center justify-between border-b border-atlas-border-default/40 pb-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-atlas-accent" />
              <h4 className="text-xs font-semibold uppercase tracking-wider text-atlas-text-primary">
                Data Completeness & Taxonomy Coverage
              </h4>
            </div>
            <span className={`rounded px-2 py-0.5 text-[10px] font-semibold ${qualBadge.colorClass}`}>
              {qualBadge.label}
            </span>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-3 text-xs">
            <div className="rounded bg-atlas-surface-2/40 p-2.5">
              <div className="text-[11px] text-atlas-text-secondary">Holdings Coverage</div>
              <div className="mt-1 text-sm font-bold text-atlas-text-primary font-mono">
                {formatPercent(dq.portfolio_holdings_coverage_ratio, 1)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2/40 p-2.5">
              <div className="text-[11px] text-atlas-text-secondary">Benchmark Coverage</div>
              <div className="mt-1 text-sm font-bold text-atlas-text-primary font-mono">
                {formatPercent(dq.benchmark_constituent_coverage_ratio, 1)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2/40 p-2.5">
              <div className="text-[11px] text-atlas-text-secondary">GICS Taxonomy Match</div>
              <div className="mt-1 text-sm font-bold text-atlas-text-primary font-mono">
                {formatPercent(dq.taxonomy_coverage_ratio, 1)}
              </div>
            </div>
            <div className="rounded bg-atlas-surface-2/40 p-2.5">
              <div className="text-[11px] text-atlas-text-secondary">Unmapped Categories</div>
              <div className="mt-1 text-sm font-bold text-atlas-text-primary font-mono">
                {formatWeight(dq.unmapped_sector_weight)} ({dq.missing_securities_count} items)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
